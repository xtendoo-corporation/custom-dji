# -- coding: utf-8 --
from odoo import api, models, fields,_


class SaleOrder(models.Model):
    _inherit = ['sale.order', 'administrator.mixin.rule']
    _name = 'sale.order'


    def _compute_picking_state_done(self):
        for sale in self:
            sale.is_picking_state_done = bool(sale.picking_ids.filtered(lambda p: p.state == 'done'))

    is_picking_state_done = fields.Boolean(
        compute="_compute_picking_state_done",
        readonly=True,
        multi="stock_reservation",
        store=True,
        string="Is Picking State Done",
    )
