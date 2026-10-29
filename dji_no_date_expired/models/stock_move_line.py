from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _compute_expiration_date(self):
        # Con lote, la linea muestra la caducidad del lote (el core ya lo
        # hace). Sin lote (recepcion) solo se conserva lo que escriba el
        # usuario, sin el valor por defecto "hoy + vida util" del core.
        for line in self:
            lot = line.quant_id.lot_id or line.lot_id
            if lot:
                line.expiration_date = lot.expiration_date
            else:
                line.expiration_date = line.expiration_date or False

    def _compute_removal_date(self):
        super()._compute_removal_date()
        self.removal_date = False

    def action_open_lot(self):
        """Abrir la ficha del lote desde los detalles de la operacion.

        En v19 la lista de detalles no deja abrir el lote (y cuando el
        albaran esta validado lo muestra como texto), asi que no habia forma
        de corregir la caducidad u otros datos desde la recepcion.
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.lot",
            "res_id": self.lot_id.id,
            "view_mode": "form",
            "target": "new",
        }
