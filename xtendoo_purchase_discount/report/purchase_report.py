# Copyright 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# Copyright 2026 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools.sql import SQL


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    discount = fields.Float(string="Discount (%)", digits="Discount", aggregator="avg")

    # En Odoo 19 purchase.report._select()/_group_by() devuelven objetos SQL
    # (odoo.tools.sql.SQL), no strings, así que ya no se puede hacer
    # res.replace(...) ni res += "...". Además el core 19 ya no expone una
    # columna 'price_unit' en el informe (usa price_average agregado), así que
    # el ajuste del precio unitario por descuento que hacía la versión vieja
    # ya no aplica: aquí solo se añade la columna 'discount' para poder
    # analizar el % de descuento en el pivot de compras.
    def _select(self) -> SQL:
        return SQL("%s, l.discount as discount", super()._select())

    def _group_by(self) -> SQL:
        return SQL("%s, l.discount", super()._group_by())
