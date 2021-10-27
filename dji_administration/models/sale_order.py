# -- coding: utf-8 --

from odoo import api, models, fields,_
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = ['sale.order', 'administrator.mixin.rule']
    _name = 'sale.order'

