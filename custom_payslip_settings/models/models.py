# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Campos de ajustes globales para el modulo de nomina
    minimum_salary = fields.Float(related='company_id.minimum_salary', string='Salario mínimo',readonly=False)
    holidays = fields.Float(related='company_id.holidays', string='Días de vacaciones', readonly=False)
    profit_days = fields.Float(related='company_id.profit_days', string='Días de utilidades', readonly=False)
    salary_basket_ticket = fields.Float(related='company_id.salary_basket_ticket', string='Salario Cesta Ticket', readonly=False)
    central_bank_social_benefits_rate = fields.Float(related='company_id.central_bank_social_benefits_rate', string='Tasa prestaciones sociales Banco Central', readonly=False)

class Company(models.Model):
    _inherit = 'res.company'

    minimum_salary = fields.Float(string='Salario mínimo', default=0)
    holidays = fields.Float(string='Días de vacaciones', default=0)
    profit_days = fields.Float(string='Días de utilidades', default=0)
    salary_basket_ticket = fields.Float(string='Salario Cesta Ticket', default=0)
    central_bank_social_benefits_rate = fields.Float(string='Tasa prestaciones sociales Banco Central', default=0)