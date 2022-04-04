from odoo import models, fields

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    is_payroll_account = fields.Boolean(string="Cuenta de nomina", default=False, help="Indica si la cuenta bancaria está destinada a pago de nóminas")
