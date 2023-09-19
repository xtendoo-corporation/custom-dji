# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Merge Sales Orders in Odoo',
    'version': '14.0.0.6',
    'category': 'Sales',
    'summary': 'Merge sale order merge sales order merge purchase order merge multiple sales order merge multiple purchase order merge mass sales order merge mass purchase order merger sale merger purchase merge Delivery order merge picking merge SO merge PO',
    'description': """
    Merge sales order, merge purchase orders, merge order, merge data,
    Sales Order Merge,
    Purchase Order Merge, Merge Sale Order, Merge purchases Order
    sale order merger
    sales order merger
    merger sales order
    merge quotation
    quotation merger
    merge SO
    so merge
    sale order merge

    merge quotation orders
Fusionar pedido de cliente, fusionar órdenes de compra, fusionar orden, fusionar datos,
     Combinación de órdenes de venta,
     Combinación de orden de compra, Orden de venta de combinación, Compra de fusión Orden
     fusión de orden de venta
     fusión de orden de ventas
     orden de venta de fusión
     fusionar cita
     fusión de cotizaciones
     fusionar órdenes de cotización

دمج أمر المبيعات ، ودمج أوامر الشراء ، ودمج الطلب ، ودمج البيانات ، دمج طلب المبيعات ، دمج طلب الشراء ، طلب دمج مدمج ، دمج طلب الشراء طلب اندماج اندماج أمر المبيعات طلب اندماج المبيعات دمج الاقتباس الاندماج الاقتباس دمج أوامر الاقتباس

Fusionner une commande client, fusionner des commandes, fusionner une commande, fusionner des données,
     Fusion des commandes client,
     Fusionner les commandes, Fusionner les commandes, Fusionner les commandes
     fusion d'ordre de vente
     fusion d'ordres de vente
     ordre de vente de fusion
     fusionner la citation
     fusion de devis
     fusionner les commandes de devis
Mesclar ordem do cliente, mesclar ordens de compra, ordem de mesclagem, mesclar dados,
     Sales Merge Order,
     Ordem de Compra Merge, Merge Sale Order, Mesclar compras Order
     fusão de pedidos de venda
     fusão de pedidos de venda
     ordem de venda da fusão
     cotação de mesclagem
     fusão de cotação
     ordens de cotação de mesclagem

    odoo Merge sales order merge purchase orders merge order merge data mix order make together
    Odoo Sales Order Merge Purchase Order Merge Merge Sale Order Merge purchases Order
    odoo merge orders merge so po merge po so merge orders merge
    odoo merging orders odoo orders merging
    Odoo Combine Invoices combine sales order combine purchase orders combine sales combine purchase combine orders
    Odoo Combine orders mix orders Combine po combine so

odoo Merge Picking list Merge Delivery Orders Merge Incoming shipments Merge Receipts Merge orders Merge
    odoo merge Delivery Orders/Incoming Shipments in odoo merge shipment merge pickings merge combine orders
    odoo combine picking order combine delivery order combine combine incoming shipment combine
    odoo merge transfer merge shipment delivery merger shipment merger picking merger
    odoo merge operations merge internal transfer in odoo
    odoo merge DO receipt merger merge multiple picking merge multiple delivery merge multiple shipment
    odoo merge warhouse picking merge stock picking merge stock movement
    odoo merge stock picking merge stock picking merger stock picking combine stock picking combine
    odoo merge stock operation merge stock operation merger stock operation combine stock operation combine
    odoo merge operations merge operations merger operations combine operations combine merge DO merge
    odoo merge delivery order merge delivery order merger delivery order combine delivery order combine
    odoo merge receipt merge receipt merger receipt combine receipt combine
    odoo merge picking merge picking merger picking combine picking combine
Fusionner la liste de prélèvement, fusionner les commandes de livraison, fusionner les envois entrants, fusionner les reçus. Fusionner les commandesfusionner le transfert, fusionner l'expédition, fusionner les livraisons, fusionner les expéditions, choisir la fusion, fusionner les opérations, fusionner le transfert internefusionner DO, réception fusion, fusionner plusieurs picking, fusionner plusieurs livraisons, fusionner plusieurs envois, fusionner picking warhouse, fusionner picking stock, fusionner stock mouvement

Combinar lista de picking, fusionar pedidos de entrega, combinar envíos entrantes, combinar recibos. Fusionar pedidos
fusión de transferencia, combinación de envío, fusión de entrega, fusión de envío, fusión de picking, fusión de operaciones, combinación de transferencia interna
fusionar DO, fusionar recibos, fusionar selección múltiple, fusionar entregas múltiples, fusionar envíos múltiples, fusionar picking de warhouse, combinar stock picking, fusionar stock de movimientos


odoo Merge purchase list Merge sale Orders Merge sales order Merge purchase Merge purchase orders Merge
    odoo merge sale order in odoo merge purchase merge purchases merge combine orders
    odoo combine purchases order combine sale order combine PO combine purchase order combine
    odoo merges sale order merger purchase order merger sale merger purchase merger
    odoo merge purchase picking merge sale transfer in odoo
    odoo merge SO receipt merger merge multiple Sales merge multiple purchase merge multiple orders
    odoo merge Sales process merge purchase process merge Sale purchase merge
    odoo merge Sales order merge purchase order merger sale purchase combine order sale combine
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
