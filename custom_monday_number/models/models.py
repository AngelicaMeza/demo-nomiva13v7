# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomMondayNumber(models.Model):
    _name = 'custom_monday_number'

    name = fields.Integer(string='Número de lunes')
    monday_number_date = fields.Date(string='Fecha')
    description = fields.Char(string='Descripción')

    def name_get(self):
        result = []
        msg = ' '
        for record in self:
            if record.name and record.monday_number_date:
                msg = str(record.name) + ' / ' + str(record.monday_number_date)
            elif not record.monday_number_date:
                msg = str(record.name)
            result.append((record.id, msg))
            msg = ' '
        return result

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    monday_number_id = fields.Many2one(comodel_name='custom_monday_number',string='Número de lunes')

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    monday_number_id = fields.Many2one(comodel_name='custom_monday_number',string='Número de lunes')


class CustomWeekend(models.Model):
    
    _name = 'custom_weekend'
    _description = 'Número de sábados y domingos'

    name = fields.Integer(string='Número de sábados y domingos')
    weekend_date = fields.Date(string='Fecha')
    description = fields.Char(string='Descripción')

    def name_get(self):
        result = []
        msg = ' '
        for record in self:
            if record.name and record.weekend_date:
                msg = str(record.name) + ' / ' + str(record.weekend_date)
            elif not record.weekend_date:
                msg = str(record.name)
            result.append((record.id, msg))
            msg = ' '
        return result


class HrPayslipWeekend(models.Model):
    _inherit = 'hr.payslip'

    weekend_id = fields.Many2one(comodel_name='custom_weekend',string='Número de sábados y domingos')

class HrPayslipRunWeekend(models.Model):
    _inherit = 'hr.payslip.run'

    weekend_id = fields.Many2one(comodel_name='custom_weekend',string='Número de sábados y domingos')

class HrPayslipRunEmployee(models.TransientModel):
    _inherit = 'hr.payslip.employees'
    
    # Filto por departamento del empleado
    department_id = fields.Many2one(comodel_name='hr.department', string='Departamento')

    @api.onchange('department_id')
    def onchange_department_id(self):
        employees = self.env['hr.employee'].search([('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id), ('department_id', '=', self.department_id.id)])
        all_employees = self.env['hr.employee'].search(self._get_available_contracts_domain())
        if self.department_id:
            if employees:
                self.employee_ids = employees
            else:
                self.employee_ids = False
        else:
            self.employee_ids = all_employees