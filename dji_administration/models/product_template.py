# -- coding: utf-8 --

from odoo import api, models, fields


class Product(models.Model):
    _inherit = 'product.template'
    _name = 'product.template'

    is_administrator = fields.Boolean(
        compute='_is_admin',
        string="Is Administrator",
        default=lambda self: self._get_default_admin()
    )

    @api.one
    def _is_admin(self):
        self.is_administrator = self.env.user.administrator

    @api.model
    def _get_default_admin(self):
        return self.env.user.administrator