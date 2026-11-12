# Copyright 2020 Xtendoo - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        val = super()._prepare_stock_return_picking_line_vals_from_move(stock_move)
        if len(stock_move.move_line_ids) == 1 and stock_move.move_line_ids.lot_id:
            val["lot_id"] = stock_move.move_line_ids.lot_id.id
        # v18+ propone 0 por defecto; DJI quiere la cantidad pendiente de
        # devolver, como en v15 (mismo calculo que action_create_returns_all)
        if stock_move.state != "cancel" and stock_move.location_dest_usage != "inventory":
            quantity = stock_move.quantity
            for move in stock_move.move_dest_ids:
                if move.origin_returned_move_id == stock_move and move.state != "cancel":
                    quantity -= move.quantity
            val["quantity"] = max(stock_move.product_uom.round(quantity), 0)
        return val

    def _create_return(self):
        """Reserve the returned lot on lot-tracked moves that come from a
        single lot, so the return is ready to validate."""
        new_picking = super()._create_return()
        moves = new_picking.move_ids.filtered(
            lambda move: move.state == "assigned"
            and move.product_id.tracking == "lot"
            and len(move.origin_returned_move_id.move_line_ids) == 1
        )
        for move in moves:
            origin_line = move.origin_returned_move_id.move_line_ids
            move.move_line_ids.unlink()
            vals = move._prepare_move_line_vals(
                quantity=min(move.product_uom_qty, origin_line.quantity)
            )
            vals["lot_id"] = origin_line.lot_id.id
            self.env["stock.move.line"].create(vals)
        return new_picking


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    lot_id = fields.Many2one(comodel_name="stock.lot")
