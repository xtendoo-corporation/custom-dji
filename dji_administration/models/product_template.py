# Copyright 2023 Xtendoo (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).from odoo import api, models, fields
from odoo import api, models, fields


class Product(models.Model):
    _inherit = ['product.template', 'administrator.mixin.rule']
    _name = 'product.template'
