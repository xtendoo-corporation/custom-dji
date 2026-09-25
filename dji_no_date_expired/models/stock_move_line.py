from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _compute_expiration_date(self):
        super()._compute_expiration_date()
        self.expiration_date = False

    def _compute_removal_date(self):
        super()._compute_removal_date()
        self.removal_date = False
