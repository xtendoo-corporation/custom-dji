# -- coding: utf-8 --
import datetime

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = ['stock.move.line']

    is_expired = fields.Boolean('Is expired', default=False, compute="_compute_is_expired")

    @api.depends('lot_id')
    def _compute_is_expired(self):
        for line in self:
            if line.lot_id and line.lot_id.expiration_date:
                line.is_expired = line.lot_id.expiration_date < datetime.datetime.now()
            else:
                line.is_expired = False
