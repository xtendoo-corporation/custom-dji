# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestInvoiceReportDueList(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payment_term_normal = cls.env["account.payment.term"].create(
            {
                "name": "One Time Payment Term",
                "line_ids": [
                    (0, 0, {"value": "percent", "value_amount": 100.0, "nb_days": 30})
                ],
            }
        )
        cls.payment_term_multi = cls.env["account.payment.term"].create(
            {
                "name": "Twice Payment Term",
                "line_ids": [
                    (0, 0, {"value": "percent", "value_amount": 25.0, "nb_days": 30}),
                    (0, 0, {"value": "percent", "value_amount": 75.0, "nb_days": 60}),
                ],
            }
        )
        cls.other_currency = cls.setup_other_currency("EUR")

    def _create_invoice(self, move_type="out_invoice", currency=None, amount=100.0):
        invoice = self.init_invoice(
            move_type,
            partner=self.partner_a,
            amounts=[amount],
            taxes=self.env["account.tax"],
            currency=currency,
        )
        invoice.invoice_payment_term_id = self.payment_term_multi
        invoice.action_post()
        return invoice

    def test_multi_due_flag(self):
        invoice = self.init_invoice("out_invoice", amounts=[100.0])
        invoice.invoice_payment_term_id = self.payment_term_normal
        self.assertFalse(invoice.multi_due)
        invoice.invoice_payment_term_id = self.payment_term_multi
        self.assertTrue(invoice.multi_due)

    def test_due_list_customer_invoice(self):
        invoice = self._create_invoice()
        due_list = invoice.get_multi_due_list()
        self.assertEqual([due[1] for due in due_list], [25.0, 75.0])
        self.assertEqual([due[2] for due in due_list], [25.0, 75.0])
        self.assertLess(due_list[0][0], due_list[1][0])
        self.assertEqual(len(invoice.multi_date_due.split()), 2)

    def test_due_list_vendor_bill(self):
        bill = self._create_invoice("in_invoice")
        due_list = bill.get_multi_due_list()
        self.assertEqual([due[1] for due in due_list], [-25.0, -75.0])

    def test_due_list_other_currency(self):
        invoice = self._create_invoice(currency=self.other_currency, amount=200.0)
        self.assertEqual(invoice.get_multi_due_list()[0][2], 50.0)

    def test_due_list_entry_is_empty(self):
        entry = self.env["account.move"].create({"move_type": "entry"})
        self.assertEqual(entry.get_multi_due_list(), [])
        self.assertEqual(entry.multi_date_due, "")

    def test_report_shows_due_list(self):
        invoice = self._create_invoice()
        html = (
            self.env["ir.actions.report"]
            ._render_qweb_html("account.report_invoice", invoice.ids)[0]
            .decode()
        )
        self.assertIn("Outstanding", html)
