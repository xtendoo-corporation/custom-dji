# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import copy


class MergeSameCustomerSaleOrder(models.TransientModel):
    _name = 'merge.same.customer.sale.order.wizard'
    _description = 'Merge Same Customer Sale orders'

    partner_id = fields.Many2one('res.partner', string='Customer')
    sale_order = fields.Many2one(
        'sale.order', 'Merge into')
    sale_order_to_merge = fields.Many2many(
        'sale.order',
        string='Orders to merge')
    type = fields.Selection(
        [('new', 'New Order and Cancel Selected'), ('exist', 'New order and Delete all selected order'),
         ('exist_1', 'Merge order on existing selected order and cancel others'),
         ('exist_2', 'Merge order on existing selected order and delete others')], 'Merge Type', default='new',
        required=True)

    @api.onchange('partner_id')
    def update_so_list(self):
        if self.partner_id:
            orders = self.env['sale.order'].search([('partner_id','=',self.partner_id.id),('state','=', 'draft')])
            self.sale_order_to_merge = orders

    @api.onchange('sale_order_to_merge')
    def update_so_value(self):
        if self.partner_id:
            self.sale_order = False



    def merge_same_customer_sale_orders(self):
        sale_obj = self.env['sale.order']
        mod_obj = self.env['ir.model.data']
        line_obj = self.env['sale.order.line']
        sales = sale_obj.browse(self.sale_order_to_merge.ids)
        partners_list = []
        partners_list_write = []
        line_list = []
        cancel_list = []
        copy_list = []
        vals = {}
        customer_ref = []
        partner_name = False
        myString = ''
        new_sale = False
        if len(sales) < 2:
            raise UserError(_('Please select multiple orders to merge in the list view.'))

        if any(sale.state in ['done', 'sale', 'confirmed', 'cancel'] for sale in sales):
            raise UserError(_('You can not merge Done and Sale order orders.'))
        for sale in sales:
            if sale.client_order_ref:
                customer_ref.append(sale.client_order_ref)
                if len(customer_ref) > 1:
                    myString = ",".join(customer_ref)
                else:
                    myString = customer_ref[0]

        msg_origin = ""
        origin_list = []

        for sale in sales:
            origin_list.append(sale.name)
        if self.sale_order:
            origin_list.append(self.sale_order.name)

        if len(origin_list) == 1:
            msg_origin = msg_origin + origin_list[0] + "."
        elif len(origin_list) > 1:
            msg_origin = ', '.join(set(origin_list))

        target = self.sale_order if self.type in ('exist_1', 'exist_2') else sale_obj
        partners = (sales | target).mapped('partner_id')
        if len(partners) > 1:
            raise UserError(_('You can only merge orders of same partners.'))
        if target and target.state in ['done', 'sale', 'confirmed', 'cancel']:
            raise UserError(_('You can not merge orders with Done, Cancel and Sale order orders.'))
        result = sale_obj._merge_orders(sales, self.type, target or None, customer_ref=myString, origin=msg_origin)
        return sale_obj._merge_action(result)
