# encoding: UTF-8

{
    'name': 'Gestiona IGFT %',
    'version':'1.0',
    'author': 'IT Sales',
    "license": "AGPL-3",
    "category": "Localization",
    "website": "www.itsalescorp.com",
    'summary':'Automatic ITF Withhold',
    'description': '''\
Calculate automatic itf withholding
===========================

V13
Calculate automatic itf withholding
''',
    #data, es una lista donde se agregan todas las vistas del módulo, es decir los archivos.xml y archivos.csv.
    'data': [

             'view/res_company_view.xml',

            ],
    #depends,  es una lista donde se agregan los módulos que deberían estar instalados (Módulos dependencia) para que el modulo pueda ser instalado en Odoo.
    'depends': ['base','account'],
    'js': [],
    'css': [],
    'qweb' : [],
    #'installable': True,
    #'auto_install': False,
    'application': True,
}
