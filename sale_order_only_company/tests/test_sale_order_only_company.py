from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderOnlyCompany(TransactionCase):
    def test_customer_domain_in_form(self):
        arch = self.env["sale.order"].get_view(view_type="form")["arch"]
        self.assertIn("is_company", arch)
        self.assertIn("res_partner_search_mode", arch)

    def test_domain_filters_people(self):
        company = self.env["res.partner"].create({"name": "Empresa SL", "is_company": True})
        person = self.env["res.partner"].create({"name": "Persona", "is_company": False})
        found = self.env["res.partner"].search(
            [
                "|",
                "&",
                ("company_id", "=", False),
                ("company_id", "=", self.env.company.id),
                ("is_company", "=", True),
                ("id", "in", (company | person).ids),
            ]
        )
        self.assertEqual(found, company)
