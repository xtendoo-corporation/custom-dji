# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.tools import is_html_empty
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import copy

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order Inherit'

    @api.model
    def _merge_notes(self, orders):
        """Une el campo "Términos y condiciones" (note) de todos los pedidos,
        en el orden dado: una nota por párrafo y sin repetir las idénticas."""
        parts = []
        for order in orders:
            if is_html_empty(order.note):
                continue
            note = str(order.note).strip()
            if not note.lower().startswith(('<p', '<div', '<ul', '<ol', '<h', '<table', '<blockquote')):
                note = '<p>%s</p>' % note
            if note not in parts:
                parts.append(note)
        return Markup('').join(Markup(part) for part in parts)

    def _merge_orders(self, sales, merge_type, target=None, partner=None, customer_ref='', origin=''):
        """Fusiona los presupuestos `sales` y devuelve el pedido resultante.

        merge_type: 'new' (pedido nuevo y cancelar), 'exist' (nuevo y borrar),
        'exist_1' (sobre `target` y cancelar), 'exist_2' (sobre `target` y borrar).
        Las líneas se copian completas (descuento, unidad, secciones, notas,
        analítica...) con copy_data y conservan su orden: primero las del
        destino y después las de cada pedido, uno detrás de otro.
        """
        sale_obj = self.env['sale.order']
        line_obj = self.env['sale.order.line']
        if merge_type in ('new', 'exist'):
            base = sales[0]
            if partner and partner != base.partner_id:
                vals = {'partner_id': partner.id}
            else:
                vals = base.copy_data()[0]
                vals.pop('order_line', None)
            vals.update({
                'client_order_ref': customer_ref,
                'origin': origin,
                'state': 'draft',
                'note': self._merge_notes(sales),
            })
            target = sale_obj.create(vals)
            sources = sales
        else:
            vals = {'origin': origin}
            if customer_ref:
                vals['client_order_ref'] = customer_ref
            notes = self._merge_notes(target | (sales - target))
            if notes:
                vals['note'] = notes
            target.write(vals)
            sources = sales - target

        sequence = max(target.order_line.mapped('sequence') or [0])
        new_lines = []
        for sale in sources:
            for line in sale.order_line.sorted(lambda l: (l.sequence, l.id)):
                sequence += 10
                if merge_type == 'exist_2':
                    line.write({'order_id': target.id, 'sequence': sequence})
                else:
                    new_lines.append(line.copy_data({'order_id': target.id, 'sequence': sequence})[0])
        if new_lines:
            line_obj.create(new_lines)

        target.message_post(body=Markup(_("This sale order has been created from: <b>%s</b>")) % origin)
        sources = sources.with_context(disable_cancel_warning=True)
        sources.action_cancel()
        if merge_type in ('exist', 'exist_2'):
            sources.unlink()
        return target

    @staticmethod
    def _merge_action(order):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': order.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
        }

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        res_config = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        if res_config.auto_merge_sale_orderlines:
            for rec in self:
                if rec.state == 'draft':
                    order_lines = self.auto_merge()
                    vals['order_line'] = [(6, 0, [i.id for i in set(order_lines)])]
                    res = super(SaleOrder, self).write(vals)
                else:
                    pass
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # Desde Odoo 17 el core siempre llama a create() con una lista
        # (creacion en lote). Con @api.model + create(self, vals) el "res"
        # de super().create() puede tener varios registros y res.state /
        # res.order_line explota con "Expected singleton" en creaciones
        # multiples (import CSV, integraciones). Se itera por cada pedido
        # creado en vez de asumir uno solo.
        res = super(SaleOrder, self).create(vals_list)
        res_config = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        if res_config.auto_merge_sale_orderlines:
            for order_rec in res:
                if order_rec.state == 'draft':
                    order_new_lines = []
                    for order in order_rec.order_line:
                        if order.product_id not in [i.product_id for i in order_new_lines]:
                            order_new_lines.append(order)
                        elif order.product_id in [i.product_id for i in order_new_lines]:
                            a = [order_new_lines.index(i) for i in order_new_lines if
                                 (i.product_id == order.product_id) and (i.price_unit == order.price_unit)]
                            if len(a) == 1:
                                order_new_lines[a[0]].product_uom_qty += order.product_uom_qty
                                order_new_lines[a[0]].tax_ids += order.tax_ids
                            else:
                                order_new_lines.append(order)

                    order_rec.order_line = [(6, 0, [i.id for i in set(order_new_lines)])]
        return res


    def action_confirm(self):
        res_config = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        if res_config.auto_merge_sale_orderlines:
            for rec in self:
                if rec.state == 'draft':
                    order_lines = self.auto_merge()
                    rec.order_line = [(6, 0, [i.id for i in set(order_lines)])]
            res = super(SaleOrder, self).action_confirm()
        else:
            res = super(SaleOrder, self).action_confirm()
        return res

    def action_quotation_send(self):
        res_config = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        if res_config.auto_merge_sale_orderlines:
            for rec in self:
                if rec.state == 'draft':
                    order_lines = self.auto_merge()
                    rec.order_line = [(6, 0, [i.id for i in set(order_lines)])]
            res = super(SaleOrder, self).action_quotation_send()
        else:
            res = super(SaleOrder, self).action_quotation_send()
        return res

    def auto_merge(self):
        order_new_lines = []
        for rec in self:
            if rec.state == 'draft':
                for order in rec.order_line:
                    if order.product_id not in [i.product_id for i in order_new_lines]:
                        order_new_lines.append(order)
                    elif order.product_id in [i.product_id for i in order_new_lines]:
                        a = [order_new_lines.index(i) for i in order_new_lines if
                             (i.product_id == order.product_id) and (i.price_unit == order.price_unit)]
                        if len(a) == 1:
                            order_new_lines[a[0]].product_uom_qty += order.product_uom_qty
                            order_new_lines[a[0]].tax_ids += order.tax_ids
                        else:
                            order_new_lines.append(order)
                return set(order_new_lines)