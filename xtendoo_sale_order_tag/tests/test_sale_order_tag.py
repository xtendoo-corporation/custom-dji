from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderTag(TransactionCase):
    def test_tag_defaults_and_assignment(self):
        tag = self.env["sale.order.tag"].create({"name": "VIP"})
        self.assertTrue(tag.active)
        self.assertIsInstance(tag.sequence, int)
        partner = self.env["res.partner"].create({"name": "Customer"})
        order = self.env["sale.order"].create(
            {"partner_id": partner.id, "so_tag_ids": [(6, 0, tag.ids)]}
        )
        self.assertEqual(order.so_tag_ids, tag)

    def test_sequence_falls_back_to_zero(self):
        self.env["ir.sequence"].search([("code", "=", "sale.order.tag")]).unlink()
        tag = self.env["sale.order.tag"].create({"name": "No sequence"})
        self.assertEqual(tag.sequence, 0)
