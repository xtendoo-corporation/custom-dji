# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('is_storable', 'product_uom_qty', 'qty_delivered', 'state', 'move_ids', 'product_uom_id')
    def _compute_qty_to_deliver(self):
        """Compute the visibility of the inventory widget."""
        super()._compute_qty_to_deliver()
        for line in self:
            line.display_qty_widget = bool(
                line.state in ("draft", "sent")
                and line.is_storable
                and line.product_uom_id
                and line.qty_to_deliver > 0
            )
