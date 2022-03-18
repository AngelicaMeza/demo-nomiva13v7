# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import re
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta

class CustomEmployee(models.Model):
    _inherit = 'hr.employee'

    rif = fields.Char(string='R.I.F', groups="hr.group_hr_user")
    # Cuenta bancaria
    account_holder_id = fields.Char(string='Titular de la cuenta', groups="hr.group_hr_user")
    holder_id = fields.Char(string='C.I. del titular', groups="hr.group_hr_user")

    def write(self, vals):
        res = {}
        if vals.get('rif'):
            res = self.validate_rif(vals.get('rif', False))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    'El rif tiene el formato incorrecto. Ej: V-012345678, E-012345678, J-012345678 o G-012345678. Por favor intente de nuevo'))
            if not self.validate_rif_duplicate(vals.get('rif', False)):
                raise exceptions.except_orm(('Advertencia!'),
                                            (u'El cliente o proveedor ya se encuentra registrado con el rif: %s y se encuentra activo') % (
                                                vals.get('rif', False)))
        res = super(CustomEmployee, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        res = {}
        if vals.get('rif'):
            res = self.validate_rif(vals.get('rif'))
            if not res:
                raise exceptions.except_orm(('Advertencia!'), (
                    'El rif tiene el formato incorrecto. Ej: V-012345678, E-012345678, J-012345678 o G-012345678. Por favor intente de nuevo'))
            if not self.validate_rif_duplicate(vals.get('rif', False), True):
                raise exceptions.except_orm(('Advertencia!'),
                                            (u'El cliente o proveedor ya se encuentra registrado con el rif: %s y se encuentra activo') % (
                                                vals.get('rif', False)))
        res = super(CustomEmployee, self).create(vals)
        return res

    @api.model
    def validate_rif(self, field_value):
        rif_obj = re.compile(r"^[V|E|J|G]+[-][\d]{9}", re.X)
        if rif_obj.search(field_value.upper()):
            if len(field_value) == 11:
                return True
            else:
                return False
        return False

    def validate_rif_duplicate(self, valor, create=False):
        found = True
        company = self.search([('rif', '=', valor)])
        if create:
            if company:
                found = False
        elif company:
            found = False
        return found

class CustomContract(models.Model):
    _inherit = 'hr.contract'

    
    def _compute_employee_soo_cestaticket(self):
        company_obj = self.env['res.company'].search([('id', '=', self.env.company.id)])

        if company_obj:
            self.social_security_salary = company_obj.minimum_salary
            self.salary_basket_ticket = company_obj.salary_basket_ticket
        else:
            self.social_security_salary = 0
            self.salary_basket_ticket = 0
        self.compute_field_soo = True

    compute_field_soo = fields.Boolean(compute='_compute_employee_soo_cestaticket')
    social_security_salary = fields.Float(string='Salario Seguro Social SSO')
    salary_basket_ticket = fields.Float(string='Salario Cesta Ticket')
    custom_salary = fields.Float(string="Salario en $")
    withholding_discount_rate = fields.Float(string="Tasa descuento retención", digits=(4, 2))

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def _compute_employee_soo_cestaticket_payslip_run(self):
        company_obj = self.env['res.company'].search([('id', '=', self.env.company.id)])

        if company_obj:
            self.social_security_salary = company_obj.minimum_salary
            self.salary_basket_ticket = company_obj.salary_basket_ticket
        else:
            self.social_security_salary = 0
            self.salary_basket_ticket = 0
        self.compute_field_payslip_run = True

    compute_field_payslip_run = fields.Boolean(compute='_compute_employee_soo_cestaticket_payslip_run')
    social_security_salary = fields.Float(string='Salario Seguro Social SSO')
    salary_basket_ticket = fields.Float(string='Salario Cesta Ticket')