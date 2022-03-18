# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta

class CustomCurrencyRate(models.Model):
    _name = 'custom_currency_rate'

    name = fields.Float(string='Tasa')
    rate_date = fields.Date(string='Fecha')
    description = fields.Char(string='Descripción')

    def name_get(self):
        result = []
        msg = ' '
        for record in self:
            if record.name and record.rate_date:
                msg = str(record.name) + ' / ' + str(fields.Date.from_string(record.rate_date))
            elif not record.rate_date:
                msg = str(record.name)
            
            result.append((record.id, msg))
            msg = ' '
        return result

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    custom_currency_id = fields.Many2one(comodel_name='custom_currency_rate',string='Tasa personalizada')

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    custom_currency_id = fields.Many2one(comodel_name='custom_currency_rate',string='Tasa personalizada')