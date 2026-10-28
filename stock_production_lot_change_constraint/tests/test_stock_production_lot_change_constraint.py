from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestLotChangeConstraint(TransactionCase):
    def test_duplicate_lot_names_allowed(self):
        product = self.env["product.product"].create(
            {"name": "Con lote", "is_storable": True, "tracking": "lot"}
        )
        lot1 = self.env["stock.lot"].create(
            {"name": "L-001", "product_id": product.id, "company_id": self.env.company.id}
        )
        lot2 = self.env["stock.lot"].create(
            {"name": "L-001", "product_id": product.id, "company_id": self.env.company.id}
        )
        self.assertEqual(lot1.name, lot2.name)
        self.assertNotEqual(lot1, lot2)
