from odoo import api,fields, models, _


class ReportSaleOrderLine(models.AbstractModel):
    _name = 'report.document_format.report_saleorder_line'
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
            lazy=False,
        )
        for line in lines:
            product = self.env['product.product'].browse(line['product_id'][0])
            records.append({'product_name': product.name,
                            'product_classification_sequence': product.product_classification_id.sequence,
                            'product_classification_name': product.product_classification_id.name,
                            'product_qty': line['product_uom_qty']})
        records.sort(key=lambda x: x['product_classification_sequence'])
        return records



