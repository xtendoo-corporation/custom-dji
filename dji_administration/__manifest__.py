{
    'name': 'Custom DJI Administration',
    'summary': """Administration settings for DJI""",
    'version': '19.0.1.0.0',
    'description': """Administration settings for DJI""",
    'author': 'Dani Domínguez',
    'company': 'Xtendoo',
    'website': 'https://xtendoo.es',
    'category': 'Admin Tools',
    'depends': [
        'base',
        'sale',
        'purchase',
        'product',
        'website',
        'crm',
        'account',
        'stock',
        'website_sale',
        'account_banking_mandate',
        'account_payment_return',
        'account_payment_return_import',
        'account_asset_management',
        'sale_commission_oca',
        'account_invoice_margin',
        # dependencia real, no declarada hasta ahora: sale_order_views.xml
        # hereda una vista de sale_margin sin tenerlo como depends - ha
        # funcionado "por suerte" (orden de carga) hasta que en el salto
        # 18->19 un cambio de dependencias en otro sitio movió el orden y
        # dejó de cargar antes que dji_administration.
        'sale_margin',
    ],
    'license': 'AGPL-3',
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/product_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'auto_install': True,
}

