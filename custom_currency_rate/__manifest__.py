# -*- coding: utf-8 -*-
{
    'name': "Custom Currency Rate",

    'summary': """
        Tasa personalizada en el modulo de nomina""",

    'description': """
        Tasa personalizada en el modulo de nomina
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
        'security/custom_currency_rate.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
