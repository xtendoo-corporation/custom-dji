from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestDocumentFormatReports(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "Cliente informes", "email": "c@example.com"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Producto informes",
                "default_code": "PI-001",
                "is_storable": True,
                "list_price": 10.0,
            }
        )

    def _confirm(self, order):
        if "route_ids" in order._fields:
            # con sale_order_required_route instalado hace falta una ruta
            order.route_ids = self.env["stock.route"].create(
                {"name": "Ruta informes", "sale_selectable": True}
            )
        order.action_confirm()

    def _render(self, report_ref, records):
        html, _fmt = self.env["ir.actions.report"]._render_qweb_html(
            report_ref, records.ids
        )
        return html.decode() if isinstance(html, bytes) else html

    def _invoice(self, with_orphan_lines=True):
        lines = [
            (
                0,
                0,
                {
                    "product_id": self.product.id,
                    "quantity": 2,
                    "price_unit": 10.0,
                },
            )
        ]
        if with_orphan_lines:
            lines += [
                (0, 0, {"display_type": "line_section", "name": "Sección"}),
                (0, 0, {"display_type": "line_note", "name": "Nota"}),
                # línea sin producto y sin descripción
                (0, 0, {"name": False, "quantity": 1, "price_unit": 5.0}),
            ]
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": "2026-10-01",
                "invoice_line_ids": lines,
            }
        )
        invoice.action_post()
        return invoice

    def test_invoice_with_lines_without_product_or_name(self):
        invoice = self._invoice()
        for report in (
            "account.account_invoices",
            "document_format.report_invoice_not_grouped",
        ):
            html = self._render(report, invoice)
            self.assertIn("PI-001", html, report)

    def test_credit_note_with_lines_without_product_or_name(self):
        invoice = self._invoice()
        credit = invoice._reverse_moves(
            [{"invoice_date": "2026-10-02"}], cancel=False
        )
        credit.action_post()
        for report in (
            "account.account_invoices",
            "document_format.report_invoice_not_grouped",
        ):
            self.assertIn("PI-001", self._render(report, credit), report)

    def test_invoice_dossier(self):
        invoice = self._invoice()
        self.assertTrue(self._render("document_format.report_invoice_dossier", invoice))

    def test_sale_order_reports(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 3}),
                    (0, 0, {"display_type": "line_section", "name": "Sección"}),
                ],
            }
        )
        for report in (
            "sale.action_report_saleorder",
            "document_format.report_sale_order_blank_format",
            "document_format.action_report_saleorder_line",
        ):
            self.assertTrue(self._render(report, order), report)

    def test_purchase_order_report(self):
        order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_qty": 4,
                            "price_unit": 3.0,
                        },
                    )
                ],
            }
        )
        self.assertTrue(self._render("purchase.action_report_purchase_order", order))

    def test_delivery_reports(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 3})
                ],
            }
        )
        self._confirm(order)
        picking = order.picking_ids
        self.assertTrue(picking)
        for report in (
            "stock.action_report_delivery",
            "document_format.action_report_delivery",
        ):
            self.assertTrue(self._render(report, picking), report)
        # el albarán de mercancía no lleva tabla de productos, como en 13
        html = self._render("document_format.action_report_delivery", picking)
        self.assertNotIn("PI-001", html)

    def test_invoice_only_lines_without_product(self):
        """Sin ninguna línea con producto el informe agrupado usa el respaldo."""
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": "2026-10-01",
                "invoice_line_ids": [
                    (0, 0, {"name": False, "quantity": 1, "price_unit": 7.0}),
                    (0, 0, {"name": "Servicio sin producto", "quantity": 2, "price_unit": 4.0}),
                ],
            }
        )
        invoice.action_post()
        for report in (
            "account.account_invoices",
            "document_format.report_invoice_not_grouped",
        ):
            html = self._render(report, invoice)
            self.assertIn("Servicio sin producto", html, report)

    def test_delivery_without_price(self):
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        self.env["stock.quant"]._update_available_quantity(
            self.product, warehouse.lot_stock_id, 10
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 3})
                ],
            }
        )
        self._confirm(order)
        html = self._render(
            "document_format.report_delivery_without_price", order.picking_ids
        )
        self.assertIn("PI-001", html)
        self.assertNotIn("30.00", html)

    def _deliver(self, product, qty=3, lot=None, partner=True):
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        self.env["stock.quant"]._update_available_quantity(
            product, warehouse.lot_stock_id, 10, lot_id=lot
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": product.id, "product_uom_qty": qty})
                ],
            }
        )
        self._confirm(order)
        picking = order.picking_ids
        if not partner:
            picking.partner_id = False
        return picking

    def test_delivery_reports_with_lot_and_expiration_date(self):
        product = self.env["product.product"].create(
            {
                "name": "Producto con lote",
                "default_code": "PL-001",
                "is_storable": True,
                "tracking": "lot",
                "use_expiration_date": True,
            }
        )
        lot = self.env["stock.lot"].create(
            {
                "name": "LOTE-1",
                "product_id": product.id,
                "expiration_date": "2027-03-15 10:00:00",
            }
        )
        group = self.env.ref("stock.group_lot_on_delivery_slip")
        self.env.user.write({"group_ids": [(4, group.id)]})
        picking = self._deliver(product, lot=lot)
        for report in (
            "stock.action_report_delivery",
            "document_format.report_delivery_without_price",
        ):
            html = self._render(report, picking)
            self.assertIn("LOTE-1", html, report)
            self.assertIn("15/03/2027", html, report)

    def test_delivery_reports_without_partner(self):
        picking = self._deliver(self.product, partner=False)
        for report in (
            "stock.action_report_delivery",
            "document_format.action_report_delivery",
            "document_format.report_delivery_without_price",
        ):
            self.assertTrue(self._render(report, picking), report)

    def test_invoice_with_sepa_qr_enabled(self):
        self.env.company.qr_code = True
        bank = self.env["res.partner.bank"].create(
            {
                "acc_number": "ES9121000418450200051332",
                "partner_id": self.env.company.partner_id.id,
            }
        )
        invoice = self._invoice()
        invoice.partner_bank_id = bank
        for report in (
            "account.account_invoices",
            "document_format.report_invoice_not_grouped",
        ):
            self.assertIn("PI-001", self._render(report, invoice), report)

    def test_manufacture_report(self):
        component = self.env["product.product"].create(
            {"name": "Componente", "is_storable": True}
        )
        bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_qty": 1,
                "bom_line_ids": [(0, 0, {"product_id": component.id, "product_qty": 2})],
            }
        )
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        self.env["stock.quant"]._update_available_quantity(
            component, warehouse.lot_stock_id, 20
        )
        production = self.env["mrp.production"].create(
            {"product_id": self.product.id, "bom_id": bom.id, "product_qty": 3}
        )
        production.action_confirm()
        production.action_assign()
        self.assertTrue(production.move_raw_ids.move_line_ids)
        self.assertTrue(self._render("document_format.mrp_report", production))

    def test_not_grouped_invoice_mail_template(self):
        template = self.env.ref("document_format.email_template_grouped_invoice")
        invoice = self._invoice()
        for field in ("subject", "body_html", "email_from", "partner_to", "lang"):
            value = template._render_field(field, invoice.ids)[invoice.id]
            self.assertNotIn("${", str(value), field)
            self.assertNotIn("{{", str(value), field)
        body = template._render_field("body_html", invoice.ids)[invoice.id]
        self.assertIn("Cliente informes", body)
        self.assertIn(invoice.name, body)
        self.assertIn("Please remit payment", body)
        mail = self.env["mail.mail"].browse(
            template.send_mail(invoice.id, force_send=False)
        )
        self.assertTrue(mail.attachment_ids)
        self.assertIn(invoice.name.replace("/", "_"), mail.attachment_ids[0].name)

