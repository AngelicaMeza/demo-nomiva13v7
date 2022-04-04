# -*- coding: utf-8 -*-
{
    'name': "hr_payslip_customization",

    'summary': """
        Personalizacion del modulo de nomina""",

    'description': """
        Personalizacion del modulo de nomina
    """,

    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Payroll',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll', 'hr_employee_customization'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
