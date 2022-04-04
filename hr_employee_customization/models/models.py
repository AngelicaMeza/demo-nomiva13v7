# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HrEmployeeSalaryAdvance(models.Model):
    _name = 'hr_employee_salary_advance'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Employee salary advance'

    name = fields.Selection(
        [('1', 'Employee'), ('2', 'Department'), ('3', 'Company')], string="Advance type")

    employee_ids = fields.Many2many(
        string='Employees', comodel_name='hr.employee', ondelete='restrict')

    employee_contract_ids = fields.Many2many(
        comodel_name='hr.contract', string='Employee contracts', ondelete='restrict')

    active = fields.Boolean(
        default=True, help="Set active to false to hide the salary advance tag without removing it.")

    employee_payslip_id = fields.Many2one(
        comodel_name='hr.payslip', ondelete='restrict')

    department_id = fields.Many2one(
        comodel_name='hr.department', ondelete='restrict', string='Department')
    currency_id = fields.Many2one(
        comodel_name='res.currency', ondelete='restrict', string='Currency')
    company_id = fields.Many2one(
        comodel_name='res.company', ondelete='restrict', string='Company')

    date = fields.Date(string='Date')
    reason = fields.Selection([('1', 'Advance payment of social benefits'), ('2', 'Profit advance'), (
        '3', 'Salary advance'), ('4', 'Advance vacation'), ('5', 'Days per years')], string='Reason')
    advancement = fields.Float(string='Amount')
    
    advance_vacation = fields.Boolean(string='It is a vacation bonus?')
    
    type_advance_vacation = fields.Selection(
        string='Type advance vacation',
        selection=[('1', 'Bonus'), ('2', 'Vacations')])

    def name_get(self):
        result = []
        msg = ' '

        for record in self:
            if self.name == '1':
                msg = str(self.employee_ids.name)
            elif self.name == '2':
                msg = str(self.employee_ids.department_id.name)
            else:
                msg = str(self.employee_ids.company_id.name)
            result.append((record.id, msg))
            msg = ' '
        return result

    @api.onchange('name', 'employee_ids', 'department_id', 'company_id')
    def onchange_fields(self):
        if self.name == '1':
            self.employee_contract_ids = False
            self.department_id = False
            self.company_id = False
            if self.employee_ids:
                if len(self.employee_ids) > 1:
                    self.employee_ids = False
                else:
                    self.employee_contract_ids = False if self.employee_contract_ids else self.employee_ids.contract_id
                    self.department_id = False if self.department_id else self.employee_ids.department_id
                    self.company_id = False if self.company_id else self.employee_ids.company_id
        elif self.name == '2':
            self.employee_ids = False
            self.employee_contract_ids = False
            self.company_id = False
            if self.department_id:
                self.employee_ids = False if self.employee_ids else self.department_id.member_ids
                self.employee_contract_ids = False if self.employee_contract_ids else self.employee_ids.contract_ids
                self.company_id = False if self.company_id else self.employee_ids.company_id
        elif self.name == '3':
            employee_obj = self.env['hr.employee'].search(
                [('company_id', '=', self.company_id.id), ('active', '=', True)])
            self.employee_ids = False
            self.employee_contract_ids = False
            self.department_id = False
            if self.company_id:
                self.employee_ids = False if self.employee_ids else employee_obj
                self.employee_contract_ids = False if self.employee_contract_ids else self.employee_ids.contract_ids
                self.department_id = False
    
    @api.onchange('advancement')
    def _onchange_advancement(self):
        if self.name == '1':
            first_contract = self.employee_ids.contract_id
            contract_obj = self.env['hr.contract'].search(
                [('employee_id', '=', first_contract.employee_id.id)])

            # Validation of days per year
            if self.name == '1' and self.reason == '5' and contract_obj:
                # The amount available in days per year is automatically assigned to the requested advance.
                self.advancement = contract_obj.employee_days_per_year

                # The advance of days per year is subtracted from the general total.
                contract_obj.employee_grand_total -= self.advancement

                # The amount available in days per year is updated.
                contract_obj.employee_days_per_year -= self.advancement
            else:
                pass

    @api.constrains('advancement')
    def constrains_advancement(self):
        # Finding the amount of profits for the worker
        if self.name == '1':
            first_contract = self.employee_ids.contract_id
            contract_obj = self.env['hr.contract'].search(
                [('employee_id', '=', first_contract.employee_id.id)])
            result = False
            msj = " "
            # Validation of profit advances
            if self.name == '1' and self.reason == '2':
                if contract_obj:
                    # There is an advance
                    if contract_obj.employee_result_profit:
                        aux_amount = contract_obj.employee_result_profit
                    # It is validated according to the amount: (TA) * (0.33)
                    else:
                        aux_amount = contract_obj.employee_profit
                    # Is the amount entered greater than the utilities available?
                    result = True if self.advancement > round(
                        aux_amount, 2) else False
                    msj += _("to your profits")
            # Validation of social benefits
            elif self.name == '1' and self.reason == '1':
                if contract_obj:
                    # There is no previous benefit (the accumulated "excel" is taken)
                    if not contract_obj.employee_grand_total:
                        contract_obj.employee_grand_total = contract_obj.employee_social_benefits + \
                            contract_obj.employee_accrued_benefits
                    else:
                        pass

                    # Is the amount deposited greater than 75% of the total available benefits?
                    aux_amount = contract_obj.employee_grand_total
                    result = True if self.advancement > round(
                        aux_amount*(75/100), 2) else False
                    msj += _("to 75{} of the total amount of benefits available".format("%"))
            else:
                pass
            if result:
                raise ValidationError(
                    _(("The advance amount must not be greater than {}: {:,.2f}".format(msj, aux_amount))))

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    salary_advance_ids = fields.Many2many(
        string='salary_advance',
        comodel_name='hr_employee_salary_advance',
        help="Salary advances requested by the employee",
        ondelete='restrict'
    )