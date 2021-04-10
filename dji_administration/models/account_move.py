# -- coding: utf-8 --

from odoo import api, models, fields


class AccountMove(models.Model):
    _inherit = ['account.move', 'administrator.mixin.rule']
    _name = 'account.move'


