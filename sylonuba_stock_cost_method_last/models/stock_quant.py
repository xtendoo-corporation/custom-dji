# Copyright 2026 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    # stock.quant.cost_method (stock_account) es un campo computado desde
    # product_categ_id.property_cost_method con su propia lista de
    # selection estatica, igual que product.template.cost_method (ver
    # models/product.py) - sin extenderla aqui tambien, el ORM revienta con
    # ValueError "Wrong value for stock.quant.cost_method: 'last'" en
    # cuanto se lee un quant de una categoria con coste 'last' (por
    # ejemplo desde el boton inteligente 'En mano' de un producto).
    cost_method = fields.Selection(
        selection_add=[("last", "Last Price")],
    )
