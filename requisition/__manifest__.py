# -*- coding: utf-8 -*-
{
    'name': "Requisiciones",

    'summary': """
        Adaptaciones en el flujo de requisiciones""",

    'description': """
        Adaptaciones en el flujo de requisiciones
    """,

    'author': "ITSALES",
    'website': "http://www.itsalescorp.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'stock_landed_costs', 'purchase'],

    # always loaded
    'data': [
        'security/stock_groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/deliveryslip.xml',
        'reports/deliveryslip.xml',
    ],
}
