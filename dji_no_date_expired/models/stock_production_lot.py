from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    @api.model_create_multi
    def create(self, vals_list):
        # create() con lista (Odoo 17+); antes con vals singular, 'expiration_date
        # in vals' comprobaba pertenencia en una LISTA (siempre False) al crear
        # varios lotes de golpe, saltandose el limpiado en silencio.
        res = super().create(vals_list)
        for rec, vals in zip(res, vals_list):
            if 'expiration_date' in vals:
                rec._clean_expiration_date()
        return res

    def _clean_expiration_date(self):
        for record in self:
            record.expiration_date = False

    def _get_dates(self, product_id=None):
        res = super()._get_dates(product_id)
        if 'expiration_date' in res:
            res.pop('expiration_date')
        return res
