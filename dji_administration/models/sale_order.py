# -- coding: utf-8 --

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = ['sale.order', 'administrator.mixin.rule']
    _name = 'sale.order'
