# Copyright 2020 Xtendoo - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    return_lot_ids = fields.Many2many("stock.lot", compute="_compute_return_lot_ids")

    def _compute_return_lot_ids(self):
        for rec in self:
            returned_move = rec.move_id.origin_returned_move_id
            move_lots = rec.move_id.move_line_ids.lot_id
            if returned_move:
                rec.return_lot_ids = returned_move.move_line_ids.lot_id
            elif move_lots:
                rec.return_lot_ids = move_lots
            else:
                rec.return_lot_ids = self.env["stock.lot"].search(
                    [("product_id", "=", rec.product_id.id)]
                )
