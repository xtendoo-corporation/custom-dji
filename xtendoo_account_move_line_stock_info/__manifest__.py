# © 2016 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Fork mantenido por Xtendoo desde 2026-08-26: tomado del PR sin fusionar
# OCA/stock-logistics-warehouse#2549 (rama
# 19.0-mig-account_move_line_stock_info de
# collinskipkorir/stock-logistics-warehouse), ya que OCA todavía no ha
# aceptado la migración a 19.0. Renombrado con prefijo xtendoo_ para
# evitar colisión de nombre técnico con el módulo OCA original si se
# fusiona más adelante. Se mantiene la autoría/licencia original.
{
    "name": "Account Move Line Stock Info",
    "version": "19.0.1.0.0",
    "depends": ["stock_account"],
    "author": "ForgeFlow, Odoo Community Association (OCA), Xtendoo",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "category": "Warehouse Management",
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_line_view.xml",
        "views/stock_move_view.xml",
    ],
}
