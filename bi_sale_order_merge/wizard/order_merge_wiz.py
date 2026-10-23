# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class SaleOrderMerge(models.TransientModel):
    _name = 'sale.order.merge'
    _description = 'Merge Sale orders'

    sale_order_to_merge = fields.Many2many(
        'sale.order', 'rel_sale_to_merge', 'sale_id', 'to_merge_id',
        string='Orders to merge')
    type = fields.Selection(
        [('new', 'New Order and Cancel Selected'), ('exist', 'New order and Delete all selected order'),
         ('exist_1', 'Merge order on existing selected order and cancel others'),
         ('exist_2', 'Merge order on existing selected order and delete others')], 'Merge Type', default='new',
        required=True)
    sale_order = fields.Many2one('sale.order', string='Merge with')
    merge_with_diff_partner = fields.Boolean(
        string='Merge with Different Customer')
    partner_id = fields.Many2one(
        'res.partner', 'Customer')

    @api.model
    def default_get(self, fields):
        rec = super(SaleOrderMerge, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        if active_ids:
            sale_ids = []
            sales = self.env['sale.order'].browse(active_ids)

            if any(sale.state == 'done' for sale in sales):
                raise UserError(_('You can not merge done orders.'))

            sale_ids = [sale.id for sale in sales]

            if 'sale_order_to_merge' in fields:
                rec.update({'sale_order_to_merge': sale_ids})
        return rec

    @api.onchange('merge_with_diff_partner')
    def set_data(self):
        if self.merge_with_diff_partner:
            self.sale_order = False
            self.type = 'new'
        elif not self.merge_with_diff_partner:
            self.partner_id = False

    def merge_sale(self):
        sale_obj = self.env['sale.order']
        line_obj = self.env['sale.order.line']
        sales = sale_obj.browse(self._context.get('active_ids', []))
        partners_list = []
        partners_list_write = []
        cancel_list = []
        customer_ref = []
        partner_name = False
        my_string = ''

        if len(sales) < 2:
            raise UserError(_('Please select multiple orders to merge in the list view.'))

        if any(sale.state in ['done', 'sale', 'confirmed', 'cancel'] for sale in sales):
            raise UserError(_('You can not merge Done and Sale order orders.'))
        for sale in sales:
            if sale.client_order_ref:
                customer_ref.append(sale.client_order_ref)
                if len(customer_ref) > 1:
                    my_string = ",".join(customer_ref)
                else:
                    my_string = customer_ref[0]

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

        if not self.merge_with_diff_partner:
            target = self.sale_order if self.type in ('exist_1', 'exist_2') else sale_obj
            partners = (sales | target).mapped('partner_id')
            if len(partners) > 1:
                raise UserError(_('You can only merge orders of same partners.'))
            if target and target.state in ['done', 'sale', 'confirmed', 'cancel']:
                raise UserError(_('You can not merge orders with Done, Cancel and Sale order orders.'))
            result = sale_obj._merge_orders(sales, self.type, target or None, customer_ref=my_string, origin=msg_origin)
        else:
            result = sale_obj._merge_orders(sales, 'new', partner=self.partner_id, customer_ref=my_string, origin=msg_origin)
        return sale_obj._merge_action(result)
