# -- coding: utf-8 --

from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _name = 'sale.order'

    is_administrator = fields.Boolean(
        compute='_is_admin',
        string="isAdmin",
        default=lambda self: self._get_default_admin()
    )

    @api.one
    def _is_admin(self):
        self.is_admin = self.env.user.administrator

    @api.model
    def _get_default_admin(self):
        return self.env.user.administrator
