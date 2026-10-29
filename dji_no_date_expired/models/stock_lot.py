from odoo import models


class StockLot(models.Model):
    _inherit = "stock.lot"

    def _compute_expiration_date(self):
        # La fecha de caducidad solo la pone el usuario: ni se pone a False
        # al recalcular ni se rellena sola con "hoy + vida util".
        for lot in self:
            lot.expiration_date = lot.expiration_date or False

    def _compute_dates(self):
        # Se conserva expiration_date, pero se anulan el resto de fechas:
        # removal_date es la que resta stock disponible del core.
        super()._compute_dates()
        for lot in self:
            lot.use_date = False
            lot.removal_date = False
            lot.alert_date = False
