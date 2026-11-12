from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReportSaleOrderAccumulate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.report = cls.env["report.document_format_dji.report_saleorder_line"]
        classification = cls.env["product.classification"]
        cls.first = classification.create({"name": "First", "sequence": 1})
        cls.second = classification.create({"name": "Second", "sequence": 5})
        cls.product_a = cls.env["product.product"].create(
            {"name": "Product A", "product_classification_id": cls.second.id}
        )
        cls.product_b = cls.env["product.product"].create(
            {"name": "Product B", "product_classification_id": cls.first.id}
        )
        partner = cls.env["res.partner"].create({"name": "Customer"})
        cls.orders = cls.env["sale.order"].create(
            [
                {
                    "partner_id": partner.id,
                    "order_line": [
                        (0, 0, {"product_id": cls.product_a.id, "product_uom_qty": 2}),
                        (0, 0, {"product_id": cls.product_b.id, "product_uom_qty": 1}),
                        (0, 0, {"display_type": "line_note", "name": "Note"}),
                    ],
                },
                {
                    "partner_id": partner.id,
                    "order_line": [
                        (0, 0, {"product_id": cls.product_a.id, "product_uom_qty": 3}),
                    ],
                },
            ]
        )

    def test_report_values_expose_line_getter(self):
        values = self.report._get_report_values(self.orders.ids)
        self.assertEqual(values["docids"], self.orders.ids)
        self.assertEqual(
            values["get_saleorder_lines"](self.orders.ids),
            self.report.get_saleorder_lines(self.orders.ids),
        )

    def test_lines_are_accumulated_and_sorted_by_classification(self):
        records = self.report.get_saleorder_lines(self.orders.ids)
        self.assertEqual(
            records,
            [
                {
                    "product_name": "Product B",
                    "product_classification_sequence": 1,
                    "product_classification_name": "First",
                    "product_qty": 1.0,
                },
                {
                    "product_name": "Product A",
                    "product_classification_sequence": 5,
                    "product_classification_name": "Second",
                    "product_qty": 5.0,
                },
            ],
        )

    def test_no_orders_returns_empty_list(self):
        self.assertEqual(self.report.get_saleorder_lines([]), [])
