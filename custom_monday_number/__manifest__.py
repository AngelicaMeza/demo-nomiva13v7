# -*- coding: utf-8 -*-
{
    'name': "Custom Monday Number",

    'summary': """
        Campo numero de Lunes para ser utilizado a la hora de generar el aporte SSOO.""",

    'description': """
        Campo numero de Lunes para ser utilizado a la hora de generar el aporte SSOO.
    """,

    'author': "ITSALES",
    'website': "https://www.itsalescorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll'],

    # always loaded
    'data': [
        'security/custom_monday_number_security.xml',
        'security/custom_weekend_security.xml',
        'views/views.xml',
        'views/weekend_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
