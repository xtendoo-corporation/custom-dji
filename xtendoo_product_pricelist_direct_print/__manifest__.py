# Copyright 2017 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - João Marques
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
#
# Fork mantenido por Xtendoo desde 2026-08-26: tomado del PR sin fusionar
# OCA/product-attribute#2220 (rama 19.0-mig-product_pricelist_direct_print
# de Studio73/product-attribute), ya que OCA todavía no ha aceptado la
# migración a 19.0. Renombrado con prefijo xtendoo_ para evitar colisión
# de nombre técnico con el módulo OCA original si se fusiona más
# adelante. Se mantiene la autoría/licencia original.
{
    "name": "Product Pricelist Direct Print",
    "summary": "Print price list from menu option, product templates, "
    "products variants or price lists",
    "version": "19.0.1.0.0",
    "category": "Product",
    "website": "https://github.com/OCA/product-attribute",
    "author": "Tecnativa, GRAP, Odoo Community Association (OCA), Xtendoo",
    "maintainers": ["legalsylvain"],
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "reports/report_product_pricelist.xml",
        "data/mail_template_data.xml",
        "wizards/product_pricelist_print_view.xml",
    ],
}
