# -*- coding: utf-8 -*-
# author: Oscar Llovera

{
    'name': "l10n_withholdings_multirate",
    'summary': """ IVA with multirate currency """,
    'author': "ITSales",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['l10n_ve_base_withholdings', 'l10n_ve_withholding_iva', 'l10n_ve_withholding_islr', 'res_currency_multirate'],
    'data': [
        'views/views.xml',
    ],
}
