from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged("post_install", "-at_install")
class TestCustomerInvoiceDeliveryAddress(TransactionCase):
    def test_domains_in_sale_order_and_invoice_forms(self):
        user = new_test_user(
            self.env,
            login="usuario_direcciones",
            groups="sales_team.group_sale_salesman,account.group_account_invoice,"
            "account.group_delivery_invoice_address,base.group_user",
        )
        order_arch = self.env["sale.order"].with_user(user).get_view(view_type="form")["arch"]
        move_arch = self.env["account.move"].with_user(user).get_view(view_type="form")["arch"]
        self.assertIn("('parent_id', '=', partner_id)", order_arch)
        self.assertIn("('parent_id', '=', partner_id)", move_arch)

    def test_domain_returns_only_contacts_of_the_customer(self):
        company = self.env["res.partner"].create({"name": "Cliente SL", "is_company": True})
        child = self.env["res.partner"].create({"name": "Entrega", "parent_id": company.id})
        other = self.env["res.partner"].create({"name": "Otro", "is_company": True})
        found = self.env["res.partner"].search([("parent_id", "=", company.id)])
        self.assertEqual(found, child)
        self.assertNotIn(other, found)
