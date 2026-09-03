from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        # create() con lista (Odoo 17+); antes con vals singular, 'expiration_date
        # in vals' comprobaba pertenencia en una LISTA (siempre False) al crear
        # varias lineas de movimiento de golpe, saltandose el limpiado en silencio.
        res = super().create(vals_list)
        for rec, vals in zip(res, vals_list):
            if 'expiration_date' in vals:
                rec._clean_expiration_date()
        return res

    @api.model
    def write(self, vals):
        res = super().write(vals)
        if 'expiration_date' in vals:
            vals.pop('expiration_date')
        return res

    def _clean_expiration_date(self):
        for record in self:
            record.expiration_date = False

    def _compute_expiration_date(self):
        super()._compute_expiration_date()
        for move_line in self:
            move_line.expiration_date = False

    # def _onchange_product_id(self):
    #     res = super()._onchange_product_id()
    #     if self.lot_id:
    #         self.expiration_date = False
    #     return res

    # def _onchange_lot_id(self):
    #     res = super()._onchange_lot_id()
    #     if self.lot_id:
    #         self.expiration_date = False
    #     return res
