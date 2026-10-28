from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestPendingDeliveryLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Producto pendiente", "is_storable": True}
        )
        cls.other = cls.env["product.product"].create(
            {"name": "Otro producto", "is_storable": True}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Cliente"})
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.second = cls.env["stock.warehouse"].create(
            {"name": "Segundo almacén", "code": "SG2"}
        )

    def _picking(self, picking_type, product, qty):
        src, dest = picking_type.default_location_src_id, picking_type.default_location_dest_id
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": picking_type.id,
                "location_id": src.id,
                "location_dest_id": dest.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "location_id": src.id,
                            "location_dest_id": dest.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    def test_receipt_shows_pending_deliveries_of_all_warehouses(self):
        self._picking(self.warehouse.out_type_id, self.product, 5)
        self._picking(self.second.out_type_id, self.product, 3)
        self._picking(self.warehouse.out_type_id, self.other, 7)
        receipt = self._picking(self.warehouse.in_type_id, self.product, 10)
        self.assertAlmostEqual(receipt.move_product_qty, 8.0)

    def test_done_and_cancelled_deliveries_do_not_count(self):
        delivery = self._picking(self.warehouse.out_type_id, self.product, 5)
        delivery.action_cancel()
        receipt = self._picking(self.warehouse.in_type_id, self.product, 10)
        self.assertAlmostEqual(receipt.move_product_qty, 0.0)

    def test_product_counted_once_with_several_moves_in_the_receipt(self):
        self._picking(self.warehouse.out_type_id, self.product, 5)
        receipt = self._picking(self.warehouse.in_type_id, self.product, 4)
        receipt.write(
            {
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 6,
                            "location_id": receipt.location_id.id,
                            "location_dest_id": receipt.location_dest_id.id,
                        },
                    )
                ]
            }
        )
        self.assertAlmostEqual(receipt.move_product_qty, 5.0)

    def test_action_lists_the_pending_moves(self):
        self._picking(self.warehouse.out_type_id, self.product, 5)
        self._picking(self.second.out_type_id, self.product, 3)
        receipt = self._picking(self.warehouse.in_type_id, self.product, 10)
        action = receipt.action_picking_template_sale_list()
        moves = self.env["stock.move"].search(action["domain"])
        self.assertEqual(len(moves), 2)
        self.assertEqual(sum(moves.mapped("product_uom_qty")), 8.0)

    def test_button_in_form_for_receipts_only(self):
        arch = self.env["stock.picking"].get_view(view_type="form")["arch"]
        self.assertIn("action_picking_template_sale_list", arch)
