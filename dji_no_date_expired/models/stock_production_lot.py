from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if 'expiration_date' in vals:
            res._clean_expiration_date()
        return res

    def _clean_expiration_date(self):
        for record in self:
            record.expiration_date = False

    def _get_dates(self, product_id=None):
        res = super()._get_dates(product_id)
        if 'expiration_date' in res:
            res.pop('expiration_date')
        return res
