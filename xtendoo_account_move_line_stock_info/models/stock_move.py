# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    account_move_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="stock_move_id",
        copy=False,
    )

    def _get_account_move_line_vals(self):
        vals_list = super()._get_account_move_line_vals()
        for vals in vals_list:
            vals["stock_move_id"] = self.id
        return vals_list
