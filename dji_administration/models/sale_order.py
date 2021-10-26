# -- coding: utf-8 --

from odoo import api, models, fields,_
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = ['sale.order', 'administrator.mixin.rule']
    _name = 'sale.order'

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for line in self.order_line:
            if line.price_unit == 0.00:
                raise ValidationError(
                    _('No puede confirmar un pedido con precio 0.00 en alguna linea'))
        return res
