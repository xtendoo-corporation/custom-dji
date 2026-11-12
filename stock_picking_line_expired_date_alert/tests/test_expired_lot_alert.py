from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestExpiredLotAlert(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.customer = cls.env.ref("stock.stock_location_customers")
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Lot product",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
                "use_expiration_date": True,
            }
        )

    def _lot(self, name, days):
        return self.env["stock.lot"].create(
            {
                "name": name,
                "product_id": self.product.id,
                "expiration_date": datetime.now() + timedelta(days=days),
            }
        )

    def _picking(self, lot):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.stock, 5.0, lot_id=lot
        )
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": self.stock.id,
                "location_dest_id": self.customer.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 2.0,
                            "location_id": self.stock.id,
                            "location_dest_id": self.customer.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.picked = True
        return picking

    def test_expired_lot_blocks_validation(self):
        lot = self._lot("EXPIRED", -3)
        picking = self._picking(lot)
        self.assertTrue(picking.move_line_ids.is_expired)
        with self.assertRaisesRegex(UserError, "EXPIRED"):
            picking.button_validate()

    def test_valid_lot_can_be_validated(self):
        lot = self._lot("VALID", 30)
        picking = self._picking(lot)
        self.assertFalse(picking.move_line_ids.is_expired)
        picking.button_validate()
        self.assertEqual(picking.state, "done")

    def test_line_without_lot_is_not_expired(self):
        line = self.env["stock.move.line"].new({"product_id": self.product.id})
        self.assertFalse(line.is_expired)
