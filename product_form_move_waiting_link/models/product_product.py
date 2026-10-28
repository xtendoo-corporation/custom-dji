from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    move_product_qty = fields.Float(
        compute="_compute_picking_waiting_product_qty", string="Pickings"
    )

    def _compute_picking_waiting_product_qty(self):
        domain = [
            ("state", "not in", ["done", "cancel"]),
            ("product_id", "in", self.ids),
            ("picking_type_id.code", "=", "outgoing"),
        ]

        order_lines = self.env["stock.move"]._read_group(
            domain, ["product_id"], ["product_uom_qty:sum"]
        )
        moved_data = {
            product.id: qty_sum for product, qty_sum in order_lines
        }

        self.move_product_qty = 0
        for product in self:
            if not product.id:
                product.move_product_qty = 0.0
                continue
            product.move_product_qty = float_round(
                moved_data.get(product.id, 0),
                precision_rounding=product.uom_id.rounding,
            )
