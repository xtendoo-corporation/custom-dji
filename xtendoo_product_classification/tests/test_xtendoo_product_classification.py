from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestProductClassification(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.class_a = cls.env["product.classification"].create({"name": "A", "sequence": 1})
        cls.class_b = cls.env["product.classification"].create({"name": "B", "sequence": 2})
        cls.product = cls.env["product.template"].create(
            {"name": "Clasificado", "product_classification_id": cls.class_a.id}
        )

    def test_products_count(self):
        self.class_a.invalidate_recordset()
        self.assertEqual(self.class_a.products_count, 1)
        self.assertEqual(self.class_b.products_count, 0)

    def test_order_by_sequence(self):
        found = self.env["product.classification"].search(
            [("id", "in", (self.class_a | self.class_b).ids)]
        )
        self.assertEqual(found.mapped("name"), ["A", "B"])

    def test_group_expand_shows_empty_classifications(self):
        groups = self.env["product.template"].read_group(
            [("id", "=", self.product.id)],
            ["product_classification_id"],
            ["product_classification_id"],
        )
        names = [g["product_classification_id"][1] for g in groups if g["product_classification_id"]]
        self.assertIn("A", names)
        self.assertIn("B", names)
