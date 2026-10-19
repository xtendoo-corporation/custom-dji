from odoo import models


def _num(valor, decimales=2):
    """1234.5 → '1.234,50' (formato español)."""
    texto = f'{valor:,.{decimales}f}'
    return texto.replace(',', '#').replace('.', ',').replace('#', '.')


def _cantidad(valor):
    """1.0 → '1' · 2.5 → '2,5' · 0.125 → '0,125' (sin ceros de relleno)."""
    texto = f'{valor:.3f}'.rstrip('0').rstrip('.')
    return texto.replace('.', ',')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # ------------------------------------------------------------
    # Número de albarán: el del traslado de SALIDA (ALB/OUT/...).
    # En la entrega en dos pasos (PICK → ALB/OUT) se puede imprimir
    # desde el PICK; el cliente debe ver siempre el número del ALB/OUT,
    # que es el que luego va referenciado en la factura.
    # ------------------------------------------------------------
    def dji_albaran_salida(self):
        self.ensure_one()
        if self.picking_type_code == 'outgoing':
            return self
        destinos = self.move_ids.move_dest_ids.picking_id
        for _nivel in range(3):
            salida = destinos.filtered(lambda p: p.picking_type_code == 'outgoing' and p.state != 'cancel')
            if salida:
                return salida.sorted('id')[:1]
            destinos = destinos.move_ids.move_dest_ids.picking_id
            if not destinos:
                break
        if self.sale_id:
            salida = self.sale_id.picking_ids.filtered(
                lambda p: p.picking_type_code == 'outgoing' and p.state != 'cancel')
            if salida:
                return salida.sorted('id')[:1]
        return self

    def dji_albaran_numero(self):
        return self.dji_albaran_salida().name

    def dji_albaran_valorado(self):
        self.ensure_one()
        return bool(self.sale_id) and not self.partner_id.commercial_partner_id.dji_albaran_sin_precios

    def dji_albaran_datos(self):
        """Todo lo que pinta el albarán, ya calculado y formateado."""
        self.ensure_one()
        salida = self.dji_albaran_salida()
        pedido = self.sale_id or salida.sale_id
        cliente = (pedido.partner_invoice_id or self.partner_id).commercial_partner_id
        entrega = salida.partner_id or self.partner_id
        fecha = salida.date_done or salida.scheduled_date or self.date_done or self.scheduled_date
        valorado = self.dji_albaran_valorado()
        tiene_caducidad = 'expiration_date' in self.env['stock.lot']._fields

        lineas = []
        base = 0.0
        impuestos = {}  # etiqueta -> importe
        unidades = 0.0
        for move in self.move_ids.filtered(lambda m: m.state != 'cancel').sorted(lambda m: (m.sequence, m.id)):
            producto = move.product_id
            sale_line = move.sale_line_id
            partes = [(ml.lot_id, ml.lot_name, ml.quantity, ml.product_uom_id)
                      for ml in move.move_line_ids if ml.quantity]
            if not partes:
                qty = move.quantity or move.product_uom_qty
                if not qty:
                    continue
                partes = [(self.env['stock.lot'], False, qty, move.product_uom)]
            for lote, nombre_lote, qty, uom in partes:
                fila = {
                    'codigo': producto.default_code or '',
                    'nombre': producto.with_context(display_default_code=False).display_name,
                    'lote': lote.name or nombre_lote or '',
                    'caducidad': '',
                    'cantidad': _cantidad(qty),
                    'unidad': '' if uom == producto.uom_id else uom.name,
                    'precio': '', 'iva': '', 'importe': '',
                }
                unidades += qty
                if tiene_caducidad and lote and lote.expiration_date:
                    fila['caducidad'] = lote.expiration_date.strftime('%d/%m/%Y')
                if valorado and sale_line:
                    qty_venta = uom._compute_quantity(qty, sale_line.product_uom_id, round=False) \
                        if uom and sale_line.product_uom_id and uom != sale_line.product_uom_id else qty
                    neto = sale_line.price_unit * (1 - (sale_line.discount or 0.0) / 100.0)
                    importe = qty_venta * neto
                    base += importe
                    porcentajes = []
                    for tax in sale_line.tax_ids:
                        hijos = tax.children_tax_ids if tax.amount_type == 'group' else tax
                        for t in hijos:
                            if t.amount_type != 'percent':
                                continue
                            etiqueta = t.invoice_label or t.name
                            impuestos[etiqueta] = impuestos.get(etiqueta, 0.0) + importe * t.amount / 100.0
                            porcentajes.append(_cantidad(t.amount))
                    fila.update({
                        'precio': _num(neto),
                        'iva': ' + '.join(f'{p} %' for p in porcentajes),
                        'importe': _num(importe),
                    })
                lineas.append(fila)

        bancos = [
            {'banco': b.bank_id.name or '', 'cuenta': b.acc_number}
            for b in self.company_id.partner_id.bank_ids
        ]
        total_impuestos = sum(impuestos.values())
        return {
            'numero': salida.name,
            'fecha': fecha.strftime('%d/%m/%Y') if fecha else '',
            'pedido': pedido.name or self.origin or '',
            'comercial': pedido.user_id.name or '',
            'cliente': cliente,
            'entrega': entrega,
            'nota': salida.note or self.note,
            'valorado': valorado,
            'lineas': lineas,
            'resumen': f"{len(lineas)} {'línea' if len(lineas) == 1 else 'líneas'} · {_cantidad(unidades)} unidades",
            'base': _num(base),
            'impuestos': [{'etiqueta': k, 'importe': _num(v)} for k, v in impuestos.items()],
            'total': _num(base + total_impuestos),
            'bancos': bancos,
        }
