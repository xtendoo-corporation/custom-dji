# Copyright 2020 Carlos Roca <carlos.roca@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import MagicMock, call, patch

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.web.controllers.report import ReportController as WebReportController

from ..controllers import main
from ..controllers.main import SVGWitoutTextWriter


class TestStockPickingProductBarcodeReport(BaseCommon):
    def setUp(self):
        super().setUp()
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.product_barcode = self.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "consu",
                "is_storable": True,
                "barcode": "1001",
            }
        )
        self.product_no_barcode = self.env["product.product"].create(
            {"name": "Test Product 2", "type": "consu", "is_storable": True}
        )
        self.package = self.env["stock.package"].create({"name": "Pack-Test"})
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.picking = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": partner.id,
                "picking_type_id": self.env.ref(
                    "stock.picking_type_in"
                ).id,  # Operation type Receipts
                "move_ids": [
                    Command.create(
                        {
                            "product_id": self.product_barcode.id,
                            "product_uom_qty": 20,
                            "product_uom": self.product_barcode.uom_id.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                        },
                    ),
                    Command.create(
                        {
                            "product_id": self.product_no_barcode.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product_barcode.uom_id.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.stock_location.id,
                        },
                    ),
                ],
            }
        )
        self.picking.action_confirm()
        self.picking._action_done()
        for move_line_id in self.picking.move_line_ids:
            move_line_id.result_package_id = self.package
        self.wizard = (
            self.env["stock.picking.print"]
            .with_context(active_ids=self.picking.ids, active_model="stock.picking")
            .create({})
        )

    def test_wizard_creation(self):
        self.wizard.barcode_report = self.env.ref(
            "xtendoo_stock_picking_product_barcode_report.action_label_barcode_report"
        )
        self.wizard._onchange_picking_ids()
        self.assertEqual(1, len(self.wizard.product_print_moves.ids))
        line = self.wizard.product_print_moves[0]
        self.assertEqual(line.label_qty, 1)
        self.assertEqual(line.product_id.id, self.product_barcode.id)
        # This two sentences are added just for check that not throw an exception
        self.wizard.barcode_format = "gs1_128"
        self.wizard.print_labels()
        # Check that wizard add lines with packages and the label not
        # throw an exception when trying to print it
        self.wizard.barcode_report = self.env.ref(
            "xtendoo_stock_picking_product_barcode_report.action_label_barcode_report_quant_package"
        )
        self.wizard._onchange_picking_ids()
        self.assertEqual(2, len(self.wizard.product_print_moves.ids))
        line = self.wizard.product_print_moves[0]
        self.assertEqual(line.label_qty, 1)
        self.assertEqual(line.product_id.id, self.product_barcode.id)
        self.wizard.print_labels()

    def test_wizard_quants(self):
        quant = self.env["stock.quant"].create(
            {
                "product_id": self.product_barcode.id,
                "location_id": self.stock_location.id,
                "quantity": 20.0,
            }
        )
        quant_wizard = (
            self.env["stock.picking.print"]
            .with_context(**{"active_ids": quant.ids, "active_model": "stock.quant"})
            .create({})
        )
        quant_wizard.barcode_report = self.env.ref(
            "xtendoo_stock_picking_product_barcode_report.action_label_barcode_report"
        )
        self.assertEqual(len(quant_wizard.product_print_moves), 1)
        self.assertEqual(quant_wizard.product_print_moves.quantity, 20)
        quant_wizard.print_labels()

    def test_init(self):
        writer = SVGWitoutTextWriter(module_max_height=200)
        self.assertEqual(writer.module_max_height, 200)
        writer = SVGWitoutTextWriter()
        self.assertEqual(writer.module_max_height, 100)

    def test_create_module(self):
        writer = SVGWitoutTextWriter(module_max_height=100)
        writer._document = MagicMock()
        writer._group = MagicMock()
        xpos = 10
        ypos = 20
        width = 30
        color = "black"
        writer._create_module(xpos, ypos, width, color)
        writer._document.createElement.assert_called_once_with("rect")
        element = writer._document.createElement.return_value
        element.setAttribute.assert_has_calls(
            [
                call("x", "10.000mm"),
                call("y", "20.000mm"),
                call("width", "30.000mm"),
                call("height", "100"),
                call("style", "fill:black"),
            ],
            any_order=False,
        )
        writer._group.appendChild.assert_called_once_with(element)

    def test_create_text_is_ignored(self):
        writer = SVGWitoutTextWriter()
        writer._group = MagicMock()
        self.assertIsNone(writer._create_text(1, 2))
        writer._group.appendChild.assert_not_called()

    def test_report_barcode_gs1_128(self):
        fake_request = MagicMock()
        with patch.object(main, "request", fake_request):
            main.ReportController.report_barcode.original_endpoint(
                main.ReportController(), "gs1_128", "0101234567890128"
            )
        image = fake_request.make_response.call_args.args[0]
        headers = fake_request.make_response.call_args.kwargs["headers"]
        self.assertIn(b"<svg", image if isinstance(image, bytes) else image.encode())
        self.assertEqual(headers, [("Content-Type", "image/svg+xml")])

    def test_report_barcode_other_types_use_core(self):
        with patch.object(
            WebReportController, "report_barcode", return_value="core"
        ) as core_barcode:
            result = main.ReportController.report_barcode.original_endpoint(
                main.ReportController(), "EAN13", "1234567890128"
            )
        self.assertEqual(result, "core")
        core_barcode.assert_called_once()

    def test_lang_selection(self):
        langs = self.env["stock.picking.print"]._get_lang()
        self.assertIn("en_US", [code for code, _name in langs])

    def test_wizard_from_move_lines(self):
        move_lines = self.picking.move_line_ids
        wizard = (
            self.env["stock.picking.print"]
            .with_context(active_ids=move_lines.ids, active_model="stock.move.line")
            .create({})
        )
        self.assertEqual(wizard.stock_move_line_ids, move_lines)
        wizard._onchange_picking_ids()
        self.assertEqual(len(wizard.product_print_moves), 2)

    def test_wizard_from_lots(self):
        product = self.env["product.product"].create(
            {"name": "Lote", "is_storable": True, "tracking": "lot"}
        )
        lot = self.env["stock.lot"].create({"name": "L-1", "product_id": product.id})
        wizard = (
            self.env["stock.picking.print"]
            .with_context(active_ids=lot.ids, active_model="stock.lot")
            .create({})
        )
        self.assertEqual(wizard.product_print_moves.lot_id, lot)
        self.assertEqual(wizard.product_print_moves.product_id, product)

    def test_move_line_to_print_from_context(self):
        move_line = self.picking.move_line_ids[:1]
        lines = (
            self.env["stock.picking.print"]
            .with_context(stock_move_line_to_print=move_line.id)
            ._get_move_lines(self.picking)
        )
        self.assertEqual(lines, move_line)

    def test_other_report_returns_all_move_lines(self):
        self.wizard.barcode_report = self.env["ir.actions.report"].search(
            [("model", "=", "stock.picking")], limit=1
        )
        self.assertEqual(
            self.wizard._get_move_lines(self.picking), self.picking.move_line_ids
        )

    def test_print_custom_label(self):
        report = self.env.ref(
            "xtendoo_stock_picking_product_barcode_report.action_label_barcode_report"
        )
        report.is_custom_label = True
        self.wizard.barcode_report = report
        self.assertTrue(self.wizard.is_custom_label)
        action = self.wizard.with_context(discard_logo_check=True).print_labels()
        self.assertEqual(action["report_name"], report.report_name)

    def test_create_label_print_wiz_from_move_line(self):
        report = self.env.ref(
            "xtendoo_stock_picking_product_barcode_report.action_label_barcode_report"
        )
        wizard_model = self.env["stock.picking.print"].with_context(
            force_quantity_line=3.0
        )
        wizard = wizard_model.create_label_print_wiz_from_move_line(
            report.id, self.picking.move_line_ids.ids
        )
        self.assertEqual(len(wizard.product_print_moves), 2)
        self.assertEqual(set(wizard.product_print_moves.mapped("quantity")), {3.0})
        wizard = wizard_model.create_label_print_wiz_from_move_line(
            report.id, self.picking.move_line_ids[:1]
        )
        self.assertEqual(len(wizard.product_print_moves), 1)
