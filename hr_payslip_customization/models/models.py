# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'
    
    # Field to validate loans for employees
    loans_paid = fields.Boolean(default=False)
    # Field to validate employee utilities
    profit_paid = fields.Boolean(default=False)
    # Field to validate employee Vacation advance and vacation discounts
    vac_paid = fields.Boolean(default=False)
    
    # field to Tree of advances in payroll payments
    salary_advance_ids = fields.Many2many(
        comodel_name='hr_employee_salary_advance',
        related='employee_id.salary_advance_ids',
        ondelete='restrict',
    )