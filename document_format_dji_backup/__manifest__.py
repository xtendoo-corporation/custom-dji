# -*- coding: utf-8 -*-

{
    "name": "document_format_dji",
    "summary": """Formatos de documentos Distribuciones Joaquin Infante""",
    "version": "13.0.1.0.0",
    "description": """Formatos de documentos Distribuciones Joaquin Infante""",
    "author": "DDL",
    "company": "Xtendoo",
    "website": "http://www.xtendoo.es",
    "category": "Extra Tools",
    "depends": ["base", "account", "sale", "web", "stock"],
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": [
        "reports/report_saleorder_accumulate.xml",
        # Cabecera y Pie
        # "views/layout/external_layout_clean_dji.xml",
        # Ventas
        "views/sale/sale_order_document.xml",
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