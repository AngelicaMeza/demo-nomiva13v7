# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountWhIvaLine(models.Model):
    _inherit = "account.wh.iva.line"
    
    def convert_amount(self, amount):
        res = super().convert_amount(amount)
        if self.invoice_id.use_custom_rate() and self.invoice_id.currency_id != self.invoice_id.company_currency_id:
            rate = self.invoice_id.get_custom_rate()
            res = amount * rate
        return res
            
        
