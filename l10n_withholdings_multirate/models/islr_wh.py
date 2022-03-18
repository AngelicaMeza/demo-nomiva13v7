# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IslrWhDoc(models.Model):
    _inherit = 'islr.wh.doc'

    @api.model
    def converted_amount(self, line, amount):
        amount_converted = super().converted_amount(line, amount)
        if line.invoice_id.use_custom_rate():
            rate = line.invoice_id.get_custom_rate()
            amount_converted = amount / rate
        return amount_converted


class IslrWhDocInvoices(models.Model):
    _inherit = 'islr.wh.doc.invoices'

    def convert_amount_to_invoice_currency(self, amount):
        amount_converted = super().convert_amount_to_invoice_currency(amount)
        if self.invoice_id.use_custom_rate():
            rate = self.invoice_id.get_custom_rate()
            amount_converted = amount / rate
        return amount_converted

    def convert_amount_to_company_currency(self, wh_line, amount):
        amount_converted = super().convert_amount_to_company_currency(wh_line, amount)
        if wh_line.invoice_id.use_custom_rate():
            rate = wh_line.invoice_id.get_custom_rate()
            amount_converted = amount * rate
        return amount_converted


class IslrWhDocLine(models.Model):
    _inherit = 'islr.wh.doc.line'

    def convert_amount_to_invoice_currency(self, amount):
        amount_converted = super().convert_amount_to_invoice_currency(amount)
        if self.invoice_id.use_custom_rate():
            rate = self.invoice_id.get_custom_rate()
            amount_converted = amount / rate
        return amount_converted

    def convert_amount_to_company_currency(self, amount):
        amount_converted = super().convert_amount_to_company_currency(amount)
        if self.invoice_id.use_custom_rate():
            rate = self.invoice_id.get_custom_rate()
            amount_converted = amount * rate
        return amount_converted
