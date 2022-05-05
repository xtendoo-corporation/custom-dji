# -- coding: utf-8 --

from odoo import api, models, fields,_
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _name = 'sale.order'

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for sale in self.filtered(lambda s: s.state != 'draft'):
            if sale.order_line.filtered(lambda l: l.price_unit == 0.00 and l.product_id):
                raise ValidationError(
                    _('No puede confirmar un pedido con precio 0.00 en alguna linea'))
        return res

    def _write(self, value):
        for sale in self.filtered(lambda s: s.state != 'draft'):
            if sale.order_line.filtered(lambda l: l.price_unit == 0.00 and l.product_id):
                print("sale order line", sale.order_line.order_id)
                raise UserError(
                    _('No puede guardar un pedido con precio 0.00 en alguna linea'))
        return super(SaleOrder, self)._write(value)
