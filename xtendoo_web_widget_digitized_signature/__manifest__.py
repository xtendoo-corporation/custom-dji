# Origen: OCA/web web_widget_digitized_signature (Serpent Consulting Services, Agile Business Group,
# Tecnativa), adaptado por Xtendoo a stock.picking. Para Odoo 19 se usa el widget "signature" del core
# en lugar de la librería jSignature; los datos de 13 (adjuntos de digital_signature) se leen igual.
{
    "name": "Xtendoo Web Widget Digitized Signature",
    "version": "19.0.1.0.0",
    "summary": "Firma del receptor en el albarán (firma, nombre y NIF) y firma del usuario",
    "author": "Xtendoo, Serpent Consulting Services Pvt. Ltd., Agile Business Group, "
    "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/xtendoo-corporation/custom-dji",
    "license": "AGPL-3",
    "category": "Web",
    "depends": ["web", "mail", "stock"],
    "data": [
        "views/res_users_view.xml",
        "views/stock_picking_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
