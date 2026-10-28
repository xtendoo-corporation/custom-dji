from odoo import fields
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
        cls.category_last_auto = cls.category_last.copy(
            {"name": "Last Auto", "property_valuation": "real_time"}
        )
        cls.product_last = cls.product_fifo.copy(
            {"name": "Producto último precio", "categ_id": cls.category_last.id}
        )
        cls.product_last_auto = cls.product_fifo.copy(
            {"name": "Producto último precio auto", "categ_id": cls.category_last_auto.id}
        )

    def test_cost_method_is_last(self):
        self.assertEqual(self.product_last.cost_method, "last")

    def test_standard_price_follows_last_receipt(self):
        self._make_in_move(self.product_last, 10, unit_cost=5.0)
        self.assertAlmostEqual(self.product_last.standard_price, 5.0)
        self._make_in_move(self.product_last, 10, unit_cost=8.0)
        self.assertAlmostEqual(self.product_last.standard_price, 8.0)
        self._make_in_move(self.product_last, 5, unit_cost=3.0)
        self.assertAlmostEqual(self.product_last.standard_price, 3.0)

    def test_delivery_valued_at_last_price(self):
        self._make_in_move(self.product_last, 10, unit_cost=5.0)
        self._make_in_move(self.product_last, 10, unit_cost=8.0)
        out = self._make_out_move(self.product_last, 4)
        self.assertAlmostEqual(abs(out.value), 32.0)

    def test_other_methods_untouched(self):
        self._make_in_move(self.product_fifo, 10, unit_cost=5.0)
        self._make_in_move(self.product_fifo, 10, unit_cost=8.0)
        self.assertAlmostEqual(self.product_fifo.standard_price, 6.5)
        self._make_out_move(self.product_fifo, 4)
        self.assertAlmostEqual(self.product_fifo.total_value, 110.0)

    def test_total_value_is_sum_of_moves(self):
        """Entradas 130 - salida 32 = 98, y no los 110 de una valoración FIFO."""
        self._make_in_move(self.product_last, 10, unit_cost=5.0)
        self._make_in_move(self.product_last, 10, unit_cost=8.0)
        self._make_out_move(self.product_last, 4)
        self.product_last.invalidate_recordset()
        self.assertAlmostEqual(self.product_last.total_value, 98.0)
        quants = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.product_last.id),
                ("location_id", "=", self.stock_location.id),
            ]
        )
        self.assertAlmostEqual(sum(quants.mapped("value")), 98.0)

    def test_total_value_matches_stock_account(self):
        """El saldo de la cuenta de valoración (facturas de compra y de venta)
        coincide con el valor total del producto."""
        product = self.product_last_auto
        self._make_in_move(product, 10, unit_cost=5.0)
        self._create_bill(product, 10, 5.0)
        self._make_in_move(product, 10, unit_cost=8.0)
        self._create_bill(product, 10, 8.0)
        self._make_out_move(product, 4)
        self._create_invoice(product, 4, 20.0)
        product.invalidate_recordset()
        account = product._get_product_accounts()["stock_valuation"]
        lines = self.env["account.move.line"].search(
            [("account_id", "=", account.id), ("product_id", "=", product.id)]
        )
        self.assertEqual(len(lines), 3)
        self.assertAlmostEqual(sum(lines.mapped("balance")), 98.0)
        self.assertAlmostEqual(product.total_value, 98.0)

    def test_total_value_at_date(self):
        self._make_in_move(self.product_last, 10, unit_cost=5.0)
        product = self.product_last.with_context(
            to_date=fields.Datetime.add(fields.Datetime.now(), hours=1)
        )
        self.assertAlmostEqual(product.total_value, 50.0)

    def _set_date(self, move, date):
        move.write({"date": date})
        move.move_line_ids.write({"date": date})

    def test_manual_price_update_is_the_new_base(self):
        now = fields.Datetime.now()
        move1 = self._make_in_move(self.product_last, 10, unit_cost=5.0)
        move2 = self._make_in_move(self.product_last, 10, unit_cost=8.0)
        self._set_date(move1 | move2, fields.Datetime.subtract(now, days=1))
        self.product_last.standard_price = 10.0
        manual = self.env["product.value"].search(
            [("product_id", "=", self.product_last.id), ("move_id", "=", False)],
            order="date desc, id desc",
            limit=1,
        )
        manual.date = fields.Datetime.subtract(now, hours=2)
        self.product_last.invalidate_recordset()
        self.assertAlmostEqual(self.product_last.total_value, 200.0)
        move3 = self._make_in_move(self.product_last, 5, unit_cost=12.0)
        self._set_date(move3, fields.Datetime.subtract(now, hours=1))
        self.product_last.invalidate_recordset()
        self.assertAlmostEqual(self.product_last.total_value, 260.0)
        self.assertAlmostEqual(self.product_last.standard_price, 12.0)

    def test_delivery_without_move_valued_at_last_price(self):
        self._make_in_move(self.product_last, 10, unit_cost=5.0)
        self._make_in_move(self.product_last, 10, unit_cost=8.0)
        self.assertAlmostEqual(self.product_last._run_fifo(4), 32.0)
