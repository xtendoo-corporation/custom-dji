from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    has_overprocessed_moves = fields.Boolean(
        compute="_compute_has_overprocessed_moves"
    )

    def _get_overprocessed_moves(self):
        """Movimientos con más cantidad que la demandada."""
        self.ensure_one()
        return self.move_ids.filtered(
            lambda move: move.state not in ("draft", "cancel")
            and move.product_uom_qty
            and move.product_uom.compare(move.quantity, move.product_uom_qty) > 0
        )

    @api.depends("move_ids.quantity", "move_ids.product_uom_qty", "move_ids.state")
    def _compute_has_overprocessed_moves(self):
        for picking in self:
            picking.has_overprocessed_moves = bool(picking._get_overprocessed_moves())

    def action_update_sale_order(self):
        """Lleva a la demanda del movimiento, y a la línea del pedido de
        venta, la cantidad realmente procesada."""
        for picking in self:
            for move in picking._get_overprocessed_moves():
                line = move.sale_line_id
                if line:
                    line.product_uom_qty = move.product_uom._compute_quantity(
                        move.quantity, line.product_uom_id
                    )
                move.product_uom_qty = move.quantity
        return True
