# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.depends('product_type', 'product_uom_qty', 'qty_delivered', 'state', 'move_ids', 'product_uom')
    def _compute_qty_to_deliver(self):
        super(SaleOrderLine, self)._compute_qty_to_deliver()
        """Compute the visibility of the inventory widget."""
        for line in self:
            if line.display_qty_widget:
                qty_total = 0.00
                for qty in line.move_ids.filtered(lambda i: i.state == 'done').mapped("quantity_done"): qty_total += qty
                if qty_total >= line.product_uom_qty:
                    line.display_qty_widget = False
