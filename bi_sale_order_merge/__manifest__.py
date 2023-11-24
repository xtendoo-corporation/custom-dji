# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Merge Sales Orders in Odoo',
    'version': '15.0.1.0',
    'category': 'Sales',
    'summary': 'Merge sale order merge sales order merge purchase order merge multiple sales order merge multiple purchase order merge mass sales order merge mass purchase order merger sale merger purchase merge Delivery order merge picking merge SO merge PO',
    'description': """
Fusionar pedido de cliente, fusionar órdenes de compra, fusionar orden, fusionar datos,
""",
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    "price": 19,
    "currency": 'EUR',
    'depends': ['base','sale_management','product'],
    'data': [
        'views/order_merge_view.xml',
        'views/sale_order.xml',
        'views/sale_order_line_merge.xml',
        'views/res_config_settings.xml',
        'wizard/merge_same_customer_so_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "live_test_url":'https://youtu.be/JGH4PJvUNjo',
    "images":["static/description/Banner.png"],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
