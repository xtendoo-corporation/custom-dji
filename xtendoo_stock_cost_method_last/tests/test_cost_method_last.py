from odoo.tests import tagged

from odoo.addons.stock_account.tests.common import TestStockValuationCommon


@tagged("post_install", "-at_install")
class TestCostMethodLast(TestStockValuationCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_last = cls.env["product.category"].create(
            {
                "name": "Last",
                "property_valuation": "periodic",
                "property_cost_method": "last",
            }
        )
        cls.product_last = cls.product_fifo.copy(
            {"name": "Last price product", "categ_id": cls.category_last.id}
        )

    def test_cost_method_selection_includes_last(self):
        self.assertEqual(self.product_last.cost_method, "last")
        quant_selection = dict(
            self.env["stock.quant"]._fields["cost_method"].selection
        )
        self.assertIn("last", quant_selection)

    def test_standard_price_follows_last_receipt(self):
        self._make_in_move(self.product_last, 10, unit_cost=5.0)
        self.assertAlmostEqual(self.product_last.standard_price, 5.0)
        self._make_in_move(self.product_last, 10, unit_cost=8.0)
        self.assertAlmostEqual(self.product_last.standard_price, 8.0)
        self._make_in_move(self.product_last, 5, unit_cost=3.0)
        self.assertAlmostEqual(self.product_last.standard_price, 3.0)

    def test_outgoing_move_does_not_change_price(self):
        self._make_in_move(self.product_last, 10, unit_cost=5.0)
        self._make_out_move(self.product_last, 4)
        self.assertAlmostEqual(self.product_last.standard_price, 5.0)

    def test_other_methods_untouched(self):
        self._make_in_move(self.product_fifo, 10, unit_cost=5.0)
        self._make_in_move(self.product_fifo, 10, unit_cost=8.0)
        self.assertAlmostEqual(self.product_fifo.standard_price, 6.5)

    def test_moves_without_valued_quantity_are_skipped(self):
        move = self._make_in_move(self.product_last, 10, unit_cost=5.0)
        move.product_id.standard_price = 2.0
        move.quantity = 0.0
        move._update_standard_price_last()
        self.assertAlmostEqual(self.product_last.standard_price, 2.0)
