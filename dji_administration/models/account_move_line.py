# Copyright 2023 Xtendoo (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).from odoo import api, models, fields
from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = ['account.move.line', 'administrator.mixin.rule']
    _name = 'account.move.line'


