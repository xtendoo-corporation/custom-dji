from odoo import api, fields, models
from odoo.exceptions import AccessError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _add_supplier_to_product(self):
        super()._add_supplier_to_product()
        print("_add_supplier_to_product-------------------------------------------------")
        for line in self.order_line:
            # Do not add a contact as a supplier
            print("line", line)
            print("line.product_id", line.product_id)
            print("line.product_id.name", line.product_id.name)
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            print("partner", partner)
            already_seller = (partner | self.partner_id) & line.product_id.seller_ids.mapped('name')
            print("already_seller", already_seller)
            if already_seller:
                currency = partner.property_purchase_currency_id or self.env.company.currency_id
                price = self.currency_id._convert(
                    line.price_unit, currency, line.company_id, line.date_order or fields.Date.today(), round=False)
                print("price", price)
                supplier_info = line.product_id.seller_ids.filtered(lambda x: x.name == already_seller)
                print("supplier_info", supplier_info)
                if supplier_info and supplier_info.price != price:
                    print("supplier_info.price", supplier_info.price)
                    supplier_info.price = price
