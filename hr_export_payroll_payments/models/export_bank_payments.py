import time
import base64

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from unicodedata import normalize

class ExportBankPayments(models.Model):
    _name = 'export.bank.payments'
    _description = 'Exportar pagos de bancos'

    _READONLY_STATES = {'done': [('readonly', True)]}

    name = fields.Char('Nombre', default='Nuevo', readonly=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Confirmado')
    ], string='Estado de transacción', default='draft', copy=False)
    bank_id = fields.Many2one('account.journal', 'Banco', states=_READONLY_STATES)
    date_start = fields.Date('Fecha inicio', states=_READONLY_STATES)
    date_end = fields.Date('Fecha fin', states=_READONLY_STATES)
    txt_file = fields.Binary('Archivo TXT', copy=False)
    txt_name = fields.Char('Filename txt', copy=False)
    payroll_type = fields.Many2one('hr.payroll.structure.type', 'Tipo de nómina', states=_READONLY_STATES, help="Tipo de nómina a tomar en cuenta para la generación del archivo txt.")
    operation_type = fields.Selection([('same','Mismo banco'), ('other','Otros bancos')], string="Tipo de operación", states=_READONLY_STATES, default='same', help="Indica si el pago de nominas es entre cuentas del mismo banco o no.")
    bank_account_id = fields.Many2one('res.partner.bank', 'Número de Cuenta Bancaria', states=_READONLY_STATES, help="Cuenta bancaria de la compañía de donde será debitado el dinero.")
    valid_date = fields.Date('Fecha efectiva de pago', states=_READONLY_STATES, help="Fecha en que se ejecutará el pago.")
    by_employee = fields.Boolean(string="Por empleado", default=False, help="Indica si el txt se genera para determinados empleados.", states=_READONLY_STATES)
    employee_ids = fields.Many2many('hr.employee', string='Empleados', states=_READONLY_STATES, help="Empleados para los que se genera el archivo txt.")
    employee_domain = fields.Many2many('hr.employee', compute="_compute_employee_ids", string='Dominio para Empleados', help="Dominio para filtrar empleados.")
    description = fields.Char('Descripción', help="Texto descriptivo asociado al archivo txt generado.", states=_READONLY_STATES)
    type_trans = fields.Selection([
        ('payroll', 'Empleados'),
        ('fiscal', ' Banavih')
    ], string='Pago a', default='payroll', states=_READONLY_STATES, help="Indica el tipo de txt a generar.")

    @api.onchange('by_employee')
    def _onchange_by_employee(self):
        self.employee_ids = False 

    @api.onchange('bank_account_id')
    def _onchange_bank_account_id(self):

        banks  = self.env['res.partner.bank'].search([])
        banks_ids = []
        for bank in banks:
            if bank.is_payroll_account:
                banks_ids.append(bank.id)
        return {'domain': {'bank_account_id': [('id', 'in', banks_ids)]}}

    @api.onchange('payroll_type')
    def _onchange_payroll_type_id(self):

        structures  = self.env['hr.payroll.structure.type'].search([])
        payroll_type_ids = []
        for structure in structures:
            if 'mensual' in structure.name.lower() or 'semanal' in structure.name.lower():
                payroll_type_ids.append(structure.id)

        return {'domain': {'payroll_type': [('id', 'in', payroll_type_ids )]}}

    @api.depends('bank_account_id','operation_type', 'by_employee', 'type_trans')
    def _compute_employee_ids(self):
        for employee in self:
            employee.employee_domain = self.env['hr.employee']
            if  employee.bank_account_id and employee.by_employee:
                
                #Obtener los ids de los empleados
                    if employee.operation_type == 'same':
                        employee.employee_domain = self.env['hr.employee'].search([]).filtered(lambda x: x.bank_account_number and x.bank_account_number[:4] == employee.bank_account_id.sanitized_acc_number[:4])
                    else:
                        employee.employee_domain = self.env['hr.employee'].search([]).filtered(lambda x: x.bank_account_number and x.bank_account_number[:4] != employee.bank_account_id.sanitized_acc_number[:4])
            elif employee.type_trans == 'fiscal' and employee.by_employee:
                employee.employee_domain = self.env['hr.employee'].search([])
    # -------------------------------------------------------------------------
    @api.onchange('bank_account_id', 'operation_type')
    def _onchange_employee_ids(self):

            #Obtener todos los empleados
            filtered_employees = self.env['hr.employee']
            employees = self.env['hr.employee'].search([])
            for employee in employees:
                if employee.bank_account_number and self.bank_account_id and employee.bank_account_number[:4] == self.bank_account_id.sanitized_acc_number[:4]:
                    filtered_employees += employee
            
            self.employee_filtered_ids = filtered_employees      
    @api.model
    def create(self, vals):
        new_id = super().create(vals)
        new_id.name = self.env['ir.sequence'].next_by_code('export.bank.payments')
        return new_id

    def action_draft(self):
        self.write({
            'state': 'draft',
            'txt_file': False,
            'txt_name': False,
        })
        return True

    def action_done(self):
        """ Exportar el documento en texto plano. """
        self.ensure_one()
        data = ''

        if self.type_trans == 'payroll':
            # Valida si el numero de cuenta es de un determinado banco y si es una cuenta de nomima
            if '0102' in self.bank_account_id.sanitized_acc_number[:4] and self.bank_account_id.is_payroll_account:
                if self.operation_type != 'other':
                    root = self.generate_venezuela()
                else:
                    root = self.generate_venezuela_to_others()    
                data, filename = self._write_attachment(root, 'VZLA')
        elif self.type_trans == 'fiscal':
            root = self.generate_fiscal_payroll()
            fiscal_code = f'{self.date_end.month:0>2}' + str(self.date_end.year)
            data, filename = self._write_attachment(root, 'N03215002244192985966' + fiscal_code + '.txt', False)    
        if not data:
            raise ValidationError('No se pudo generar el archivo. Intente de nuevo con otro periodo u otro número de cuenta.')
        return self.write({'state': 'done'})

    def _write_attachment(self, root, prefix, use_date=True):
        """ Encrypt txt, save it to the db and view it on the client as an
        attachment
        @param root: location to save document
        """
        date = time.strftime('%d%m%y') if use_date else ''
        txt_name = f'{prefix}{date}.txt'
        txt_file = root.encode('utf-8')
        txt_file = base64.encodestring(txt_file)
        self.write({'txt_name': txt_name, 'txt_file': txt_file})
        return txt_file, txt_name

    def _get_import_total_by_employee(self):    

        domain = [
            ('slip_id.contract_id.lpvh', '=', True),
            ('slip_id.date_from', '>=', self.date_start),
            ('slip_id.date_to', '<=', self.date_end),
            ('slip_id.move_id.state', '=', 'posted'),
            ('category_id.code', 'in', ['BASIC', 'BASIC3'])]
        
        fields = ['employee_id',  'total :sum']
        groupby = ['employee_id']
        group_data = self.env['hr.payslip.line'].read_group(domain,fields, groupby)
        
        employees_data = {p['employee_id'][0]: p['total'] for p in group_data}
        
        return employees_data

    ###################################################################################
    def _get_payslips(self):
        """
        Consulta de recibos de pagos. De acuerdo a las siguientes condiciones:
        1. Periodo del recibo
        2. Tipo de nomina: Comparacion de check que indica si la nomina es de obrero o admin
        3. Empleado tiene un numero de cuenta
        4. Estado del asiento contable = publicado
        """

        payslips = self.env['hr.payslip'].search([
            ('date_from', '=', self.date_start),
            ('date_to', '=', self.date_end),
            ('struct_id.type_id.is_worker_payroll', '=', self.payroll_type.is_worker_payroll),
            ('employee_id.bank_account_number', '!=', False),
            ('move_id.state', '=', 'posted'),
        ])
        # Filtro:
        # 1. Tipo de operacion: Comparar primeros 4 digitos de la cuenta de la compañia con los de la cuenta del empleado
        if self.operation_type == 'same':
            payslips = payslips.filtered(lambda x: x.employee_id.bank_account_number[:4] == self.bank_account_id.acc_number[:4])
        else:
            payslips = payslips.filtered(lambda x: x.employee_id.bank_account_number[:4] != self.bank_account_id.acc_number[:4])
        # 2. Por empleado 
        if self.by_employee:
            payslips = payslips.filtered(lambda x: x.employee_id in self.employee_ids)
        
        # 3. Unicidad de tripleta (beneficiario, numero de cuenta, monto) en recibos de pagos
        pay_list = []
        for payslip in payslips:
            if (payslip.employee_id.id, payslip.employee_id.bank_account_number, payslip.net_wage) in pay_list:
                payslips -= payslip 
            else:
                pay_list += [(payslip.employee_id.id, payslip.employee_id.bank_account_number, payslip.net_wage)]
        return payslips

        ##################################################################

    def employee_payroll_validations(self, payslip):

        if not payslip.employee_id.holder_id:
            raise ValidationError(("Por favor establezca la C.I. para el empleado: %s.") % (payslip.employee_id.name))
        elif not payslip.employee_id.holder_id.isnumeric():
            raise ValidationError(("La C.I. del empleado: %s, debe contener solo números.") % (payslip.employee_id.name))

        if not payslip.employee_id.bank_account_number:
            raise ValidationError(("Por favor establezca un número de cuenta para el empleado: %s.") % (payslip.employee_id.name))
        elif len(payslip.employee_id.bank_account_number) != 20:    
                raise ValidationError(("La longitud del número de cuenta del beneficiario: %s, debe ser de 20 dígitos.") % (payslip.employee_id.name))
        
        if not payslip.employee_id.account_type:
            raise ValidationError(("Por favor establezca el tipo de cuenta para el empleado: %s.") % (payslip.employee_id.name))
            
        if not payslip.employee_id.account_holder_id:
            raise ValidationError(("Por favor establezca el titular de la cuenta para el empleado: %s.") % (payslip.employee_id.name))

        if not payslip.net_wage or payslip.net_wage <= 0.0 :
            raise ValidationError(("Establezca un monto valido a pagar al empleado: %s.") % (payslip.employee_id.name))     

        if self.operation_type == 'same':
            
            if len(payslip.employee_id.holder_id) > 10:
                raise ValidationError(("La C.I. del empleado: %s, excede la cantidad maxima de caracteres.") % (payslip.employee_id.name))
            
            if len(payslip.employee_id.account_holder_id) > 40:
                raise ValidationError(("El titular de la cuenta para el empleado: %s, excede la cantidad maxima de caracteres.") % (payslip.employee_id.name))

            if len(f'{payslip.net_wage:.2f}'.replace('.', '')) > 11:
                raise ValidationError(("El monto a pagar para el empleado: %s, excede la cantidad maxima de digitos.") % (payslip.employee_id.name))

        if self.operation_type == 'other':

            if len(payslip.employee_id.holder_id) > 9:
                raise ValidationError(("La C.I. del empleado: %s, excede la cantidad maxima de caracteres.") % (payslip.employee_id.name))

            if not payslip.employee_id.bank_id:
                raise ValidationError(("Por favor seleccione un banco para la cuenta del empleado: %s.") % (payslip.employee_id.name))
            elif not payslip.employee_id.bank_id.bic:
                raise ValidationError(("Por favor establezca el codigo SWIFT para el banco %s.") % (payslip.employee_id.bank_id.name))
            elif len(payslip.employee_id.bank_id.bic) > 12:
                raise ValidationError(("El codigo SWIFT del banco %s, excede la cantidad maxima de caracteres.") % (payslip.employee_id.bank_id.name))
            
            if not payslip.employee_id.country_id:
                raise ValidationError(("Por favor establezca la nacionalidad del empleado: %s.") % (payslip.employee_id.name))
            if len(payslip.employee_id.account_holder_id) > 30:
                raise ValidationError(("El titular de la cuenta para el empleado: %s, excede la cantidad maxima de caracteres.") % (payslip.employee_id.name))

            if len(f'{payslip.net_wage:.2f}') > 18:
                raise ValidationError(("El monto a pagar para el empleado: %s, excede la cantidad maxima de digitos.") % (payslip.employee_id.name))

        
    def _txt_prepare_data_venezuela(self, payslip):

        aux_txt_data = ''

        # *** Preparacion de campos ***
        
        rec_id = 0 if payslip.employee_id.account_type == 'corriente' else 1
        acc_type = '0770' if payslip.employee_id.account_type == 'corriente' else '1770'

        bank_acc = payslip.employee_id.bank_account_number
        amount = f'{payslip.net_wage:.2f}'.replace('.', '')    
        employee_name = payslip.employee_id.account_holder_id
        employee_id = payslip.employee_id.holder_id
        
        # *** Construccion de registro ***
        aux_txt_data += f'{rec_id:<1}{bank_acc:<20}{amount:0>11}{acc_type:<4}{employee_name:<40}{employee_id:0>10}{"003291":<6}{"":<2}\n'
        
        return aux_txt_data
    ##################################################################
    def _txt_prepare_data_venezuela_to_others(self, payslip, sequence):

        aux_txt_data = ''

        # *** Registro de debito ***

        # Preparacion de campos
        receipt_number = str(sequence) + payslip.move_id.name[len(payslip.move_id.name)-4:len(payslip.move_id.name)]
        vat_digits = ''
        nationality = ''
        if self.env.company.vat:
            nationality = self.env.company.vat[0:1]
            vat_digits = self.env.company.vat.replace('-', '')
            if len(self.env.company.vat) > 10:
                vat_digits = f'{vat_digits[1:10]}' 
            else:
                vat_digits = f'{vat_digits[1:len(vat_digits)]}'
        if len(self.env.company.name) > 35 :
            company_name = self.env.company.name[:35]
        else:
            company_name = self.env.company.name    

        if self.bank_account_id.sanitized_acc_number and len(self.bank_account_id.sanitized_acc_number) == 20:
            bank_acc = self.bank_account_id.sanitized_acc_number
        else:
            bank_acc = '0'*20

        amount = f'{payslip.net_wage:.2f}'.replace('.', ',')    
        # Construccion de registro 
        aux_txt_data += f'{"DEBITO":<8}{receipt_number:0>8}{nationality:<1}{vat_digits:0>9}{company_name:<35}{self.valid_date:%d/%m/%Y}'
        aux_txt_data += f'{"00":<2}{bank_acc:<20}{amount:0>18}{"VEF":<3}{"40":<2}\n'

        # *** Registro de credito ***

        # Preparacion de campos
        if payslip.employee_id.country_id.name == 'Venezuela':
            nationality = 'V'
        else:    
            nationality = 'E'

        employee_id = payslip.employee_id.holder_id
        employee_name = payslip.employee_id.account_holder_id

        acc_type = '00'    
        
        if payslip.employee_id.account_type == 'corriente':
            acc_type = '00'
        else:
            acc_type = '01' 
        bank_acc = payslip.employee_id.bank_account_number
        
        amount = f'{payslip.net_wage:.2f}'.replace('.', ',')

        bic = payslip.employee_id.bank_id.bic         

        # Construccion de registro 
        aux_txt_data += f'{"CREDITO":<8}{receipt_number:0>8}{nationality:<1}{employee_id:0>9}{employee_name:<30}{acc_type:<2}{bank_acc:<20}'
        aux_txt_data += f'{amount:0>18}{"00":<2}{bic:<12}{"":<3}{"":<4}{"":<50}\n'

        return aux_txt_data
    ##################################################################    
    def generate_venezuela_to_others(self):
        # Obtener recibos de salario
        payslips = self._get_payslips()
        txt_data = ''
        if payslips:

            # *** Registro de cabecera ***
            
            # 1. Preparacion de campos
            vat_digits = ''
            nationality = ''
            if self.env.company.vat:
                nationality = self.env.company.vat[0:1]
                vat_digits = self.env.company.vat.replace('-', '')
                if len(self.env.company.vat) > 10:
                    vat_digits = f'{vat_digits[1:10]}' 
                else:
                    vat_digits = f'{vat_digits[1:len(vat_digits)]}'
            
            # 2. Construccion de linea
            create_date = fields.Date.context_today(self)

            txt_data += f'{"HEADER":<8}{self.name:0>8}{"112856":0>8}{nationality:<1}{vat_digits:0>9}{create_date:%d/%m/%Y}{create_date:%d/%m/%Y}\n'
            sequence = 0
            for payslip in payslips:
                self.employee_payroll_validations(payslip)
                sequence += 1
                txt_data += self._txt_prepare_data_venezuela_to_others(payslip, sequence)
            
            # *** Registro de credito ***
            total = f'{sum(payslips.mapped("net_wage")):.2f}'.replace('.', ',')
            txt_data += f'{"TOTAL":<8}{len(payslips):0>5}{len(payslips):0>5}{total:0>18}\n'
        return txt_data
        
    def generate_venezuela(self):
        
        # Obtener recibos de salario
        payslips = self._get_payslips()
        txt_data = ''
        if payslips:

            # *** Registro de cabecera ***
            
            # 1. Preparacion de campos
            
            if payslips[0].company_id.name and len(payslips[0].company_id.name) > 40:
                company_name = payslips[0].company_id.name[0:70]
            else:
                company_name = payslips[0].company_id.name
            
            if self.bank_account_id.sanitized_acc_number and len(self.bank_account_id.sanitized_acc_number) == 20:
                bank_acc = self.bank_account_id.sanitized_acc_number
            else:
                bank_acc = '0000'
            valid_date = self.valid_date.strftime('%d/%m/%y')
            total_payroll = 0.0
            for payslip in payslips:
                total_payroll += payslip.net_wage
            total_payroll = f'{total_payroll:.2f}'.replace('.', '')    
            
            # 2. Construccion de linea
            txt_data += f'{"H":<1}{company_name:<40}{bank_acc:<20}{self.name[len(self.name)-2:len(self.name)]:<2}'
            txt_data += f'{valid_date:<8}{total_payroll:0>13}{"03291":<5}{"":<1}\n'
            
            for payslip in payslips:
                
                # *** Registro detalle ***
                self.employee_payroll_validations(payslip)
                txt_data += self._txt_prepare_data_venezuela(payslip)
        return txt_data
    ##################################################################
    def _fiscal_payroll_validations(self, employee, totals):
        
        if not employee.country_id:
            raise ValidationError(("Por favor establezca la nacionalidad del empleado: %s.") % (employee.name))
        if not employee.identification_id:
            raise ValidationError(("Por favor establezca la C.I. para el empleado: %s.") % (employee.name))
        elif not employee.identification_id.isnumeric():
            raise ValidationError(("La C.I. del empleado: %s, debe contener solo números.") % (employee.name))
        elif 5 < len(employee.identification_id) > 8:
            raise ValidationError(("La C.I. del empleado: %s, debe tener una longitud entre 5 y 8 dígitos.") % (employee.name))
        words = employee.name.split(' ')
        names = tuple(filter(lambda x: x != '', words))   
        if len(names) < 2:
            raise ValidationError(("El empleado: %s, debe tener almenos un nombre y un apellido.") % (employee.name))  
        elif len(names) == 2:
            # Se asume que se trata del primer nombre y aprimer pellido 
            if not(1 < len(names[0]) < 26):
                raise ValidationError(("El primer nombre del empleado: %s, debe tener una longitud entre 2 y 25 caracteres.") % (employee.name))
            if not(1 < len(names[1]) < 26):
                raise ValidationError(("El primer apellido del empleado: %s, debe tener una longitud entre 2 y 25 caracteres.") % (employee.name))   
        elif len(names) == 3:
            # Se asume que se trata de primer nombre, primer apellido y un segundo apellido
            if not(1 < len(names[0]) < 26):
                raise ValidationError(("El primer nombre del empleado: %s, debe tener una longitud entre 2 y 25 caracteres.") % (employee.name))
            if not(1 < len(names[1]) < 26):
                raise ValidationError(("El primer apellido del empleado: %s, debe tener una longitud entre 2 y 25 caracteres.") % (employee.name))   
        else:
            # Se asume que las primeras 4 palabras son el primer nombre, segundo nombre, primer apellido, segundo apellido       
            if not(1 < len(names[0]) < 26):
                raise ValidationError(("El primer nombre del empleado: %s, debe tener una longitud entre 2 y 25 caracteres.") % (employee.name))
            if not(1 < len(names[2]) < 26):
                raise ValidationError(("El primer apellido del empleado: %s, debe tener una longitud entre 2 y 25 caracteres.") % (employee.name))   
        if totals[employee.id] <= 0:
            raise ValidationError(("La sumatoria de los montos totales de las lineas con categoria 'Básico' y 'Basico3' en los Recibos de Salario del empleado: %s, debe ser un monto mayor que cero.") % (employee.name))
        elif len(f'{totals[employee.id]:.2f}'.replace('.', '')) > 18:
            raise ValidationError(("La sumatoria de los montos totales de las lineas con categoria 'Básico' y 'Basico3' en los Recibos de Salario del empleado: %s, no debe tener mas de 18 digitos.") % (employee.name))
        if not employee.contract_id.date_start:
            raise ValidationError(("Por establecer la fecha de inicio de contrato del empleado:") % (employee.name))
    
    def _remove_accents(self, s):

        trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
        s = normalize('NFKC', normalize('NFKD', s).translate(trans_tab))
        return s

    def generate_fiscal_payroll(self):
        
        txt_data = ''
        totals = self._get_import_total_by_employee()
        ids = [k for k in totals] 
        employees = self.env['hr.employee'].search([('id', 'in', ids)])
        i = 0
        identification_ids = []
        for employee in employees:
            # Validaciones
            if employee.identification_id in identification_ids:
                raise ValidationError(("La cedula de identidad del empleado %s, se encuentra duplicada en el archivo a generar.") % (employee.name))
            else:
                identification_ids.append(employee.identification_id)
            self._fiscal_payroll_validations(employee, totals)
            # Preparacion de campos
            nationality = 'V' if employee.country_id.name == 'Venezuela' else 'E'
            employee_id = employee.identification_id
            words = self._remove_accents(employee.name).upper().split(' ')
            names = tuple(filter(lambda x: x != '', words)) 
            second_name = ''
            second_surname = ''
            if len(names) == 2:
                first_name = names[0][:25]
                first_surname = names[1][:25]
            elif len(names) == 3:
                first_name = names[0][:25]
                first_surname = names[1][:25]
                second_surname = names[2][:25] 
            else:    
                first_name = names[0][:25] 
                second_name = names[1][:25] 
                first_surname = names[2][:25] 
                second_surname = names[3][:25]
            debt_amount = f'{totals[employee.id]:.2f}'.replace('.', '')  
            entry_date = employee.contract_id.date_start.strftime('%d%m%Y')
            exit_date = employee.contract_id.date_end.strftime('%d%m%Y') if employee.contract_id.date_end else ''

            #Contruccion de lineas
            txt_data += f'{nationality}{","}{employee_id}{","}{first_name}{","}{second_name}{","}'
            txt_data += f'{first_surname}{","}{second_surname}{","}{debt_amount}{","}{entry_date}{","}'
            if exit_date:
                txt_data += f'{exit_date}'
            i += 1
            if i < len(employees):
                txt_data += '\n'
        return txt_data

