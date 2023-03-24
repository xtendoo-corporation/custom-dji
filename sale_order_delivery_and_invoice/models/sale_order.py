# -- coding: utf-8 --
import datetime

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def delivery_and_invoice(self):
        for picking in self.picking_ids:
            for line in picking.move_lines.filtered(
                    lambda m: m.state not in ["done", "cancel"]
            ):
                line.quantity_done = line.product_uom_qty
                picking.with_context(skip_overprocessed_check=True).button_validate()

        invoices = self._create_invoices()
        for invoice in invoices:
            invoice.action_post()
            print("-"*120)
            print("VALIDACION DE LA FACTURA REALIZADA")
            print("-"*120)
