# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging



class SaleOrder(models.Model):
    _inherit = "sale.order"

    classification_ids = fields.Many2many(
        compute="_compute_sale_order_classification",
        string="Classification",
        comodel_name="product.classification",
    )

    def _compute_sale_order_classification(self):
        for so in self:
            ids = []
            for line in so.order_line:
                if not ids.count(line.product_id.product_tmpl_id.product_classification_id.id):
                    ids.append(line.product_id.product_tmpl_id.product_classification_id.id)
            so.write({'classification_ids': [(6,0,ids)]})
