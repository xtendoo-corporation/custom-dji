from odoo import api, models


class ReportSaleOrderLine(models.AbstractModel):
    _name = "report.document_format_dji.report_saleorder_line"
    _description = "Report Quotations Products Accumulate"

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            "docids": docids,
            "get_saleorder_lines": self.get_saleorder_lines,
        }

    @api.model
    def get_saleorder_lines(self, docids):
        groups = self.env["sale.order.line"]._read_group(
            [("order_id", "in", docids), ("product_id", "!=", False)],
            ["product_id"],
            ["product_uom_qty:sum"],
        )
        records = [
            {
                "product_name": product.name,
                "product_classification_sequence": (
                    product.product_classification_id.sequence
                ),
                "product_classification_name": (
                    product.product_classification_id.name
                ),
                "product_qty": quantity,
            }
            for product, quantity in groups
        ]
        records.sort(key=lambda record: record["product_classification_sequence"])
        return records
