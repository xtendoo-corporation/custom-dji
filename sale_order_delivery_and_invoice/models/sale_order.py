from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def delivery_and_invoice(self):
        for picking in self.picking_ids.filtered(
            lambda p: p.state not in ("done", "cancel")
        ):
            for move in picking.move_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            ):
                move.quantity = move.product_uom_qty
                move.picked = True
            picking.with_context(skip_overprocessed_check=True).button_validate()

        invoices = self._create_invoices()
        for invoice in invoices:
            invoice.action_post()
