from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderProductDefaultUom(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Cliente uom"})
        cls.product_default = cls.env["product.product"].create(
            {"name": "Con unidades por defecto", "uom_qty": 6.0}
        )
        cls.product_plain = cls.env["product.product"].create({"name": "Normal"})

    def _line_qty(self, product):
        with Form(self.env["sale.order"]) as order:
            order.partner_id = self.partner
            with order.order_line.new() as line:
                line.product_id = product
                qty = line.product_uom_qty
        return qty

    def test_default_units_applied_in_form(self):
        self.assertAlmostEqual(self._line_qty(self.product_default), 6.0)

    def test_plain_product_keeps_core_default(self):
        self.assertAlmostEqual(self._line_qty(self.product_plain), 1.0)

    def test_field_in_product_form(self):
        arch = self.env["product.template"].get_view(view_type="form")["arch"]
        self.assertIn('name="uom_qty"', arch)
