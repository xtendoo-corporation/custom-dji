# -- coding: utf-8 --

from odoo import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = ['sale.order.line', 'administrator.mixin.rule']
    _name = 'sale.order.line'

