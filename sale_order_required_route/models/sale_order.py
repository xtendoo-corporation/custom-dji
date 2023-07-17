# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for sale in self:
            if not sale.route_id:
                raise ValidationError(
                    _('Debe seleccionar una ruta'))
        return res
