# Copyright 2023 Xtendoo (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).from odoo import api, models, fields
from odoo import api, models, fields,_


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self, vals):
        print("*" * 50)
        if vals.get('pricelist_id'):
            if self.is_commercial:
                print("Es comercial")
            if vals.get('pricelist_id') != self.partner_id.property_product_pricelist.id:
                print("No es el mismo pricelist")
                vals['pricelist_id'] = self.partner_id.property_product_pricelist.id
        print("es comercial", self.is_commercial)
        print("es admin", self.is_admin)
        print("*"*50)
        return super(SaleOrder, self).write(vals)
