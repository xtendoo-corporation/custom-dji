from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.depends('product_id', 'picking_type_use_create_lots', 'lot_id.expiration_date')
    def _compute_expiration_date(self):
        for move_line in self:
            if move_line.lot_id.expiration_date:
                move_line.expiration_date = move_line.lot_id.expiration_date
            else:
                move_line.expiration_date = False

