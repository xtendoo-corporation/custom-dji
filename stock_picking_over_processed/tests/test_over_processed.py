from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestOverProcessed(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Cliente"})
        cls.product = cls.env["product.product"].create(
            {"name": "Producto sobreprocesado", "is_storable": True, "list_price": 10.0}
        )
        warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, warehouse.lot_stock_id, 50
        )

    def _delivery(self, qty=5):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [(0, 0, {"product_id": self.product.id, "product_uom_qty": qty})],
            }
        )
        if "route_ids" in order._fields and self.env["ir.module.module"].search_count(
            [("name", "=", "sale_order_required_route"), ("state", "=", "installed")]
        ):
            order.route_ids = self.env["stock.route"].create(
                {"name": "Ruta", "sale_selectable": True}
            )
        order.action_confirm()
        return order, order.picking_ids

    def test_no_overprocessing_by_default(self):
        _order, picking = self._delivery()
        self.assertFalse(picking.has_overprocessed_moves)

    def test_update_sale_order_with_processed_quantity(self):
        order, picking = self._delivery(5)
        move = picking.move_ids
        move.quantity = 8
        move.picked = True
        picking.invalidate_recordset()
        self.assertTrue(picking.has_overprocessed_moves)
        picking.action_update_sale_order()
        self.assertAlmostEqual(order.order_line.product_uom_qty, 8.0)
        self.assertAlmostEqual(move.product_uom_qty, 8.0)
        picking.invalidate_recordset()
        self.assertFalse(picking.has_overprocessed_moves)

    def test_exact_quantity_changes_nothing(self):
        order, picking = self._delivery(5)
        picking.action_update_sale_order()
        self.assertAlmostEqual(order.order_line.product_uom_qty, 5.0)
        self.assertAlmostEqual(picking.move_ids.product_uom_qty, 5.0)

    def test_button_in_picking_form(self):
        arch = self.env["stock.picking"].get_view(view_type="form")["arch"]
        self.assertIn("action_update_sale_order", arch)
