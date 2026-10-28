from odoo import _, fields, models
from odoo.tools.float_utils import float_round


class StockPicking(models.Model):
    _inherit = "stock.picking"

    move_product_qty = fields.Float(
        string="Pending Delivery",
        compute="_compute_move_product_qty",
    )

    def _pending_delivery_domain(self, products):
        return [
            ("product_id", "in", products.ids),
            ("state", "not in", ["done", "cancel"]),
            ("picking_type_id.code", "=", "outgoing"),
        ]

    def _compute_move_product_qty(self):
        """Unidades pendientes de entregar de los productos del albarán."""
        pending_by_product = {
            product.id: quantity
            for product, quantity in self.env["stock.move"]._read_group(
                self._pending_delivery_domain(self.move_ids.product_id),
                ["product_id"],
                ["product_qty:sum"],
            )
        }
        for picking in self:
            total = sum(
                pending_by_product.get(product.id, 0.0)
                for product in picking.move_ids.product_id
            )
            picking.move_product_qty = float_round(total, precision_digits=3)

    def action_picking_template_sale_list(self):
        self.ensure_one()
        return {
            "name": _("Pending Delivery"),
            "type": "ir.actions.act_window",
            "res_model": "stock.move",
            "view_mode": "list,form",
            "views": [
                (
                    self.env.ref(
                        "product_form_move_waiting_purchase_link.view_move_list_pending_delivery"
                    ).id,
                    "list",
                ),
                (False, "form"),
            ],
            "domain": self._pending_delivery_domain(self.move_ids.product_id),
        }
