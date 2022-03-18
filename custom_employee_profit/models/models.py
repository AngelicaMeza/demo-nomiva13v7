# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomEmployeeProfit(models.Model):
    _inherit = 'hr.contract'

    def _compute_employee_profit(self):
        #Buscando las nominas del empleado que esten en estado de pagado.
        payslip_obj = self.env['hr.payslip'].search([('employee_id.id', '=', self.employee_id.id), ('state', 'in', ['done', 'paid'])], order='id desc')
        
        if payslip_obj:
            for payslip in payslip_obj:
                # Buscando el monto (TA) o (TAVAC)
                for line in payslip.line_ids:
                    if line.code in ['TA', 'TAVAC'] and not payslip.profit_paid:
                        payslip.profit_paid = True
                        self.employee_profit += (line.total * (payslip.company_id.minimum_salary / 360))
                    else:
                        pass
        else:
            self.employee_profit = 0


        # Calculo de Anticipo de utilidades
        aux = 0
        for line in self.salary_advance_ids:
            if line.reason == '2':
                aux += line.advancement
        self.employee_adu = aux
        
        if self.employee_profit and self.employee_adu:
            self.employee_result_profit = self.employee_profit - self.employee_adu
        elif self.employee_profit:
            self.employee_result_profit = self.employee_profit
        else:
            self.employee_result_profit = 0
        
        self.compute_test = True

    def _compute_employee_holiday_advance(self):
        #Buscando las nominas del empleado que esten en estado de pagado.
        payslip_obj = self.env['hr.payslip'].search([('employee_id.id', '=', self.employee_id.id), ('state', 'in', ['done', 'paid'])], order='id desc')

        # Anticipo de vacaciones
        aux = 0
        for line in self.salary_advance_ids:
            if line.reason == '4':
                aux += line.advancement
        self.employee_holiday_advance = aux

        # DEPRESVAC
        if payslip_obj:
            for payslip in payslip_obj:
                for line in payslip.line_ids:
                    if line.code in ['DEPRESVAC'] and not payslip.profit_paid:
                        payslip.profit_paid = True
                        self.employee_holiday_depresvac_amount += line.total
                    else:
                        pass
        else:
            self.employee_holiday_depresvac_amount = 0
        
        if self.employee_holiday_advance and self.employee_holiday_depresvac_amount:
            self.employee_total_holiday_advance = self.employee_holiday_advance - self.employee_holiday_depresvac_amount
        elif self.employee_holiday_advance:
            self.employee_total_holiday_advance = self.employee_holiday_advance
        else:
            self.employee_total_holiday_advance = 0
        
        self.compute_test_holiday_advance = True

    #Utilidades y Anticipos de utilidades
    employee_profit = fields.Float(string='Utilidades', default=0)
    employee_adu = fields.Float(string='Anticipo de utilidades', default=0)
    employee_result_profit = fields.Float(string='Total disponible', default=0)
    compute_test = fields.Boolean(compute='_compute_employee_profit')

    # Anticipo de vacaciones
    employee_holiday_advance = fields.Float(string='Anticipo de vacaciones', default=0)
    employee_holiday_depresvac_amount = fields.Float(string='Descuentos de Anticipos de vacaciones', default=0)
    employee_total_holiday_advance = fields.Float(string='Total', default=0)
    compute_test_holiday_advance = fields.Boolean(compute='_compute_employee_holiday_advance')

class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'
    
    profit_paid = fields.Boolean(default=False)