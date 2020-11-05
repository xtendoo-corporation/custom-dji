# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import timedelta, time
from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'

    picking_count = fields.Float(
        compute='_compute_picking_waiting_product_qty',
        string='Pickings'
    )

    def _compute_pickings_count(self):
        for product in self:
            product.picking_count = 0
        # self.sales_count = 0
        # if not self.user_has_groups('sales_team.group_sale_salesman'):
        #   return r
        # date_from = fields.Datetime.to_string(fields.datetime.combine(fields.datetime.now() - timedelta(days=365),
        #                                                             time.min))

        # done_states = self.env['sale.report']._get_done_states()

        # domain = [
        #   ('state', 'in', done_states),
        #  ('product_id', 'in', self.ids),
        # ('date', '>=', date_from),
        # ]
        # for group in self.env['sale.report'].read_group(domain, ['product_id', 'product_uom_qty'], ['product_id']):
        #   r[group['product_id'][0]] = group['product_uom_qty']
        # for product in self:
        #   if not product.id:
        #      product.sales_count = 0.0
        #     continue
        # product.sales_count = float_round(r.get(product.id, 0), precision_rounding=product.uom_id.rounding)
        # return r

    def _compute_picking_waiting_product_qty(self):
        domain = [
            ('state', 'in', ['waiting', 'confirmed']),
            ('product_id', 'in', self.ids),
        ]
        print("domain***************",domain)

        # StockMoveLines = self.env['stock.move.line'].search(domain)
        order_lines = self.env['stock.move.line'].read_group(domain, ['product_id', 'product_uom_qty'], ['product_id'])
        moved_data = dict([(data['product_id'][0], data['product_uom_qty']) for data in order_lines])
        for data in moved_data:
            print("data***************", data)

        for product in self:
            if not product.id:
                product.purchased_product_qty = 0.0
                continue
            product.picking_count = float_round(moved_data.get(product.id, 0),
                                                precision_rounding=product.uom_id.rounding)
