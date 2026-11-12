import base64
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from odoo.tests import common

from ..hooks import post_init_hook, uninstall_hook
from ..models import assetsbundle
from ..models.res_company import URL_BASE
from ..utils import convert_to_image, image_to_rgb

BUNDLE = "xtendoo_web_company_color.company_color_assets"


class TestCompanyColorAssets(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.other_company = cls.env["res.company"].create({"name": "Otra empresa"})

    def _fake_request(self, cookie):
        cookies = {"cids": cookie} if cookie is not None else {}
        return SimpleNamespace(httprequest=SimpleNamespace(cookies=cookies))

    def test_asset_node_from_cookie_company(self):
        bundle = assetsbundle.AssetsBundleCompanyColor(BUNDLE, [], env=self.env)
        fake_request = self._fake_request(f"{self.other_company.id}-{self.company.id}")
        with patch.object(assetsbundle, "request", fake_request):
            url = bundle.get_company_color_asset_node()
        self.assertEqual(url, self.other_company.scss_get_url())

    def test_asset_node_falls_back_to_current_company(self):
        bundle = assetsbundle.AssetsBundleCompanyColor(BUNDLE, [], env=self.env)
        with patch.object(assetsbundle, "request", self._fake_request(None)):
            url = bundle.get_company_color_asset_node()
        self.assertEqual(url, self.company.scss_get_url())

    def test_generate_asset_links_adds_company_scss(self):
        links = self.env["ir.qweb"]._generate_asset_links(BUNDLE)
        self.assertIn(self.company.scss_get_url(), links)

    def test_asset_content_of_other_bundle_delegates_to_core(self):
        files, _remains = self.env["ir.qweb"]._get_asset_content("web.assets_frontend_minimal")
        self.assertTrue(files)

    def test_asset_content_of_company_bundle_is_empty(self):
        self.assertEqual(self.env["ir.qweb"]._get_asset_content(BUNDLE), ([], []))

    def test_asset_nodes_drop_type_attribute(self):
        self.env.registry.clear_cache("assets")
        nodes = self.env["ir.qweb"]._get_asset_nodes(BUNDLE, js=False)
        company_nodes = [
            attributes
            for tag, attributes in nodes
            if tag == "link" and attributes.get("href", "").startswith(URL_BASE)
        ]
        self.assertTrue(company_nodes)
        self.assertFalse([attrs for attrs in company_nodes if "type" in attrs])

    def test_hooks(self):
        attachments = self.env["ir.attachment"].search([("url", "=like", f"{URL_BASE}%")])
        self.assertTrue(attachments)
        uninstall_hook(self.env)
        self.assertFalse(attachments.exists())
        post_init_hook(self.env)
        count = self.env["ir.attachment"].search_count([("url", "=like", f"{URL_BASE}%")])
        self.assertEqual(count, self.env["res.company"].search_count([]))

    def test_unlink_removes_scss_attachment(self):
        company = self.env["res.company"].create({"name": "Empresa temporal"})
        url = company.scss_get_url()
        company.unlink()
        self.assertFalse(self.env["ir.attachment"].search([("url", "=", url)]))

    def test_write_ignoring_company_color(self):
        company = self.other_company.with_context(ignore_company_color=True)
        with patch.object(
            type(company), "scss_create_or_update_attachment"
        ) as update_attachment:
            company.write({"color_navbar_bg": "#123456"})
        update_attachment.assert_not_called()
        self.assertEqual(self.other_company.color_navbar_bg, "#123456")

    def test_image_to_rgb_converts_non_rgba_image(self):
        buffer = BytesIO()
        Image.new("RGB", (8, 8), (0, 0, 255)).save(buffer, format="PNG")
        image = convert_to_image(base64.b64encode(buffer.getvalue()))
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image_to_rgb(image), (0.0, 0.0, 1.0))
