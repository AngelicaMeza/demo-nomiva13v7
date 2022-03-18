# -*- coding: utf-8 -*-
{
    'name': "Custom Employee Fixed Additional Income",

    'summary': """
        Ingresos adicionales fijos""",

    'description': """
        Ingresos adicionales fijos del empleado
    """,

    'author': "ITSALES",
    'website': "https://www.itsalescorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr', 'hr_contract', 'hr_payroll'],

    # always loaded
    'data': [
        'security/employee_fixed_additional_income_security.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
