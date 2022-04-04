# -*- coding: utf-8 -*-
{
    'name': "Custom Employee",

    'summary': """
        Personalización del módulo de empleados""",

    'description': """
        Personalización del módulo de empleados
    """,

    'author': "IT Sales",
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
        'views/views.xml',
        'views/custom_contract_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
