# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        date = datetime.now()
        for line in self.move_line_ids_without_package:
            if date > line.lot_id.life_date:
                raise UserError(
                    _("El Lote %s para el producto %s está caducado") % (line.lot_id.name, line.product_id.name)
                )
        return res
