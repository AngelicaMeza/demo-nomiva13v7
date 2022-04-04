# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class HrContractCustomization(models.Model):
    _inherit = 'hr.contract'

    # Employee social benefits
    def _compute_social_benefits(self, contract_obj):
        # Calculation of advance payment of social benefits
        contract_obj.employee_advance_payment_benefits = sum(
            line.advancement for line in contract_obj.salary_advance_ids if line.reason == '1')

        if contract_obj.employee_advance_payment_benefits and contract_obj.employee_total_available_social_benefits:
            contract_obj.employee_total_available_social_benefits -= contract_obj.employee_advance_payment_benefits

    # Utilities and Advances of utilities
    def _compute_employee_profit(self, payslip_obj, contract_obj):
        # Calculation of Advance of utilities
        contract_obj.employee_adu = sum(
            line.advancement for line in contract_obj.salary_advance_ids if line.reason == '2')

        if payslip_obj:
            for payslip in payslip_obj:
                paid = False
                # Looking for the amount (TA), (TAVAC) or (TAQ)
                for line in payslip.line_ids:
                    if line.code in ['TA', 'TAVAC', 'TAQ']:
                        paid = True
                        if not payslip.profit_paid:
                            contract_obj.employee_profit += (
                                line.total * (payslip.company_id.profit_days / 360))
                    else:
                        pass
                if paid and not payslip.profit_paid:
                    payslip.profit_paid = True
                else:
                    pass
        else:
            pass

        if contract_obj.employee_profit and contract_obj.employee_adu:
            contract_obj.employee_result_profit = contract_obj.employee_profit - \
                contract_obj.employee_adu
        elif contract_obj.employee_profit:
            contract_obj.employee_result_profit = contract_obj.employee_profit
        else:
            contract_obj.employee_result_profit = 0

    # Employee loans
    def _compute_employee_loans(self, payslip_obj, contract_obj):
        # salary advance
        contract_obj.employee_loans = sum(
            line.advancement for line in contract_obj.salary_advance_ids if line.reason == '3')

        # loans (DPRES)
        if payslip_obj:
            for payslip in payslip_obj:
                paid = False
                for line in payslip.line_ids:
                    if line.code in ['DPRES']:
                        paid = True
                        if not payslip.loans_paid:
                            contract_obj.employee_dpres += line.total
                    else:
                        pass
                if paid and not payslip.loans_paid:
                    payslip.loans_paid = True
                else:
                    pass
        else:
            pass

        if contract_obj.employee_loans and contract_obj.employee_dpres:
            contract_obj.employee_result_loans = contract_obj.employee_loans - \
                contract_obj.employee_dpres
        elif contract_obj.employee_loans:
            contract_obj.employee_result_loans = contract_obj.employee_loans
        elif contract_obj.employee_dpres:
            contract_obj.employee_result_loans = contract_obj.employee_dpres
        else:
            contract_obj.employee_result_loans = 0

    # Vacation advance and vacation discounts
    def _compute_employee_holiday_advance(self, payslip_obj, contract_obj):
        # Advance vacation
        contract_obj.employee_holiday_advance = sum(
            line.advancement for line in contract_obj.salary_advance_ids if line.reason == '4' and not line.advance_vacation)

        # Vacation bonus counter
        contract_obj.employee_vacation_bonus = sum(
            line.advancement for line in contract_obj.salary_advance_ids if line.reason == '4' and line.advance_vacation)

        # DEPRESVAC
        if payslip_obj:
            for payslip in payslip_obj:
                paid = False
                for line in payslip.line_ids:
                    if line.code in ['DEPRESVAC']:
                        paid = True
                        if not payslip.vac_paid:
                            contract_obj.employee_holiday_depresvac_amount += line.total
                    else:
                        pass
                if paid and not payslip.vac_paid:
                    payslip.vac_paid = True
                else:
                    pass
        else:
            pass

        if contract_obj.employee_holiday_advance and contract_obj.employee_holiday_depresvac_amount and contract_obj.employee_vacation_bonus:
            contract_obj.employee_total_holiday_advance = (contract_obj.employee_holiday_advance + contract_obj.employee_vacation_bonus) - \
                contract_obj.employee_holiday_depresvac_amount
        elif contract_obj.employee_holiday_advance and contract_obj.employee_vacation_bonus:
            contract_obj.employee_total_holiday_advance = contract_obj.employee_holiday_advance + \
                contract_obj.employee_vacation_bonus
        elif contract_obj.employee_holiday_depresvac_amount:
            contract_obj.employee_total_holiday_advance = contract_obj.employee_holiday_depresvac_amount
        else:
            contract_obj.employee_total_holiday_advance = 0

    # Returns the months and years of seniority of the employee
    def _get_employee_seniority(current_contract):
        today = fields.Date.from_string(fields.Date.today())

        if not current_contract.date_end:
            # Seniority of the worker (in days)
            days = today - current_contract.date_start

            months_seniority = round(
                (days.days + 0.44)/30.44, 2) if days.days % 365 == 0 else round(days.days/30.44, 2)

            years_seniority = round(
                months_seniority/12, 2)
        else:
            days = current_contract.date_end - current_contract.date_start

            months_seniority = round(
                (days.days + 0.44)/30.44, 2) if days.days % 365 == 0 else round(days.days/30.44, 2)

            years_seniority = round(
                months_seniority/12, 2)

        months_seniority = months_seniority if months_seniority > 0 else 0
        years_seniority = years_seniority if years_seniority > 0 else 0

        seniority = {'today': today, 'months': months_seniority,
                    'years': years_seniority}
        return seniority

    def _write_employee_seniority(current_contract):
        msj_years = _("Years") if int(
            current_contract.employee_years_seniority) > 1 else _("Year")
        msj_months = _("Months") if int(
            current_contract.employee_months_seniority) > 1 else _("Month")

        if current_contract.employee_years_seniority >= 1:
            aux_months = int(current_contract.employee_months_seniority) if current_contract.employee_months_seniority < 12 else int(
                current_contract.employee_months_seniority) % 12

            current_contract.employee_seniority = "{} {} y {} {}".format(
                str(int(current_contract.employee_years_seniority)), msj_years, str(aux_months), msj_months)
        else:
            current_contract.employee_seniority = "{} {}".format(
                str(int(current_contract.employee_months_seniority)), msj_months)

    # Update advances button
    def update_advances(self):
        # from the button
        if self.active:
            seniority = self._get_employee_seniority()
            self.employee_months_seniority = seniority.get('months')
            self.employee_years_seniority = seniority.get('years')
            self._write_employee_seniority()

            # Searching for the employee's payroll that is in paid or done status.
            payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id), ('state', 'in', [
                'done', 'paid'])], order='id desc')
            self._compute_social_benefits(self)
            self._compute_employee_profit(payslip_obj, self)
            self._compute_employee_loans(payslip_obj, self)
            self._compute_employee_holiday_advance(payslip_obj, self)
        else:  # from planned action
            employee_obj = self.env['hr.employee'].search([])
            for employee in employee_obj:
                # Searching for the employee's payroll that is in paid or done status.
                payslip_obj = self.env['hr.payslip'].search(
                    [('employee_id', '=', employee.id), ('state', 'in', ['done', 'paid'])], order="create_date asc")
                self._compute_social_benefits(employee.contract_id)
                self._compute_employee_profit(
                    payslip_obj, employee.contract_id)
                self._compute_employee_loans(payslip_obj, employee.contract_id)
                self._compute_employee_holiday_advance(
                    payslip_obj, employee.contract_id)

    # Social benefits
    def _social_benefits(self):
        employee_obj = self.env['hr.employee'].search([])
        for employee in employee_obj:
            # Searching for the employee's payroll that is in paid status.
            payslip_obj = self.env['hr.payslip'].search(
                [('employee_id', '=', employee.id), ('state', 'in', ['done', 'paid'])], order="create_date asc")

            if employee.contract_id.date_start:
                
                seniority = employee.contract_id._get_employee_seniority()
                today = seniority.get('today')
                employee.contract_id.employee_months_seniority = seniority.get('months')
                employee.contract_id.employee_years_seniority = seniority.get('years')
                employee.contract_id._write_employee_seniority()

                if payslip_obj:
                    # Step 1: Calculation of the monthly salary benefits
                    payslip_rates = [
                        rate for rate in payslip_obj.custom_currency_id]
                    aux_rates = payslip_rates[len(
                        payslip_rates) - 1].name if len(payslip_rates) >= 1 else 0

                    # 1.1: Worker payroll
                    if (employee.contract_id.department_id.name in ['Obrero']):
                        employee.contract_id.smp = (employee.contract_id.hourly_wage * 30) * 8 if employee.contract_id.hourly_wage > 0 else (
                            (employee.contract_id.custom_salary * aux_rates) / 7) * 30
                    # 1.2: Administrative payroll and security
                    elif (employee.contract_id.department_id.name in ['Administrativo', 'Seguridad']):
                        employee.contract_id.smp = (
                            employee.contract_id.custom_salary * aux_rates)
                    else:
                        pass

                    # Step 2: Calculation of the daily salary benefits
                    """
                        2.1: Bring the employee's payroll that is in a paid status:
                        
                        2.1.1: Seniority equal to 3 months. If the age is the same
                        to 3 months, the query must bring the payrolls that are in 
                        paid status of the last 3 months, filtered by the rule
                        salary SDP (Daily salary benefits).

                        2.1.2: Seniority greater than 3 months. If the seniority is greater
                        to 3 months and also 3 months have passed since the last calculation 
                        of SDP. The query must bring all the payrolls paid for the last 3 months,
                        filtered by the salary rule SDP (Daily salary benefits).
                        
                        2.2: Of all the paid payrolls that result from the query, 
                        add the total amounts of all the lines. 
                    """

                    # 2.1.2: Seniority greater than or equal to 3 months.
                    sdp_list = []
                    if (int(employee.contract_id.employee_months_seniority) >= 3):

                        # Is there a previous sdp calculation?
                        if (employee.contract_id.most_recent_spd):

                            # Number of months since the last sdp calculation
                            months_last_sdp = round(
                                ((today - employee.contract_id.most_recent_spd).days) / 30.44, 2)

                            # Has it been 3 months since the last calculation of sdp?
                            if (int(months_last_sdp) == 3):

                                # Start and end of the last 3 months
                                start_last_3_months = employee.contract_id.most_recent_spd
                                end_last_3_months = today

                                # Most recent calculation of SDP
                                employee.contract_id.most_recent_spd = today

                                # Salaries paid in the last three months
                                sdp_list = payslip_obj.filtered(lambda x: (
                                    (x.date_from >= start_last_3_months and x.date_from < end_last_3_months) and (x.date_to > start_last_3_months and x.date_to <= end_last_3_months)))
                            else:
                                pass
                        else:  # This is your first calculation of spd

                            three_months_date_of_admission = payslip_obj.contract_id.date_start + \
                                relativedelta(months=3)

                            # Start and End of the last 3 months (from the date of admission)
                            start_last_3_months = three_months_date_of_admission
                            end_last_3_months = start_last_3_months + \
                                relativedelta(months=3)

                            # Most recent calculation of SDP
                            employee.contract_id.most_recent_spd = today

                            # Salaries paid for the last three months
                            sdp_list = payslip_obj.filtered(lambda x: (
                                (x.date_from >= start_last_3_months and x.date_from < end_last_3_months) and (x.date_to > start_last_3_months and x.date_to <= end_last_3_months)))
                    else:
                        pass

                    if sdp_list:
                        # Sum of total amounts
                        rule_sdp_acum = sum(
                            [payslip_line.total for payslip_line in sdp_list.line_ids if payslip_line.code in ['SDP']])  # ['STD'] FOR TESTS

                        employee.contract_id.sdp = (
                            employee.contract_id.smp + rule_sdp_acum) / 30

                        # Step 3: Calculation of profit rate
                        aliquot_profits = (
                            employee.contract_id.sdp * employee.company_id.profit_days) / 360

                        # Step 4: Calculation of vacation rate
                        aliquot_holidays = (
                            employee.contract_id.sdp * employee.company_id.holidays) / 360

                        # Step 5: Calculation of the Comprehensive Salary
                        comprehensive_salary = employee.contract_id.sdp + \
                            aliquot_profits + aliquot_holidays

                        # Step 7: Assignment of benefits
                        employee.contract_id.employee_social_benefits = comprehensive_salary
                    else:
                        pass

                    # Step 8: Total Benefits
                    if employee.contract_id.employee_total_social_benefits > 0:
                        employee.contract_id.employee_total_social_benefits += employee.contract_id.employee_social_benefits
                    elif employee.contract_id.employee_accrued_benefits > 0:
                        employee.contract_id.employee_total_social_benefits = employee.contract_id.employee_social_benefits + \
                            employee.contract_id.employee_accrued_benefits
                    else:
                        pass

                    # Step 9: Advances

                    # Step 10: Total Benefits Available, Days per year and Grand Total
                    salary = 0
                    if employee.contract_id.name in ['Vigilante', 'Supervisor de Vigilancia', 'Director Seguridad y Prevención de Pérdida']:
                        if employee.contract_id.structure_type_id.default_schedule_pay == 'weekly':
                            # salary for 12 hours
                            salary = (
                                employee.contract_id.custom_salary * aux_rates) / 7
                    elif employee.contract_id.structure_type_id.wage_type == 'monthly':
                        # Bi-weekly salary (administrative employee)
                        salary = (
                            employee.contract_id.custom_salary * aux_rates) / 30
                    elif employee.contract_id.structure_type_id.default_schedule_pay == 'weekly':
                        # Hourly wage
                        salary = employee.contract_id.hourly_wage * 8
                    elif employee.contract_id.structure_type_id.default_schedule_pay == 'bi-monthly':
                        salary = employee.contract_id.wage / 2

                    # Step 6: Calculation of Additional Days (Days per year)
                    if employee.contract_id.employee_years_seniority % 2 == 0 and employee.contract_id.employee_additional_days <= 31:
                        additional_days = 0
                        for item in range(int(employee.contract_id.employee_years_seniority / 2)):
                            additional_days += 2
                        employee.contract_id.employee_additional_days = additional_days
                        employee.contract_id.employee_days_per_year = employee.contract_id.employee_additional_days * salary

                    # Total Benefits Available
                    employee.contract_id.employee_total_available_social_benefits += (
                        employee.contract_id.employee_total_social_benefits - employee.contract_id.employee_advance_payment_benefits)

                    # Grand Total
                    employee.contract_id.employee_grand_total = (
                        employee.contract_id.employee_total_available_social_benefits + employee.contract_id.employee_days_per_year)
                else:
                    pass
            else:
                pass

    salary_advance_ids = fields.Many2many(
        comodel_name='hr_employee_salary_advance',
    )

    employee_accrued_benefits = fields.Float(
        string="Accumulated benefits", default=0)

    # Loans and salary advances
    employee_loans = fields.Float(string='Salary advances', default=0)
    employee_dpres = fields.Float(string='Salary advance discounts', default=0)
    employee_result_loans = fields.Float(string='Total loans', default=0)

    # Utilities and Advances of utilities
    employee_profit = fields.Float(string='Utilities', default=0)
    employee_adu = fields.Float(string='Advances of utilities', default=0)
    employee_result_profit = fields.Float(string='Total available', default=0)

    # Advance vacation
    employee_holiday_advance = fields.Float(
        string='Advance vacation', default=0)
    employee_holiday_depresvac_amount = fields.Float(
        string='Vacation Advance Discounts', default=0)
    employee_total_holiday_advance = fields.Float(
        string='Total holiday advance', default=0)
    # Vacation bonus counter
    employee_vacation_bonus = fields.Float(
        string='Vacation bonus',
        default = 0,
        digits=(2,2))

    # Social benefits
    employee_social_benefits = fields.Float(
        string='Social benefits', default=0)
    employee_total_social_benefits = fields.Float(
        string='Total benefits', default=0)
    employee_advance_payment_benefits = fields.Float(
        string='Advances', default=0)
    employee_total_available_social_benefits = fields.Float(
        string='Total available benefits', default=0)
    employee_days_per_year = fields.Float(string='Days per year', default=0)
    employee_grand_total = fields.Float(string='Grand Total', default=0)
    # Calculation of social benefits
    smp = fields.Float(help="Monthly salary benefits", default=0)
    sdp = fields.Float(help="Daily salary benefits", default=0)
    most_recent_spd = fields.Date(help="Most recent SPD payment")
    employee_seniority = fields.Char(help="Employee Seniority")
    employee_years_seniority = fields.Float(
        help="Years of seniority of the employee")
    employee_months_seniority = fields.Float(
        help="Months of seniority of the employee")
    employee_additional_days = fields.Integer(
        help="Additional days", default=0)
