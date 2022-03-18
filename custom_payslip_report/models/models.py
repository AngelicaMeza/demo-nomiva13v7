# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
class CustomPayslipReport(models.Model):
    _inherit = 'hr.payslip'

    #metodo para el calculo del acumulado de las Asignaciones
    def accumulated_assignments(self):
        acum = 0
        for line in self.line_ids:
            if line.category_id.name in ['Básico','Prima','Basico2'] and line.appears_on_payslip:
                acum += line.total
        return acum
    #metodo para el calculo del acumulado de las Deducciones
    def accumulated_deductions(self):
        acum = 0
        for line in self.line_ids:
            if line.category_id.name in ['Deducción','Aporte'] and line.appears_on_payslip:
                acum += line.total
        return acum

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id: # Add a default contract if not already defined
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        payslip_name = self.struct_id.payslip_name or ('Recibo de Salario')
        self.name = '%s' % (payslip_name)

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = ("¡Esta nómina puede ser errónea! Es posible que no se generen entradas de trabajo para el período desde  %s hasta %s." %
                (date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1), date_to))
        else:
            self.warning_message = False

        self.worked_days_line_ids = self._get_new_worked_days_lines()
    
