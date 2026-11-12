# Copyright Copyright 2021 Daniel Dominguez, Manuel Calero - https://xtendoo.es
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderDeliveryProducts(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "type": "consu", "is_storable": True}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 1000.00,
                        },
                    )
                ],
            }
        )

    def test_action_view_picking(self):
        self.order.action_confirm()
        action = self.order.action_view_picking()
        picking = self.order.picking_ids
        self.assertEqual(action["res_model"], "stock.picking")
        self.assertEqual(action["res_id"], picking.id)
        self.assertEqual(action["domain"], [("id", "in", picking.ids)])
        self.assertEqual(action["views"][0][1], "form")
        self.assertEqual(action["context"]["default_origin"], self.order.name)

    def test_action_view_picking_without_pending_pickings(self):
        self.assertIsNone(self.order.action_view_picking())
        self.order.action_confirm()
        self.order.picking_ids.action_cancel()
        self.assertIsNone(self.order.action_view_picking())
