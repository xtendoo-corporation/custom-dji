# -*- coding: utf-8 -*-

{
    "name": "sale waiting for product",
    "summary": """Añade un smart button al producto, para acceder a un listado de pedidos que están a la espera de ese producto""",
    "version": "12.0.1.0.0",
    "description": """Añade un smart button al producto, para acceder a un listado de pedidos que están a la espera de ese producto""",
    "author": "DDL",
    "company": "Xtendoo",
    "website": "https://xtendoo.es",
    "category": "Extra Tools",
    "depends": ["base", "product","stock",],
    "license": "AGPL-3",
    "data": [
            'views/sale_order_line.xml',
            'views/product_product.xml',
            'views/product_template.xml',
    "demo": [],
    "installable": True,
    "auto_install": False,
}
