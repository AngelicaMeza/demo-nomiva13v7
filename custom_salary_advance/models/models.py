# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class CustomSalaryAdvance(models.Model):
    _name = 'custom_salary_advance'
    
    name = fields.Many2one(comodel_name='hr.employee',string='Empleado')
    employee_payslip_id = fields.Many2one(comodel_name='hr.payslip')
    employee_contract_id = fields.Many2one(comodel_name='hr.contract')
    advance_mode = fields.Selection([('1', 'Empleado'),('2','Departamento'),('3','Compañía')], string="Tipo de anticipo")
    department_id = fields.Many2one(comodel_name='hr.department', string='Departamento')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Moneda')
    company_id = fields.Many2one(comodel_name='res.company', string='Compañía')
    credit_account_id = fields.Many2one(comodel_name='res.partner.bank', string='Cuenta de crédito')
    debit_account_id = fields.Many2one(comodel_name='res.partner.bank', string='Cuenta de débito')
    account_jornal_id = fields.Many2one(comodel_name='account.journal', string='Diario')
    date = fields.Date(string='Fecha')
    reason = fields.Selection([('1', 'Anticipo de prestaciones sociales'),('2','Anticipo de utilidades'),('3','Anticipo de sueldo'), ('4','Anticipo de vacaciones')], string='Razón')
    advancement = fields.Float(string='Monto')

    @api.onchange('name', 'department_id')
    def onchange_advance_mode(self):
        if self.advance_mode == '1':
            #Buscando el departamento y la companhia del empleado
            employee_obj = self.env['hr.employee'].search([('name', '=', self.name.name)])
            self.department_id = employee_obj.department_id.id
            self.company_id = employee_obj.company_id.id
        elif self.advance_mode == '2':
            #Buscando la companhia a la que pertenece del departamento
            department_obj = self.env['hr.department'].search([('name', '=', self.department_id.name)])
            self.company_id = department_obj.company_id.id
    
    @api.constrains('advancement')
    def onchange_advancement(self):
        # Buscando el monto de las utilidades para el trabajador
        employee_obj = self.env['hr.contract'].search([('employee_id.id', '=', self.name.id)])
        result = False
        
        # Validacion de anticipos de utilidades
        if self.advance_mode == '1' and self.reason == '2':
            if employee_obj:
                # Hay un anticipo previo
                if employee_obj.employee_result_profit:
                    aux_amount = employee_obj.employee_result_profit
                else: # Se valida de acuerdo al monto: (TA) * (0.33)
                    aux_amount = employee_obj.employee_profit
                #El monto ingresado es mayor las utilidades disponibles?
                result = True if self.advancement > round(aux_amount,2) else False

        if result:
            raise ValidationError(("El monto de anticipo no debe ser mayor a sus utilidades: {:,.2f}".format(aux_amount)))

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    salary_advance_ids = fields.One2many(comodel_name='custom_salary_advance', inverse_name='name', string='Anticipo de salario')

class HrContract(models.Model):
    _inherit = 'hr.contract'

    def _compute_employee_contract(self):
        advance_objet = self.env['custom_salary_advance'].search([('name', '=', self.employee_id.name)])
        if advance_objet:
            self.salary_advance_ids += advance_objet
        else:
            self.salary_advance_ids = False

    salary_advance_ids = fields.One2many(comodel_name='custom_salary_advance', inverse_name='employee_contract_id', compute='_compute_employee_contract' ,string='Anticipo de salario')

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _compute_employee_paylip(self):
        advance_objet = self.env['custom_salary_advance'].search([('name', '=', self.employee_id.name)])
        if advance_objet:
            self.salary_advance_ids += advance_objet
        else:
            self.salary_advance_ids = False

    salary_advance_ids = fields.One2many(comodel_name='custom_salary_advance', inverse_name='employee_payslip_id', compute='_compute_employee_paylip' ,string='Anticipo de salario')