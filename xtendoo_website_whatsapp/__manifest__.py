# Copyright 2022 Studio73 - Ioan Galan <ioan@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# Fork mantenido por Xtendoo desde 2026-08-26: tomado del PR sin fusionar
# OCA/website#1207 (rama 19.0-mig-website_whatsapp de Jarsa-dev/website),
# ya que OCA todavía no ha aceptado la migración a 19.0. Renombrado con
# prefijo xtendoo_ para evitar colisión de nombre técnico con el módulo
# OCA original si se fusiona más adelante. Se mantiene la
# autoría/licencia original.
{
    "name": "Website Whatsapp",
    "summary": "Whatsapp integration",
    "category": "Website",
    "version": "19.0.1.0.0",
    "website": "https://github.com/OCA/website",
    "author": "Studio73, Odoo Community Association (OCA), Xtendoo",
    "maintainers": ["ioans73"],
    "license": "AGPL-3",
    "depends": ["website"],
    "data": [
        "templates/website.xml",
        "views/res_config_settings.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "/xtendoo_website_whatsapp/static/src/scss/website.scss"
        ]
    },
    "installable": True,
}
