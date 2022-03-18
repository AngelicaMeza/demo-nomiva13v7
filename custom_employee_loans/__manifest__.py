# -*- coding: utf-8 -*-
{
    'name': "Custom Employee Loans",

    'summary': """
        Cálculo de los prestamos para los empleados""",

    'description': """
        Cálculo de los prestamos para los empleados
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
        # 'security/ir.model.access.csv',
        #'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
