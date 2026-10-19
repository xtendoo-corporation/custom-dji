# Copyright 2021 Manuel Calero - Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self, vals):
        change = False
        for line in self.order_line:
            if vals.get('order_line'):
                for line_vals in vals.get('order_line'):
                    # Los comandos 2, 3 y 4 llegan con solo 2 elementos
                    if (
                        len(line_vals) > 2
                        and line_vals[0] == 1
                        and line_vals[1] == line.id
                        and line_vals[2]
                        and line_vals[2].get('price_unit')
                    ):
                        change = line._compute_is_pricelist_change_line(line_vals[2].get('price_unit'))
        vals['is_price_list_change'] = change
        res = super(SaleOrder, self).write(vals)
        return res
    def _action_confirm(self):
        result = ""
        for line in self.order_line:
            if line.compute_price_unit_is_valid():
                result += line.compute_price_unit_is_valid()
        if result:
            raise UserError(result)
        return super(SaleOrder, self)._action_confirm()


    def action_update_in_pricelist(self):
        for line in self.order_line:
            line.action_update_pricelist()
        self.is_price_list_change = False

    is_price_list_change = fields.Boolean(
        "The pricelist has changed",
    )

    @api.onchange('order_line')
    def onchange_order_line(self):
        self.is_price_list_change = False
        for line in self.order_line:
            if line.is_pricelist_change:
                self.is_price_list_change = True
                break
        return




