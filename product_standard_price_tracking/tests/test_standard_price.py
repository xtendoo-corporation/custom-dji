from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStandardPriceTracking(TransactionCase):
    def test_standard_price_field_definition(self):
        field = self.env["product.product"]._fields["standard_price"]
        self.assertTrue(field.company_dependent)
        self.assertEqual(field.string, "Cost")
        self.assertEqual(field.groups, "base.group_user")

    def test_standard_price_is_stored_per_product(self):
        product = self.env["product.product"].create(
            {"name": "Tracked product", "standard_price": 4.5}
        )
        product.standard_price = 6.25
        self.assertEqual(product.standard_price, 6.25)
