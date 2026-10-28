from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged("post_install", "-at_install")
class TestSaleOrderRequiredRoute(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Cliente ruta"})
        cls.product = cls.env["product.product"].create(
            {"name": "Producto ruta", "type": "consu"}
        )
        cls.route = cls.env["stock.route"].create(
            {"name": "Ruta de prueba", "sale_selectable": True}
        )
        cls.salesman = new_test_user(
            cls.env,
            login="vendedor_ruta",
            groups="sales_team.group_sale_salesman,base.group_user",
        )

    def _order(self, **vals):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1})
                ],
                **vals,
            }
        )

    def test_confirm_without_route_fails(self):
        order = self._order()
        with self.assertRaises(ValidationError):
            order.action_confirm()
        self.assertEqual(order.state, "draft")

    def test_confirm_with_route(self):
        order = self._order(route_ids=[(6, 0, self.route.ids)])
        order.action_confirm()
        self.assertEqual(order.state, "sale")

    def test_salesman_sees_route_field_and_can_confirm(self):
        """Un vendedor sin el grupo de rutas push/pull ve el campo y puede
        completarlo, como en 13."""
        self.assertFalse(
            self.salesman.has_group("stock.group_adv_location"),
        )
        order = self._order(user_id=self.salesman.id).with_user(self.salesman)
        arch = order.get_view(view_type="form")["arch"]
        self.assertIn('name="route_ids"', arch)
        with self.assertRaises(ValidationError):
            order.action_confirm()
        order.route_ids = self.route
        order.action_confirm()
        self.assertEqual(order.state, "sale")
