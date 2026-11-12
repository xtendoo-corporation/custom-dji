from odoo.addons.base.tests.common import BaseCommon


class TestWebsiteWhatsapp(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].create(
            {
                "name": "Test Website",
                "whatsapp_text": "Hola",
                "whatsapp_track_url": True,
            }
        )

    def test_track_url_with_domain_strips_query(self):
        self.website.domain = "https://shop.example.com"
        message = self.website._get_track_url_message("/shop?page=2")
        self.assertTrue(message.startswith("Hola %0A%0A*"))
        self.assertIn("https://shop.example.com /shop", message)
        self.assertNotIn("page=2", message)

    def test_track_url_falls_back_to_base_url(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "web.base.url", "https://base.example.com"
        )
        message = self.website._get_track_url_message("/contactus")
        self.assertIn("https://base.example.com /contactus", message)

    def test_without_track_url_returns_default_text(self):
        self.website.whatsapp_track_url = False
        self.assertEqual(self.website._get_track_url_message("/shop"), "Hola")
