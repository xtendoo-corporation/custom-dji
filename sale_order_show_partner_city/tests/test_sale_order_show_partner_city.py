from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderShowPartnerCity(TransactionCase):
    def test_city_follows_partner(self):
        partner = self.env["res.partner"].create({"name": "Cliente", "city": "Sevilla"})
        order = self.env["sale.order"].create({"partner_id": partner.id})
        self.assertEqual(order.partner_city, "Sevilla")
        partner.city = "Cádiz"
        self.assertEqual(order.partner_city, "Cádiz")

    def test_city_column_in_quotation_and_order_lists(self):
        for xmlid in ("sale.view_quotation_tree", "sale.view_order_tree"):
            view = self.env.ref(xmlid)
            arch = self.env["sale.order"].get_view(view.id, "list")["arch"]
            self.assertIn('name="partner_city"', arch, xmlid)
