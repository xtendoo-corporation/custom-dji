from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        msg_error = ""
        for line in self.move_line_ids:
            if line.lot_id and line.is_expired:
                msg_error += _(
                    "Product %(product)s with lot %(lot)s is expired.\n",
                    product=line.product_id.name,
                    lot=line.lot_id.name,
                )
        if msg_error:
            raise UserError(msg_error)
        return super().button_validate()
