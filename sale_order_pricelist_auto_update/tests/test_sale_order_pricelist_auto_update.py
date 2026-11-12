from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderPricelistAutoUpdate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Cliente tarifa"})
        cls.product = cls.env["product.product"].create(
            {"name": "Producto tarifa", "list_price": 10.0, "standard_price": 2.0}
        )
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Tarifa cliente"})
        cls.item = cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "compute_price": "fixed",
                "fixed_price": 10.0,
            }
        )

    def _order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "order_line": [(0, 0, {"product_id": self.product.id, "product_uom_qty": 1})],
            }
        )

    def test_flag_and_update_pricelist(self):
        order = self._order()
        line = order.order_line
        self.assertAlmostEqual(line.price_unit, 10.0)
        self.assertFalse(line.is_pricelist_change)
        self.assertFalse(order.is_price_list_change)
        with Form(order) as form:
            with form.order_line.edit(0) as order_line:
                order_line.price_unit = 12.0
        self.assertTrue(line.is_pricelist_change)
        self.assertTrue(order.is_price_list_change)
        order.action_update_in_pricelist()
        self.assertAlmostEqual(self.item.fixed_price, 12.0)
        self.assertFalse(order.is_price_list_change)

    def test_creates_item_when_missing(self):
        self.item.unlink()
        order = self._order()
        order.order_line.price_unit = 7.5
        order.action_update_in_pricelist()
        item = self.env["product.pricelist.item"].search(
            [
                ("pricelist_id", "=", self.pricelist.id),
                ("product_tmpl_id", "=", self.product.product_tmpl_id.id),
            ]
        )
        self.assertEqual(len(item), 1)
        self.assertAlmostEqual(item.fixed_price, 7.5)

    def test_confirm_blocked_below_cost(self):
        order = self._order()
        order.order_line.price_unit = 1.0
        with self.assertRaises(UserError):
            order.action_confirm()
        order.order_line.price_unit = 3.0
        if "route_ids" in order._fields:
            # con sale_order_required_route instalado hace falta una ruta
            order.route_ids = self.env["stock.route"].create(
                {"name": "Ruta tarifa", "sale_selectable": True}
            )
        order.action_confirm()
        self.assertEqual(order.state, "sale")

    def test_price_unit_is_valid_branches(self):
        order = self._order()
        line = order.order_line
        line.price_unit = 1.0
        self.assertIn("Producto tarifa", line.compute_price_unit_is_valid())
        line.price_unit = 0.0
        self.assertIsNone(line.compute_price_unit_is_valid())
        line.price_unit = 5.0
        self.assertIsNone(line.compute_price_unit_is_valid())
        note = self.env["sale.order.line"].create(
            {"order_id": order.id, "display_type": "line_note", "name": "Nota"}
        )
        self.assertIsNone(note.compute_price_unit_is_valid())
        self.assertFalse(note.is_pricelist_change)
        self.assertFalse(note._compute_is_pricelist_change_line(3.0))

    def test_pricelist_change_line(self):
        line = self._order().order_line
        self.assertTrue(line._compute_is_pricelist_change_line(12.0))
        self.assertFalse(line._compute_is_pricelist_change_line(10.0))

    def test_pricelist_change_errors_are_ignored(self):
        line = self._order().order_line
        with patch.object(
            type(line), "_get_display_price", side_effect=Exception("boom")
        ):
            line.price_unit = 15.0
            line.flush_recordset()
            self.assertFalse(line.is_pricelist_change)
            self.assertFalse(line._compute_is_pricelist_change_line(15.0))
