# Copyright 2016-2019 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Xtendoo Last Price Costing Method",
    "version": "19.0.1.0.0",
    "category": "Warehouse",
    "license": "AGPL-3",
    "summary": "Add a new Costing Method 'Last Price'",
    "author": "Akretion,Odoo Community Association (OCA), Camilo",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    # OJO: depender de l10n_es aquí NO soluciona el problema de orden de
    # carga con product_data.xml (al revés: garantiza que l10n_es cargue
    # ANTES que este módulo, justo lo contrario de lo necesario) - lo
    # comprobé en el salto 18->19 y seguía fallando igual con esta
    # dependencia puesta. El campo product.category.property_cost_method
    # es company_dependent (se guarda en ir_property, no en una columna),
    # así que cualquier categoría con valor 'last' choca con CUALQUIER
    # módulo que cree/actualice productos y cargue antes que este, no solo
    # l10n_es. La solución real es operativa, no de manifest: sanear a mano
    # (UPDATE ir_property ... SET value_text='standard') los registros con
    # 'last' antes de cada --update all sobre una BD que ya tenga histórico,
    # y restaurar el valor real vía ORM (odoo shell) después de que el
    # salto termine bien - igual que se hizo en el salto 16->17 (91
    # categorías entonces, mismas 91 en 18->19).
    "depends": ["stock", "stock_account", "purchase"],
    "data": [
       "views/product.xml",
    ],
    "installable": True,
}
