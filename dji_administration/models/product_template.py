# -- coding: utf-8 --

from odoo import api, models, fields


class Product(models.Model):
    _inherit = ['product.template', 'administrator.mixin.rule']
    _name = 'product.template'
