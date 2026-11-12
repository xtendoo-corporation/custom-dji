from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestDocumentFormatGroupingXtendoo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Cliente agrupado"})
        cls.product_a, cls.product_b = cls.env["product.product"].create(
            [
                {"name": "Producto A", "is_storable": True, "list_price": 10.0},
                {"name": "Producto B", "is_storable": True, "list_price": 5.0},
            ]
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        for product in (cls.product_a, cls.product_b):
            cls.env["stock.quant"]._update_available_quantity(
                product, cls.stock_location, 100.0
            )

    def _delivered_order(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_a.id, "product_uom_qty": 3}),
                    (0, 0, {"product_id": self.product_b.id, "product_uom_qty": 2}),
                ],
            }
        )
        order.action_confirm()
        picking = order.picking_ids
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.move_ids.picked = True
        picking.button_validate()
        return order, picking

    def _invoice(self, order):
        invoice = order._create_invoices()
        invoice.action_post()
        return invoice

    def test_validation_restores_sale_line_link(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (0, 0, {"product_id": self.product_a.id, "product_uom_qty": 1}),
                ],
            }
        )
        order.action_confirm()
        picking = order.picking_ids
        sale_line = order.order_line.filtered(
            lambda line: line.product_id == self.product_a
        )
        extra_move = self.env["stock.move"].create(
            {
                "product_id": self.product_a.id,
                "product_uom_qty": 1,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        extra_move._action_confirm()
        self.assertFalse(extra_move.sale_line_id)
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty
        picking.move_ids.picked = True
        picking.button_validate()
        self.assertEqual(extra_move.sale_line_id, sale_line)

    def test_lines_grouped_by_delivered_picking(self):
        order, picking = self._delivered_order()
        invoice = self._invoice(order)
        grouped = invoice.lines_grouped_by_picking()
        self.assertEqual({group["picking"] for group in grouped}, {picking})
        self.assertEqual(sorted(group["quantity"] for group in grouped), [2.0, 3.0])

    def test_lines_grouped_through_sale_order(self):
        order, picking = self._delivered_order()
        invoice = self._invoice(order)
        line_b = invoice.invoice_line_ids.filtered(
            lambda line: line.product_id == self.product_b
        )
        line_b.move_line_ids = [(5,)]
        grouped = invoice.lines_grouped_by_picking()
        group_b = [group for group in grouped if group["line"] == line_b]
        self.assertEqual(group_b[0]["picking"], picking)
        self.assertEqual(group_b[0]["quantity"], 2.0)

    def _refund(self, moves):
        refund = self.env["account.move"].create(
            {
                "move_type": "out_refund",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                            "quantity": 3,
                            "price_unit": 10.0,
                            "move_line_ids": [(6, 0, moves.ids)],
                        },
                    )
                ],
            }
        )
        return refund

    def test_refund_without_returned_goods(self):
        _order, picking = self._delivered_order()
        move_a = picking.move_ids.filtered(lambda move: move.product_id == self.product_a)
        grouped = self._refund(move_a).lines_grouped_by_picking()
        self.assertEqual(len(grouped), 1)
        self.assertEqual(grouped[0]["quantity"], 3.0)

    def test_refund_with_returned_goods(self):
        return_move = self.env["stock.move"].create(
            {
                "product_id": self.product_a.id,
                "product_uom_qty": 3,
                "location_id": self.customer_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        return_move._action_confirm()
        return_move.quantity = 3
        return_move.picked = True
        return_move._action_done()
        grouped = self._refund(return_move).lines_grouped_by_picking()
        self.assertEqual(grouped[0]["quantity"], 3.0)

    def _pickings(self, names):
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        picking_type = self.env.ref("stock.picking_type_out")
        pickings = self.env["stock.picking"]
        for name in names:
            pickings |= self.env["stock.picking"].create(
                {
                    "name": name,
                    "picking_type_id": picking_type.id,
                    "location_id": self.stock_location.id,
                    "location_dest_id": self.customer_location.id,
                    "sale_id": order.id,
                }
            )
        return pickings

    def test_pic_name_single_delivery(self):
        pic, alb = self._pickings(["PIC/0001", "ALB/0001"])
        self.assertEqual(pic.pic_name, "ALB/0001")
        self.assertEqual(alb.pic_name, "ALB/0001")

    def test_pic_name_without_delivery(self):
        (pic,) = self._pickings(["PIC/0002"])
        self.assertEqual(pic.pic_name, "PIC/0002")

    def test_pic_name_several_deliveries(self):
        pickings = self._pickings(["PIC/0003", "PIC/0004", "ALB/0003", "ALB/0004"])
        pic_names = set(pickings[:2].mapped("pic_name"))
        self.assertEqual(pic_names, {"ALB/0003", "ALB/0004"})

    def test_saleorder_accumulate_lines(self):
        orders = self.env["sale.order"].create(
            [
                {
                    "partner_id": self.partner.id,
                    "order_line": [
                        (0, 0, {"product_id": self.product_a.id, "product_uom_qty": qty}),
                    ],
                }
                for qty in (2, 3)
            ]
        )
        report = self.env["report.document_format.report_saleorder_line"]
        values = report._get_report_values(orders.ids)
        lines = values["get_saleorder_lines"](orders.ids)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["product_name"], "Producto A")
        self.assertEqual(lines[0]["product_qty"], 5.0)
