# coding: utf-8


{
    "name": "Libros Fiscales para Venezuela",
    "version": "0.5",
    "depends": ['base',
                'account',
                'base_vat',
                'account_accountant',
                'l10n_ve_withholding_iva',
                'l10n_ve_account_fiscal_requirements',
                'l10n_ve_validation_res_partner',
                'l10n_ve_invoice_validation',
                'l10n_ve_location_group',
                'l10n_ve_manual_credit_note',
                ],
    "author": "IT Sales",
    "license": "AGPL-3",
    "category": "Localization",
    "website": "www.itsalescorp.com",
    "data": [
        "wizard/fiscal_book_wizard_view.xml",
        "view/adjustment_book.xml",
        "view/fiscal_book.xml",
        "report/fiscal_purchase_book_report.xml",
        "report/fiscal_book_report.xml",
        "wizard/change_invoice_sin_cred_view.xml",
        "view/account_invoice_view.xml",
        "security/ir.model.access.csv"
    ],
    "installable": True,
}





