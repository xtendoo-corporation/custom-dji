{
    "name": "Sale line stock warning custom",
    "summary": """sale line stock warning custom para dji""",
    "version": "15.0.1.0.0",
    "description": """sale line stock warning custom para dji""",
    "author": "Daniel Dominguez",
    "company": "Xtendoo",
    "website": "http://xtendoo.es",
    "category": "Extra Tools",
    "license": "AGPL-3",
    "depends": [
        "sale_stock",
    ],
    "data": [
    ],
    'assets': {
        'web.assets_qweb':[
            'sale_line_stock_warning_custom/static/src/xml/qty_at_date.xml',
        ],
    },
    "installable": True,
    "auto_install": False,
}
