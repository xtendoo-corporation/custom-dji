from odoo import _, api, fields, models


class DJIUpdateCost(models.TransientModel):
    _name = "dji.update.cost"
    _description = "DJI Update Cost"

    @api.model
    def _dji_update_cost(self):
        products = self.env["product.template"].search([("standard_price", "=", 0)])
        for product in products:
            po = ( self.env["purchase.order"]
                    .sudo()
                    .search(
                    [
                        ("order_line.product_id", "=", product.id),
                    ],
                    limit=1,
                    order="date_order ASC",
                ) )
            if po:
                po_line = (
                    self.env["purchase.order.line"]
                    .sudo()
                    .search(
                    [
                        ("order_id", "=", po.id),
                        ("product_id", "=", product.id)
                    ],
                    limit=1,
                    order="id DESC",
                    )
                )
                if po_line:
                    product.standard_price = po_line.price_unit

    def product_update_cost(self):
        self.ensure_one()
        self._dji_update_cost()
