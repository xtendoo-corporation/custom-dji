{
    'name': 'DJI - Gestión de Faltas',
    'version': '19.0.1.0.1',
    'summary': 'Pasa las faltas de un presupuesto a un presupuesto FALTAS y avisa al comercial',
    'author': 'DJI',
    'category': 'Sales',
    'depends': ['sale'],
    'data': [
        'data/campos.xml',
        'data/accion_faltas.xml',
        'views/sale_order_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
