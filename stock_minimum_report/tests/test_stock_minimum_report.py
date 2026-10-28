from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockMinimumReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.second = cls.env["stock.warehouse"].create(
            {"name": "Segundo almacén", "code": "SG2"}
        )
        cls.low = cls.env["product.product"].create({"name": "Poco stock", "is_storable": True})
        cls.ok = cls.env["product.product"].create({"name": "Stock suficiente", "is_storable": True})
        cls.env["stock.quant"]._update_available_quantity(cls.low, cls.warehouse.lot_stock_id, 3)
        cls.env["stock.quant"]._update_available_quantity(cls.ok, cls.warehouse.lot_stock_id, 50)
        Orderpoint = cls.env["stock.warehouse.orderpoint"]
        cls.op_low = Orderpoint.create(
            {"product_id": cls.low.id, "warehouse_id": cls.warehouse.id,
             "location_id": cls.warehouse.lot_stock_id.id, "product_min_qty": 10, "product_max_qty": 20}
        )
        cls.op_ok = Orderpoint.create(
            {"product_id": cls.ok.id, "warehouse_id": cls.warehouse.id,
             "location_id": cls.warehouse.lot_stock_id.id, "product_min_qty": 10, "product_max_qty": 20}
        )
        cls.op_second = Orderpoint.create(
            {"product_id": cls.low.id, "warehouse_id": cls.second.id,
             "location_id": cls.second.lot_stock_id.id, "product_min_qty": 100, "product_max_qty": 200}
        )

    def _run(self, **vals):
        wizard = self.env["wizard.report.stock.minimum"].create(vals)
        action = wizard.run_wizard()
        return self.env["stock.warehouse.orderpoint"].search(action["domain"]), action

    def test_all_warehouses(self):
        found, action = self._run(warehouse_option="1")
        self.assertIn(self.op_low, found)
        self.assertIn(self.op_second, found)
        self.assertNotIn(self.op_ok, found)
        self.assertEqual(action["res_model"], "stock.warehouse.orderpoint")

    def test_specific_warehouse(self):
        found, _action = self._run(warehouse_option="2", warehouse_selected=self.warehouse.id)
        self.assertEqual(found & (self.op_low | self.op_ok | self.op_second), self.op_low)

    def test_report_follows_stock_changes(self):
        found, _action = self._run(warehouse_option="2", warehouse_selected=self.warehouse.id)
        self.assertIn(self.op_low, found)
        self.env["stock.quant"]._update_available_quantity(self.low, self.warehouse.lot_stock_id, 20)
        found, _action = self._run(warehouse_option="2", warehouse_selected=self.warehouse.id)
        self.assertNotIn(self.op_low, found)
        self.env["stock.quant"]._update_available_quantity(self.ok, self.warehouse.lot_stock_id, -45)
        found, _action = self._run(warehouse_option="2", warehouse_selected=self.warehouse.id)
        self.assertIn(self.op_ok, found)

    def test_wizard_form_requires_warehouse_when_specific(self):
        with Form(self.env["wizard.report.stock.minimum"]) as form:
            form.warehouse_option = "2"
            form.warehouse_selected = self.warehouse
        self.assertEqual(form.record.warehouse_selected, self.warehouse)

    def test_list_view_has_the_extra_columns(self):
        view = self.env.ref("stock_minimum_report.view_minimum_warehouse_orderpoint_tree")
        arch = self.env["stock.warehouse.orderpoint"].get_view(view.id, "list")["arch"]
        self.assertIn('name="qty_available"', arch)
        self.assertIn('name="warehouse_name"', arch)
