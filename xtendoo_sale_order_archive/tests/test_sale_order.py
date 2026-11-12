from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderArchive(TransactionCase):
    def test_orders_are_active_and_can_be_archived(self):
        partner = self.env["res.partner"].create({"name": "Customer"})
        order = self.env["sale.order"].create({"partner_id": partner.id})
        self.assertTrue(order.active)
        order.action_archive()
        self.assertFalse(order.active)
        self.assertNotIn(
            order, self.env["sale.order"].search([("partner_id", "=", partner.id)])
        )
        order.action_unarchive()
        self.assertTrue(order.active)
