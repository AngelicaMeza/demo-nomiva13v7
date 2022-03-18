# -*- coding: utf-8 -*-
{
    'name': "Custom Salary Advance",

    'summary': """
        Adelanto de sueldo""",

    'description': """
        Incluir la pagina adelanto de sueldo
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
        'security/security_salary_advance.xml',
        'views/views.xml',
    ],
    
}
