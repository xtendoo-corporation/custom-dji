from odoo import api, fields, models
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _add_supplier_to_product(self):
        super()._add_supplier_to_product()
        for line in self.order_line:
            # Do not add a contact as a supplier
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            already_seller = (partner | self.partner_id) & line.product_id.seller_ids.mapped('partner_id')
            if already_seller:
                currency = partner.property_purchase_currency_id or self.env.company.currency_id
                price = self.currency_id._convert(
                    line.price_unit, currency, line.company_id, line.date_order or fields.Date.today(), round=False)
                supplier_info = line.product_id.seller_ids.filtered(lambda x: x.partner_id == already_seller)
                if supplier_info and supplier_info.price != price:
                    supplier_info.price = price
