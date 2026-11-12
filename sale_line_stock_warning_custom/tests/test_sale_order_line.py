from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleLineStockWarning(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Customer"})
        cls.storable = cls.env["product.product"].create(
            {"name": "Storable", "type": "consu", "is_storable": True}
        )
        cls.service = cls.env["product.product"].create(
            {"name": "Service", "type": "service"}
        )

    def _order(self, product):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": product.id, "product_uom_qty": 2.0})
                ],
            }
        )

    def test_draft_storable_line_shows_widget(self):
        line = self._order(self.storable).order_line
        line._compute_qty_to_deliver()
        self.assertTrue(line.display_qty_widget)

    def test_service_line_hides_widget(self):
        line = self._order(self.service).order_line
        line._compute_qty_to_deliver()
        self.assertFalse(line.display_qty_widget)

    def test_confirmed_line_hides_widget(self):
        order = self._order(self.storable)
        order.action_confirm()
        order.order_line._compute_qty_to_deliver()
        self.assertFalse(order.order_line.display_qty_widget)
