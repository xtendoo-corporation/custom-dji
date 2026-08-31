# Copyright 2016-2019 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    property_cost_method = fields.Selection(
        selection_add=[("last", "Last Price")],
        ondelete={"last": "set default"},
    )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # product.template.cost_method (stock_account) es un campo computado
    # cuyo valor viene de categ_id.property_cost_method, pero su propia
    # lista de selection es estática y NO hereda las opciones añadidas
    # arriba - hay que extenderla también aquí o la asignación del valor
    # 'last' calculado falla con ValueError "Wrong value for
    # product.template.cost_method" en cuanto se crea/actualiza cualquier
    # producto de una categoría con coste 'last' (detectado en el salto
    # 18->19 al cargar l10n_es/data/product_data.xml).
    cost_method = fields.Selection(
        selection_add=[("last", "Last Price")],
    )

