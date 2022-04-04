# -*- coding: utf-8 -*-
{
    'name': "hr_export_payroll_payments",

    'summary': """
        Generación de archivo txt para pagos masivos de nominas""",

    'description': """
        Generación de archivo txt para pagos masivos de nominas    """,

    'author': "IT Sales",
    'website': "www.itsalescorp.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Payroll',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr', 'hr_payroll', 'hr_payroll_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/export_bank_payments_views.xml',
        'data/sequence_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
