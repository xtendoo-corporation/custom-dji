from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReturnLotQty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock = cls.warehouse.lot_stock_id
        cls.customer = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "Producto lote", "is_storable": True, "tracking": "lot"}
        )
        cls.lot = cls.env["stock.lot"].create({"name": "L-001", "product_id": cls.product.id})
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.stock, 10, lot_id=cls.lot)

    def _delivery(self, qty=4):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "location_id": self.stock.id,
                "location_dest_id": self.customer.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
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
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        return picking

    def _return_wizard(self, picking):
        return (
            self.env["stock.return.picking"]
            .with_context(active_id=picking.id, active_model="stock.picking")
            .create({})
        )

    def test_wizard_proposes_lot_and_pending_quantity(self):
        picking = self._delivery()
        wizard = self._return_wizard(picking)
        line = wizard.product_return_moves
        self.assertEqual(line.lot_id, self.lot)
        self.assertEqual(line.quantity, 4)

    def test_return_reserves_original_lot(self):
        picking = self._delivery()
        wizard = self._return_wizard(picking)
        wizard.product_return_moves.quantity = 3
        return_picking = wizard._create_return()
        move_line = return_picking.move_ids.move_line_ids
        self.assertEqual(move_line.lot_id, self.lot)
        self.assertEqual(move_line.quantity, 3)
        self.assertEqual(move_line.return_lot_ids, self.lot)
        # tras devolver 3, solo quedan 1 pendientes de devolver
        return_picking.move_ids.picked = True
        return_picking.button_validate()
        self.assertEqual(self._return_wizard(picking).product_return_moves.quantity, 1)

    def test_return_lot_ids_without_return(self):
        picking = self._delivery()
        self.assertEqual(picking.move_ids.move_line_ids.return_lot_ids, self.lot)
        other_lot = self.env["stock.lot"].create({"name": "L-002", "product_id": self.product.id})
        line = self.env["stock.move.line"].new({"product_id": self.product.id})
        self.assertEqual(line.return_lot_ids._origin, self.lot | other_lot)
