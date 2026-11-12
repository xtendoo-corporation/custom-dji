from unittest.mock import patch

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestUpdateCostFix(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env["product.template"].create(
            {"name": "Cost product", "standard_price": 5.0}
        )
        cls.product = cls.template.product_variant_id

    def test_template_onchange_syncs_variant_when_price_differs(self):
        template_cls = type(self.env["product.template"])
        other = self.env["product.product"].create(
            {"name": "Other", "standard_price": 1.0}
        )
        with patch.object(
            type(self.env["product.product"]), "search", return_value=other
        ), patch.object(template_cls, "_set_standard_price") as setter:
            self.template.onchange_standard_price()
        setter.assert_called_once()

    def test_template_onchange_skips_when_price_matches(self):
        template_cls = type(self.env["product.template"])
        with patch.object(template_cls, "_set_standard_price") as setter:
            self.template.onchange_standard_price()
        setter.assert_not_called()

    def test_variant_onchange_propagates_to_template(self):
        product_cls = type(self.env["product.product"])
        changed = self.env["product.product"].new(
            {"product_tmpl_id": self.template.id, "standard_price": 9.0}
        )
        with patch.object(
            product_cls, "_set_standard_price_template"
        ) as setter:
            self.product.onchange_standard_price()
            setter.assert_not_called()
            changed.onchange_standard_price()
            setter.assert_called_once()

    def test_set_standard_price_template_writes_template(self):
        self.product.standard_price = 7.5
        self.product._set_standard_price_template()
        self.assertEqual(self.template.standard_price, 7.5)

    def test_set_standard_price_template_on_new_record(self):
        draft = self.env["product.product"].new({"name": "Borrador", "standard_price": 7.0})
        draft._set_standard_price_template()
        self.assertEqual(draft.product_tmpl_id.standard_price, 7.0)
