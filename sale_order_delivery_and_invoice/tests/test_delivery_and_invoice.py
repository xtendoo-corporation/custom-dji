from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDeliveryAndInvoice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Customer"})
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

    def _order(self, product, qty=3.0):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        return order

    def test_delivers_pending_moves_and_posts_invoice(self):
        product = self.env["product.product"].create(
            {
                "name": "Storable",
                "type": "consu",
                "is_storable": True,
                "invoice_policy": "delivery",
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            product, self.stock_location, 10.0
        )
        order = self._order(product)
        order.delivery_and_invoice()
        self.assertEqual(order.picking_ids.state, "done")
        self.assertEqual(order.order_line.qty_delivered, 3.0)
        self.assertEqual(order.invoice_ids.state, "posted")

    def test_done_pickings_are_skipped(self):
        product = self.env["product.product"].create(
            {"name": "Service", "type": "service", "invoice_policy": "order"}
        )
        order = self._order(product, qty=1.0)
        self.assertFalse(order.picking_ids)
        order.delivery_and_invoice()
        self.assertEqual(order.invoice_ids.state, "posted")
        self.assertEqual(order.invoice_ids.amount_untaxed, 10.0)
