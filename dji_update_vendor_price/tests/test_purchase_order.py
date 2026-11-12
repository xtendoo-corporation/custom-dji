from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestUpdateVendorPrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor DJI"})
        cls.contact = cls.env["res.partner"].create(
            {"name": "Vendor Contact", "parent_id": cls.vendor.id}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Product DJI", "type": "consu"}
        )

    def _create_order(self, partner, price):
        return self.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 1.0,
                            "price_unit": price,
                        },
                    )
                ],
            }
        )

    def _add_seller(self, partner, price):
        return self.env["product.supplierinfo"].create(
            {
                "partner_id": partner.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "price": price,
            }
        )

    def test_existing_seller_price_is_updated(self):
        seller = self._add_seller(self.vendor, 5.0)
        self._create_order(self.vendor, 12.5).button_confirm()
        self.assertEqual(seller.price, 12.5)

    def test_contact_order_updates_parent_seller(self):
        seller = self._add_seller(self.vendor, 5.0)
        self._create_order(self.contact, 8.0).button_confirm()
        self.assertEqual(seller.price, 8.0)
        self.assertNotIn(
            self.contact, self.product.seller_ids.mapped("partner_id")
        )

    def test_same_price_is_not_rewritten(self):
        seller = self._add_seller(self.vendor, 7.0)
        write_date = seller.write_date
        self._create_order(self.vendor, 7.0).button_confirm()
        self.assertEqual(seller.price, 7.0)
        self.assertEqual(seller.write_date, write_date)

    def test_new_seller_created_by_standard_flow(self):
        self._create_order(self.vendor, 9.0).button_confirm()
        seller = self.product.seller_ids.filtered(
            lambda info: info.partner_id == self.vendor
        )
        self.assertEqual(len(seller), 1)
        self.assertEqual(seller.price, 9.0)

    def test_no_seller_and_no_creation(self):
        self.product.seller_ids = [
            (0, 0, {"partner_id": self.env["res.partner"].create(
                {"name": "Other %s" % index}).id, "price": 1.0})
            for index in range(11)
        ]
        self._create_order(self.vendor, 3.0).button_confirm()
        self.assertNotIn(
            self.vendor, self.product.seller_ids.mapped("partner_id")
        )
