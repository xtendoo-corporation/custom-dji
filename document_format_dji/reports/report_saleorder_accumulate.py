from odoo import api,fields, models, _


class ReportSaleOrderLine(models.AbstractModel):
    _name = 'report.document_format_dji.report_saleorder_line'
    _description = 'Report Quotations Products Accumulate'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'docids': docids,
            'get_saleorder_lines': self.get_saleorder_lines,
        }

    @api.model
    def get_saleorder_lines(self, docids):
        records = []
        lines = self.env['sale.order.line'].read_group(
            [('order_id', 'in', docids)],
            ['product_id', 'product_uom_qty'],
            ['product_id'],
            lazy=False
        )
        for line in lines:
            product = self.env['product.product'].browse(line['product_id'][0])
            records.append({'product_name': product.name, 'product_qty': line['product_uom_qty']})
        return records


