# Copyright 2023 Xtendoo (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    classification_str = fields.Char(
        compute="_compute_sale_order_classification_str",
        string="Classification",
        store="True",
    )

    @api.depends('order_line')
    def _compute_sale_order_classification_str(self):
        self.classification_str = ''
        for so in self:
            so.classification_str = ",".join(
                so.order_line.product_id.product_tmpl_id.product_classification_id.mapped('name'))
