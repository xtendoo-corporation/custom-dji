# Copyright 2016-2019 Akretion (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        # En Odoo 19 ya no existe product_price_update_before_done: el valor
        # de los movimientos entrantes se calcula en _action_done (_set_value)
        # y el coste estándar se recalcula allí para los métodos no estándar.
        # Se fija el último precio de compra después de ese recálculo.
        moves = super()._action_done(cancel_backorder=cancel_backorder)
        moves._update_standard_price_last()
        return moves

    def _update_standard_price_last(self):
        moves = self.filtered(
            lambda move: move.state == "done"
            and move.is_in
            and move.location_id.usage == "supplier"
            and move.product_id.cost_method == "last"
        )
        for move in moves.sorted("id"):
            if not move._get_valued_qty():
                continue
            move.product_id.with_company(move.company_id).sudo().with_context(
                disable_auto_revaluation=True
            ).write({"standard_price": move._get_price_unit()})
