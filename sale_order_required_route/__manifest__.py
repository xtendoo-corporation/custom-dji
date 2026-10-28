{
    'name': 'Sale order required route',
    'summary': """Sale order required route""",
    'version': '19.0.1.0.0',
    'description': """No permite confirmar un pedido de venta sin ruta.""",
    'author': 'Dani Domínguez',
    'company': 'Xtendoo',
    'website': 'http://xtendoo.es',
    'category': 'Admin Tools',
    'depends': [
        'sale_order_global_stock_route',
    ],
    'license': 'AGPL-3',
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
