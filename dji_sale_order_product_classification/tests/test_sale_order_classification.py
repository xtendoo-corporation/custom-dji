# Copyright 2023 Xtendoo (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleOrderClassification(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Classification Customer"})
        cls.classification_a = cls.env["product.classification"].create(
            {"name": "Alpha", "sequence": 1}
        )
        cls.classification_b = cls.env["product.classification"].create(
            {"name": "Beta", "sequence": 2}
        )
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Product A",
                "product_classification_id": cls.classification_a.id,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Product B",
                "product_classification_id": cls.classification_b.id,
            }
        )
        cls.product_plain = cls.env["product.product"].create(
            {"name": "Product Plain"}
        )

    def _create_order(self, products):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": product.id, "product_uom_qty": 1})
                    for product in products
                ],
            }
        )

    def test_empty_order_has_empty_classification(self):
        order = self._create_order([])
        self.assertFalse(order.classification_str)

    def test_product_without_classification_gives_empty_string(self):
        order = self._create_order([self.product_plain])
        self.assertEqual(order.classification_str, "")

    def test_single_classification_name(self):
        order = self._create_order([self.product_a])
        self.assertEqual(order.classification_str, "Alpha")

    def test_multiple_classifications_are_comma_joined(self):
        order = self._create_order([self.product_a, self.product_b])
        self.assertEqual(order.classification_str, "Alpha,Beta")

    def test_classification_recomputed_when_line_added(self):
        order = self._create_order([self.product_a])
        self.assertEqual(order.classification_str, "Alpha")
        order.write(
            {
                "order_line": [
                    (0, 0, {"product_id": self.product_b.id, "product_uom_qty": 1})
                ]
            }
        )
        self.assertEqual(order.classification_str, "Alpha,Beta")
