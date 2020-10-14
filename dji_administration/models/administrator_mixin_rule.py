# -- coding: utf-8 --

from odoo import api, models, fields


class AdministratorMixinRule(models.Model):
    _name = 'administrator.mixin.rule'

    is_commercial = fields.Boolean(
        compute='_is_commercial',
        string="Is Commercial",
        default=lambda self: self._get_default_comercial()
    )

    @api.one
    def _is_commercial(self):
        self.is_commercial = self._get_default_commercial()

    @api.model
    def _get_default_commercial(self):
        return self.env["res.users"].has_group(
                "dji_administration.commercial_group"
            )
