from odoo import models


class StockLot(models.Model):
    _inherit = "stock.lot"

    def _compute_expiration_date(self):
        super()._compute_expiration_date()
        self.expiration_date = False

    def _compute_dates(self):
        super()._compute_dates()
        for lot in self:
            lot.use_date = False
            lot.removal_date = False
            lot.alert_date = False
