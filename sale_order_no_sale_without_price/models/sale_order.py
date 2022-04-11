# -- coding: utf-8 --

from odoo import api, models, fields,_
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _name = 'sale.order'

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for line in self.order_line:
            if line.price_unit == 0.00 and line.product_id and self.state != 'draft':
                raise ValidationError(
                    _('No puede confirmar un pedido con precio 0.00 en alguna linea'))
        return res

    def _write(self, value):
        for line in self.order_line:
            if line.price_unit == 0.00 and line.product_id and self.state != 'draft':
                raise ValidationError(
                    _('No puede guardar un pedido con precio 0.00 en alguna linea'))
        return super(SaleOrder, self)._write(value)
