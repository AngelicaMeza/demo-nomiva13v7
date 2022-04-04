# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError

class HrEmployeePrivate(models.Model):

    _inherit = "hr.employee"
    
    # Definicion del campo numero de cuenta de Empleado

    bank_account_number = fields.Char(
        string='Número de cuenta',
        domain="[('partner_id', '=', address_home_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        groups="hr.group_hr_user",
        tracking=True,
        help='Cuenta bancaria de salario del empleado')

    account_type = fields.Selection([
        ('corriente', 'Corriente'),
        ('ahorro', 'Ahorro')], string="Tipo de cuenta", groups="hr.group_hr_user", help='Tipo de cuenta bancaria del empleado') 

    bank_id = fields.Many2one('res.bank', 'Banco', help="Banco al que pertence la cuenta bancaria del beneficiario.")

    @api.onchange('bank_id')
    def onchange_bank_id(self):
        if self.bank_id and self.bank_id.bic == False:
            raise exceptions.ValidationError("Por favor establezca el Código de identificación bancaria (BIC/SWIFT) para el banco seleccionado")