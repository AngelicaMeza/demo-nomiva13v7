# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomEmployeeLoans(models.Model):
    _inherit = 'hr.contract'

    def _compute_employee_loans(self):
        #Buscando las nominas del empleado que esten en estado de pagado.
        payslip_obj = self.env['hr.payslip'].search([('employee_id.id', '=', self.employee_id.id), ('state', 'in', ['done', 'paid'])], order='id desc')

        # Prestamos (PRES)
        aux = 0
        for line in self.salary_advance_ids:
            if line.reason == '3':
                aux += line.advancement
        self.employee_loans = aux

        # Prestamos (DPRES)
        if payslip_obj:
            for payslip in payslip_obj:
                for line in payslip.line_ids:
                    if line.code in ['DPRES'] and not payslip.loans_paid:
                        payslip.loans_paid = True
                        self.employee_dpres += line.total
                    else:
                        pass
        else:
            self.employee_dpres = 0
        
        if self.employee_loans and self.employee_dpres:
            self.employee_result_loans = self.employee_loans - self.employee_dpres
        elif self.employee_loans:
            self.employee_result_loans = self.employee_loans
        else:
            self.employee_result_loans = 0
        
        self.compute_test_loans = True

    # Prestamos y Anticipos de sueldo
    employee_loans = fields.Float(string='Anticipos de sueldo', default=0)
    employee_dpres = fields.Float(string='Descuentos de Anticipos de sueldo', default=0)
    employee_result_loans = fields.Float(string='Total', default=0)
    compute_test_loans = fields.Boolean(compute='_compute_employee_loans')


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'
    
    loans_paid = fields.Boolean(default=False)
