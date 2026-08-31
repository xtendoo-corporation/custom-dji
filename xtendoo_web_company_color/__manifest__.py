# Odoo, Open Source Web Company Color
# Copyright (C) 2019 Alexandre Díaz <dev@redneboa.es>
#
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).#
#
# Fork mantenido por Xtendoo desde 2026-08-26: tomado del PR sin fusionar
# OCA/web#3326 (rama 19.0-mig-web_company_color de HeliconiaIO/web), ya
# que OCA todavía no ha aceptado la migración a 19.0. Renombrado con
# prefijo xtendoo_ para evitar colisión de nombre técnico con el módulo
# OCA original si se fusiona más adelante. Se mantiene la autoría/licencia
# original.
{
    "name": "Web Company Color",
    "category": "web",
    "version": "19.0.1.0.0",
    "author": "Alexandre Díaz, Odoo Community Association (OCA), Xtendoo",
    "website": "https://github.com/OCA/web",
    "depends": ["web", "base_sparse_field"],
    "data": ["view/assets.xml", "view/res_company.xml"],
    "uninstall_hook": "uninstall_hook",
    "post_init_hook": "post_init_hook",
    "license": "AGPL-3",
    "auto_install": False,
    "installable": True,
}
