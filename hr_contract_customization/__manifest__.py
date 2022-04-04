# -*- coding: utf-8 -*-
{
    'name': "hr_contract_customization",

    'summary': """
        Personalizacion del modulo contrato""",

    'description': """
        Personalizacion del modulo contrato, agrega campos y
        metodos para el calculo de Prestaciones sociales, utilidades,
        prestaciones, anticipo de vacaciones.
    """,

    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Payroll',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract', 'hr_payroll', 'hr_employee_customization'],

    # always loaded
    'data': [
        'data/social_benefits.xml',
        'data/update_advances_button.xml',
        'views/views.xml',
    ],
    'license': 'LGPL-3',
}
