# -- coding: utf-8 --

from odoo import api, models, fields,_
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name = 'product.template'

    @api.onchange('standard_price')
    def onchange_standard_price(self):
        product = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        if self.standard_price != product.standard_price:
            self._set_standard_price()


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _name = 'product.product'

    @api.onchange('standard_price')
    def onchange_standard_price(self):
        product_template = self.env['product.template'].search([('id', '=', self.id)])
        if product_template.standard_price != self.standard_price:
            product_template._set_standard_price_template()


    def _set_standard_price_template(self):
        for product in self:
            if product.product_tmpl_id:
                product.product_tmpl_id.standard_price = product.standard_price
