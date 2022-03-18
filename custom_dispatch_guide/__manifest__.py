{
    'name': 'Guia de Despacho',
    'version': '0.1',
    'depends': ['stock', 'account', 'sale_management'],
    'license': 'AGPL-3',
    'author': 'IT Sales',
    "website": "www.itsalescorp.com",

    'category': 'stock',
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/dispatch_guide_driver_view.xml',
        'views/dispatch_guide_views.xml',
        'wizard/add_dispatch_lines.xml',
        'report/dispatch_guide_report.xml'
    ],
}
