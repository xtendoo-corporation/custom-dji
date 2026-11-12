import datetime
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

FIXED_TODAY = datetime.datetime(2026, 1, 10, 8, 0, 0)


@tagged("post_install", "-at_install")
class TestDjiNoDateExpired(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Producto caducidad",
                "is_storable": True,
                "tracking": "lot",
                "use_expiration_date": True,
                "expiration_time": 30,
            }
        )
        cls.lot = cls.env["stock.lot"].create(
            {"name": "LOTE-DJI-1", "product_id": cls.product.id}
        )

    def _generate_vals(self, product, mode="generate", count=2):
        context = {
            "default_product_id": product.id,
            "default_picking_id": False,
            "default_tracking": "lot",
            "default_quantity": count,
            "default_location_dest_id": self.env.ref("stock.stock_location_stock").id,
        }
        with patch.object(fields.Datetime, "today", return_value=FIXED_TODAY):
            return self.env["stock.move"].action_generate_lot_line_vals(
                context, mode, "A", count, ""
            )

    def test_lot_keeps_user_expiration_date(self):
        expiration = FIXED_TODAY + datetime.timedelta(days=10)
        self.lot.expiration_date = expiration
        self.lot._compute_expiration_date()
        self.assertEqual(self.lot.expiration_date, expiration)

    def test_lot_without_user_expiration_date_stays_empty(self):
        lot = self.env["stock.lot"].create(
            {"name": "LOTE-DJI-2", "product_id": self.product.id}
        )
        lot._compute_expiration_date()
        self.assertFalse(lot.expiration_date)

    def test_lot_dates_other_than_expiration_are_cleared(self):
        self.lot._compute_dates()
        self.assertFalse(self.lot.use_date)
        self.assertFalse(self.lot.removal_date)
        self.assertFalse(self.lot.alert_date)

    def test_move_line_with_lot_shows_lot_expiration(self):
        expiration = FIXED_TODAY + datetime.timedelta(days=5)
        self.lot.expiration_date = expiration
        line = self.env["stock.move.line"].new({"lot_id": self.lot.id})
        line._compute_expiration_date()
        self.assertEqual(line.expiration_date, expiration)

    def test_move_line_without_lot_keeps_user_date(self):
        expiration = FIXED_TODAY + datetime.timedelta(days=3)
        line = self.env["stock.move.line"].new({"expiration_date": expiration})
        line._compute_expiration_date()
        self.assertEqual(line.expiration_date, expiration)

    def test_move_line_without_lot_and_date_stays_empty(self):
        line = self.env["stock.move.line"].new({})
        line._compute_expiration_date()
        self.assertFalse(line.expiration_date)

    def test_move_line_removal_date_is_cleared(self):
        line = self.env["stock.move.line"].new({})
        line._compute_removal_date()
        self.assertFalse(line.removal_date)

    def test_action_open_lot_returns_lot_form(self):
        line = self.env["stock.move.line"].new({"lot_id": self.lot.id})
        action = line.action_open_lot()
        self.assertEqual(action["res_model"], "stock.lot")
        self.assertEqual(action["res_id"], self.lot.id)
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")

    def test_action_open_lot_rejects_multiple_records(self):
        lines = self.env["stock.move.line"].new({})
        lines |= self.env["stock.move.line"].new({})
        with self.assertRaises(ValueError):
            lines.action_open_lot()

    def test_generate_lot_vals_removes_default_expiration(self):
        vals_list = self._generate_vals(self.product)
        self.assertEqual(len(vals_list), 1)
        for vals in vals_list:
            self.assertFalse(vals["expiration_date"])

    def test_generate_lot_vals_without_expiration_product_is_untouched(self):
        product = self.env["product.product"].create(
            {
                "name": "Producto sin caducidad",
                "is_storable": True,
                "tracking": "lot",
                "use_expiration_date": False,
            }
        )
        vals_list = self._generate_vals(product)
        self.assertEqual(len(vals_list), 1)
        for vals in vals_list:
            self.assertNotIn("expiration_date", vals)

    def test_generate_lot_vals_rejects_missing_product(self):
        with self.assertRaises(UserError):
            self.env["stock.move"].action_generate_lot_line_vals(
                {}, "generate", "A", 1, ""
            )

    def test_generate_serial_commands_clear_expiration(self):
        move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 2,
                "product_uom": self.product.uom_id.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        field_data = [
            {"lot_name": "SER-1", "quantity": 1},
            {"lot_name": "SER-2", "quantity": 1},
        ]
        commands = move._generate_serial_move_line_commands(field_data)
        self.assertTrue(commands)
        for command in commands:
            self.assertFalse(command[2]["expiration_date"])
