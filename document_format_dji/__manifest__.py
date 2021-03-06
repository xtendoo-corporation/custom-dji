# -*- coding: utf-8 -*-

{
    "name": "DJI Document Format",
    "summary": """Formatos de documentos Distribuciones Joaquin Infante""",
    "version": "12.0.1.0.0",
    "description": """Formatos de documentos Distribuciones Joaquin Infante""",
    "author": "DDL",
    "company": "Xtendoo",
    "website": "http://www.xtendoo.es",
    "category": "Extra Tools",
    "depends": ["base", "account", "sale", "web", "stock", "stock_move_line_label"],
    "license": "AGPL-3",
    "data": [
        # Cabecera y Pie
        "views/layout/external_layout_clean.xml",
        # Ventas
        "views/sale/report_saleorder_document.xml",
        # Albarán
        "views/delivery/report_delivery_document.xml",
        # Factura
        "views/invoice/report_invoice_document.xml",
        # Etiquetas producto desde albarán
        "views/delivery_labels/report_delivery_product_label.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
