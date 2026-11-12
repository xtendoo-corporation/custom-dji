# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2015-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TestPurchaseDiscount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.supplier = cls.env["res.partner"].create(
            {"name": "Proveedor", "default_supplierinfo_discount": 15.0}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Producto", "is_storable": True}
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_qty": 2.0,
                            "price_unit": 10.0,
                            "discount": 50.0,
                            "tax_ids": [(6, 0, [])],
                        },
                    )
                ],
            }
        )
        cls.line = cls.purchase_order.order_line

    def test_supplierinfo_default_discount_from_partner(self):
        supplierinfo = self.env["product.supplierinfo"].create(
            {"partner_id": self.supplier.id, "product_tmpl_id": self.product.product_tmpl_id.id}
        )
        self.assertEqual(supplierinfo.discount, 15.0)

    def test_supplierinfo_explicit_discount_wins(self):
        supplierinfo = self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "discount": 5.0,
            }
        )
        self.assertEqual(supplierinfo.discount, 5.0)

    def test_discount_change_updates_pending_move(self):
        self.purchase_order.button_confirm()
        move = self.line.move_ids
        self.assertAlmostEqual(move.price_unit, 5.0)
        self.line.discount = 25.0
        self.assertAlmostEqual(move.price_unit, 7.5)

    def test_discount_change_on_draft_order_has_no_moves(self):
        self.line.discount = 10.0
        self.assertFalse(self.line.move_ids)
        self.assertAlmostEqual(self.line.price_subtotal, 18.0)

    def test_report_discount_column(self):
        self.env.flush_all()
        report = self.env["purchase.report"].search(
            [("order_id", "=", self.purchase_order.id)]
        )
        self.assertEqual(report.discount, 50.0)

    @mute_logger("odoo.sql_db")
    def test_line_discount_limit(self):
        with self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.line.discount = 150.0
                self.env.flush_all()
