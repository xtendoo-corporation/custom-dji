# Copyright 2026 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# En 19.0 el modulo OCA sale_order_line_price_history cambio respecto a
# 15.0: icono fa-history en vez del reloj (fa-clock-o), columna junto al
# precio en vez de al final de la linea, y se oculta en cuanto la linea
# tiene algo facturado. DJI lo quiere exactamente como en 15.0.
{
    "name": "DJI Sale Price History (como v15)",
    "summary": "Reloj del historial de precios de venta como en 15.0",
    "version": "19.0.1.0.0",
    "category": "Sales Management",
    "author": "Xtendoo",
    "license": "AGPL-3",
    "depends": ["sale_order_line_price_history"],
    "data": ["views/sale_order_views.xml"],
    "assets": {
        "web.assets_backend": [
            "dji_sale_price_history_v15/static/src/xml/price_history_widget.xml",
        ],
    },
    "installable": True,
}
