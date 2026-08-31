# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#
# Fork mantenido por Xtendoo desde 2026-08-26: tomado del PR sin fusionar
# OCA/stock-logistics-workflow#2161 (rama 19.0-mig-stock_picking_mass_action
# de adhoc-dev/stock-logistics-workflow), ya que OCA todavía no ha
# aceptado la migración a 19.0. Renombrado con prefijo xtendoo_ para
# evitar colisión de nombre técnico con el módulo OCA original si se
# fusiona más adelante. Se mantiene la autoría/licencia original.
{
    "name": "Stock Picking Mass Action",
    "version": "19.0.1.0.0",
    "author": "Camptocamp, GRAP, Tecnativa, Odoo Community Association (OCA), "
    "Xtendoo",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "category": "Warehouse Management",
    "depends": ["stock_account"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/mass_action_view.xml",
        "data/ir_cron.xml",
    ],
}
