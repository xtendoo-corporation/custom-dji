{
    'name': 'Stock picking line expired date alert',
    'summary': """Stock picking line expired date alert""",
    'version': '13.0.1.0.0',
    'description': """Stock picking line expired date alert""",
    'author': 'Camilo',
    'company': 'Xtendoo',
    'website': 'http://xtendoo.es',
    'category': 'Admin Tools',
    'depends': [
        'base',
        'stock',
    ],
    'license': 'AGPL-3',
    'data': [
        'views/stock_picking_view.xml'
    ],
    'installable': True,
    'auto_install': True,
}

