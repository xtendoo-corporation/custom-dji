{
    'name': 'dji_administration',
    'summary': """Administration settings for DJI""",
    'version': '12.0.1.0.0',
    'description': """Administration settings for DJI""",
    'author': 'Dani Domínguez',
    'company': 'Xtendoo',
    'website': 'http://xtendoo.es',
    'category': 'Admin Tools',
    'depends': [
        'base',
        'sale',
        'product',
    ],
    'license': 'AGPL-3',
    'data': [
        'views/sale_order_views.xml',
        'security/security_group.xml',
        'views/product_views.xml'
    ],
    'installable': True,
    'auto_install': True,
}
