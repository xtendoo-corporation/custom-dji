from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderShowShippingAddress(TransactionCase):
    def test_shipping_column_in_quotation_list(self):
        view = self.env.ref("sale.view_quotation_tree")
        arch = self.env["sale.order"].get_view(view.id, "list")["arch"]
        self.assertIn('name="partner_shipping_id"', arch)
        self.assertIn('optional="hide"', arch)
