# -- coding: utf-8 --
import datetime

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = ['stock.picking']

    def button_validate(self):
        msg_error = ""
        for line in self.move_line_ids_without_package:
            if line.lot_id and line.is_expired:
                msg_error = msg_error + _("Product %s with lot %s is expired.\n" %(line.product_id.name, line.lot_id.name))
        if msg_error != "":
            raise UserError(_(msg_error))
        return super().button_validate()
