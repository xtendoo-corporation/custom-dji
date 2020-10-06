{
    'name': 'DJI Administration',
    'summary': """Administration settings for DJI""",
    'version': '12.0.1.0.0',
    'description': """Administration settings for DJI""",
    'author': 'Manuel Calero, Javier Lagares',
    'company': 'Xtendoo',
    'website': 'http://www.xtendoo.es',
    'category': 'Admin Tools',
    'depends': [
        'base',
        'sale',
    ],
    'license': 'AGPL-3',
    'data': [
        'views/sale_order_views.xml',
        'views/user_views.xml',
    ],
    'installable': True,
    'auto_install': True,
}
