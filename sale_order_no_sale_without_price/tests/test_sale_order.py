from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNoSaleWithoutPrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "service"}
        )

    def _order(self, price):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "price_unit": price})
                ],
            }
        )

    def test_confirm_with_zero_price_raises(self):
        order = self._order(0.0)
        with self.assertRaises(ValidationError):
            order.action_confirm()

    def test_confirm_with_price_succeeds(self):
        order = self._order(5.0)
        order.action_confirm()
        self.assertEqual(order.state, "sale")

    def test_section_line_without_product_is_allowed(self):
        order = self._order(5.0)
        order.order_line = [
            (0, 0, {"display_type": "line_section", "name": "Section"})
        ]
        order.action_confirm()
        self.assertEqual(order.state, "sale")
