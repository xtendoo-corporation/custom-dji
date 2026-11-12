from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestNoPaginationLines(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Cliente sin paginacion"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Producto sin paginacion",
                "list_price": 10.0,
                "taxes_id": [(5, 0, 0)],
            }
        )

    def _create_order(self, quantity=1.0):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": quantity,
                        },
                    )
                ],
            }
        )

    def test_total_invoiced_is_zero_without_invoices(self):
        order = self._create_order()
        self.assertEqual(order.total_invoiced, 0.0)

    def test_total_invoiced_sums_invoice_amounts(self):
        order = self._create_order(quantity=2.0)
        order.action_confirm()
        invoices = order._create_invoices()
        self.assertEqual(
            order.total_invoiced,
            sum(invoices.mapped("amount_total_signed")),
        )
        self.assertAlmostEqual(order.total_invoiced, 20.0)

    def test_total_invoiced_computed_for_multiple_orders(self):
        first = self._create_order(quantity=1.0)
        second = self._create_order(quantity=3.0)
        for order in first | second:
            order.action_confirm()
            order._create_invoices()
        self.assertAlmostEqual(first.total_invoiced, 10.0)
        self.assertAlmostEqual(second.total_invoiced, 30.0)
