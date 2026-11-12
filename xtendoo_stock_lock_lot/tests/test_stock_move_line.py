from odoo import exceptions

from odoo.addons.base.tests.common import BaseCommon


class TestStockMoveLine(BaseCommon):
    def setUp(cls):
        super().setUp()
        cls.category = cls.env["product.category"].create(
            {"name": "Test category", "lot_default_locked": True}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "categ_id": cls.category.id, "is_storable": True}
        )
        cls.location_src = cls.env["stock.location"].create({"name": "Source Location"})
        cls.location_dest = cls.env["stock.location"].create(
            {"name": "Destination Location", "allow_locked": False}
        )
        cls.lot = cls.env["stock.lot"].create(
            {
                "name": "Test lot",
                "product_id": cls.product.id,
                "company_id": cls.env.user.company_id.id,
                "locked": True,
            }
        )
        cls.move = cls.env["stock.move"].create(
            {
                "product_id": cls.product.id,
                "product_uom_qty": 10,
                "location_id": cls.location_src.id,
                "location_dest_id": cls.location_dest.id,
            }
        )

        cls.move_line = cls.env["stock.move.line"].create(
            {
                "move_id": cls.move.id,
                "product_id": cls.product.id,
                "location_id": cls.location_src.id,
                "location_dest_id": cls.location_dest.id,
                "lot_id": cls.lot.id,
            }
        )

    def test_action_done_with_locked_lot(self):
        with self.assertRaises(exceptions.ValidationError):
            self.move_line._action_done()

    def test_action_done_allowed_location(self):
        self.location_dest.allow_locked = True
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location_src, 10, lot_id=self.lot
        )
        self.move_line.quantity = 10
        self.move_line._action_done()
        self.assertEqual(
            self.env["stock.quant"]._get_available_quantity(
                self.product, self.location_dest, lot_id=self.lot, allow_negative=True
            ),
            10,
        )
