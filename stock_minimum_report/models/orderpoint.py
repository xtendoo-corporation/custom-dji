from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    qty_available = fields.Float(
        string="Quantity On Hand (all)",
        related="product_id.qty_available",
        digits="Product Unit",
    )
    under_minimum = fields.Boolean(
        string="Under Minimum",
        compute="_compute_under_minimum",
        help="True if the quantity available is under the minimum quantity.",
    )
    warehouse_name = fields.Char(related="warehouse_id.name")

    @api.depends("product_id", "product_min_qty")
    def _compute_under_minimum(self):
        for orderpoint in self:
            orderpoint.under_minimum = (
                orderpoint.qty_available - orderpoint.product_min_qty
            ) < 0
