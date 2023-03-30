# Copyright 2023 Xtendoo (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).from odoo import api, models, fields
from odoo import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = ['sale.order.line', 'administrator.mixin.rule']
    _name = 'sale.order.line'

