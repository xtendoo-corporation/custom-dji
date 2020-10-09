# -- coding: utf-8 --

from odoo import api, models, fields


class AdministratorMixinRule(models.Model):
    _name = 'administrator.mixin.rule'

    is_comercial = fields.Boolean(
        compute='_is_comercial',
        string="Is Comercial",
        default=lambda self: self._get_default_comercial()
    )

    @api.one
    def _is_comercial(self):
        self.is_comercial = self.env["res.users"].has_group(
                "dji_administration.comercial_group"
            )

    @api.model
    def _get_default_comercial(self):
        return self.env["res.users"].has_group(
                "dji_administration.comercial_group"
            )
