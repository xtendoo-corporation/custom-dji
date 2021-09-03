# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import logging



class SaleOrder(models.Model):
    _inherit = "sale.order"

    classification_ids = fields.Char(
        compute="_compute_sale_order_classification",
        string="Classification",
        store = "True"
    )

    def _compute_sale_order_classification(self):
        for so in self:
            ids = ''
            for line in so.order_line.filtered(lambda l: l.product_id.product_tmpl_id.product_classification_id.id != False):
                print(line.product_id.product_tmpl_id.product_classification_id)
                if ids.find(line.product_id.product_tmpl_id.product_classification_id.name) < 0:
                    if ids != '':
                        ids += ', '
                    ids +=line.product_id.product_tmpl_id.product_classification_id.name
            so.classification_ids = ids
