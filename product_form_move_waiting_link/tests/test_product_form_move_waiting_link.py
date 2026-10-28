from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestProductFormMoveWaitingLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Pendiente", "is_storable": True})
        cls.partner = cls.env["res.partner"].create({"name": "Cliente entrega"})

    def _delivery(self, warehouse, qty):
        picking_type = warehouse.out_type_id
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": picking_type.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": qty,
                            "location_id": picking_type.default_location_src_id.id,
                            "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        return picking

    def test_pending_delivery_quantity(self):
        warehouse = self.env["stock.warehouse"].search([("company_id", "=", self.env.company.id)], limit=1)
        self._delivery(warehouse, 5)
        self.product.invalidate_recordset()
        self.assertAlmostEqual(self.product.move_product_qty, 5.0)
        self.assertAlmostEqual(self.product.product_tmpl_id.move_product_qty, 5.0)

    def test_pending_quantity_counts_every_warehouse(self):
        warehouse = self.env["stock.warehouse"].search([("company_id", "=", self.env.company.id)], limit=1)
        second = self.env["stock.warehouse"].create({"name": "Segundo almacén", "code": "SEG"})
        self._delivery(warehouse, 5)
        self._delivery(second, 3)
        self.product.invalidate_recordset()
        action_domain = self.env["stock.move"].search_count(
            [
                ("state", "not in", ["done", "cancel"]),
                ("picking_type_id.code", "=", "outgoing"),
                ("product_id", "=", self.product.id),
            ]
        )
        self.assertEqual(action_domain, 2)
        self.assertAlmostEqual(self.product.move_product_qty, 8.0)

    def test_buttons_in_forms(self):
        for model in ("product.product", "product.template"):
            arch = self.env[model].get_view(view_type="form")["arch"]
            self.assertIn("move_product_qty", arch)
