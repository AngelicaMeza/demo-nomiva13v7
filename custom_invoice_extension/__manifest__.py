# -*- coding: utf-8 -*-
{
    'name': "custom invoice extension",

    'summary': """
        Personalización de la factura de cliente""",

    'description': """
        Personalización de la factura de cliente
    """,

    'author': "ITSALES",
    'website': "http://www.itsalescorp.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/report_invoice_extends.xml',
        'views/invoice_debit_note.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
