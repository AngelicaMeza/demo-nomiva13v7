# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmployeeFixedAdditionalIncome(models.Model):
    _name = 'custom_employee_fixed_additional_income'

    name = fields.Char(string='Descripción')
    amount = fields.Float(string='Monto')
    start_date = fields.Date(string='Fecha desde')
    end_date = fields.Date(string='Fecha hasta')
    contract_id = fields.Many2one(comodel_name='hr.contract')
    employe_id = fields.Many2one(comodel_name='hr.employee')

class EmployeeFixedadditionaldiscounts(models.Model):
    _name = 'custom_employee_fixed_additional_discounts'

    name = fields.Char(string='Descripción')
    amount = fields.Float(string='Monto')
    start_date = fields.Date(string='Fecha desde')
    end_date = fields.Date(string='Fecha hasta')
    contract_id = fields.Many2one(comodel_name='hr.contract')
    employe_id = fields.Many2one(comodel_name='hr.employee')

class HrContractInherit(models.Model):
    _inherit = 'hr.contract'
    
    def _compute_employee(self):
        employee_obj = self.env['hr.employee'].search([('contract_id.id', '=', self.id)])

        if employee_obj:
            # Ingresos Adicionales
            self.employee_fixed_additional_income_ids.employe_id = employee_obj.id
            self.employee_fixed_additional_income_ids.contract_id = self.id

            # Descuentos
            self.employee_fixed_additional_discounts_ids.employe_id = employee_obj.id
            self.employee_fixed_additional_discounts_ids.contract_id = self.id

        self.compute_field_income_discounts = True

    compute_field_income_discounts = fields.Boolean(compute='_compute_employee')
    employee_fixed_additional_income_ids = fields.One2many(comodel_name='custom_employee_fixed_additional_income', inverse_name='contract_id', string='Ingresos Adicionales fijos')
    employee_fixed_additional_discounts_ids = fields.One2many(comodel_name='custom_employee_fixed_additional_discounts', inverse_name='contract_id', string='Descuentos adicionales fijos')

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    def _compute_employee_additional_discounts(self):
        discounts_obj = self.env['custom_employee_fixed_additional_discounts'].search([('employe_id.id', '=', self.id)])

        if discounts_obj:
            self.employee_fixed_additional_discounts_ids += discounts_obj
        else:
            self.employee_fixed_additional_discounts_ids = False

    employee_fixed_additional_discounts_ids = fields.One2many(comodel_name='custom_employee_fixed_additional_discounts', inverse_name='employe_id', compute='_compute_employee_additional_discounts')
