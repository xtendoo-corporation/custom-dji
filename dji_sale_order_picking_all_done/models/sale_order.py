# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_sale_order_confirm_and_delivery(self):
        self.action_confirm()
        if self.route_id.name =='Entrega directa al cliente':
            for picking in self.picking_ids:
                for line in picking.move_lines.filtered(
                    lambda m: m.state not in ["done", "cancel"]
                ):
                    line.quantity_done = line.product_uom_qty
                picking.with_context(skip_overprocessed_check=True).button_validate()
        else:
            for picking_pic in self.picking_ids.filtered(lambda r: 'PIC' in r.name):
                for line in picking_pic.move_lines.filtered(
                    lambda m: m.state not in ["done", "cancel"]
                ):
                    picking_lines = self.env["stock.move.line"].search([('move_id', '=', line.id)])
                    line.quantity_done = line.product_uom_qty
                picking_pic.with_context(skip_overprocessed_check=True).button_validate()

            for picking_pic in self.picking_ids.filtered(lambda r: 'ALB' in r.name):
                for line in picking_pic.move_lines.filtered(
                    lambda m: m.state not in ["done", "cancel"]
                ):
                    picking_lines = self.env["stock.move.line"].search([('move_id', '=', line.id)])
                    line.quantity_done = line.product_uom_qty
                picking_pic.with_context(skip_overprocessed_check=True).button_validate()


    def action_sale_order_confirm_and_invoice(self):
        self.action_sale_order_confirm_and_delivery()
        payment = self.env["sale.advance.payment.inv"].create({})
        payment.with_context(active_ids=self.ids).create_invoices()
