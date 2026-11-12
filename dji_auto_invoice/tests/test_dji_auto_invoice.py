from unittest.mock import patch

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo import fields
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDjiAutoInvoice(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Auto invoice partner",
            "email": "auto@example.com",
            "auto_invoice": True,
        })

    def _create_invoice(self, partner=None, move_type="out_invoice"):
        return self.env["account.move"].create({
            "move_type": move_type,
            "partner_id": (partner or self.partner).id,
            "invoice_date": fields.Date.today(),
            "invoice_line_ids": [(0, 0, {"name": "Line", "quantity": 1, "price_unit": 100})],
        })

    def test_partner_auto_invoice_defaults_to_false(self):
        partner = self.env["res.partner"].create({"name": "Plain"})
        self.assertFalse(partner.auto_invoice)

    def test_action_post_sends_email_when_all_conditions_met(self):
        invoice = self._create_invoice()
        with patch.object(type(invoice), "send_email") as send_email:
            invoice.action_post()
        send_email.assert_called_once()
        self.assertEqual(invoice.state, "posted")

    def test_action_post_skips_email_without_partner_email(self):
        partner = self.env["res.partner"].create({"name": "No mail", "auto_invoice": True})
        invoice = self._create_invoice(partner=partner)
        with patch.object(type(invoice), "send_email") as send_email:
            invoice.action_post()
        send_email.assert_not_called()

    def test_action_post_skips_email_when_partner_not_auto_invoice(self):
        self.partner.auto_invoice = False
        invoice = self._create_invoice()
        with patch.object(type(invoice), "send_email") as send_email:
            invoice.action_post()
        send_email.assert_not_called()

    def test_action_post_skips_email_for_non_customer_invoice(self):
        invoice = self._create_invoice(move_type="in_invoice")
        with patch.object(type(invoice), "send_email") as send_email:
            invoice.action_post()
        send_email.assert_not_called()

    def test_send_email_uses_invoice_template(self):
        invoice = self._create_invoice()
        invoice.action_post()
        template_model = type(self.env.ref("account.email_template_edi_invoice"))
        with patch.object(template_model, "send_mail", return_value=42) as send_mail:
            result = invoice.send_email()
        self.assertEqual(result, 42)
        send_mail.assert_called_once_with(invoice.id)

    def test_send_email_requires_single_record(self):
        invoices = self._create_invoice() | self._create_invoice()
        with self.assertRaises(ValueError):
            invoices.send_email()
