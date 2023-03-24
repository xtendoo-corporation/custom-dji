# -- coding: utf-8 --
import datetime

from odoo import api, models, fields, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = ['stock.picking']

    def button_validate(self):
        msgError = ""
        for line in self.move_line_ids_without_package:
            if line.lot_id and line.is_expired:
                msgError = msgError + _("Product %s with lot %s is expired.\n" %(line.product_id.name, line.lot_id.name))

        if msgError != "":
            raise UserError(_(msgError))
        res = super().button_validate()
        return res
