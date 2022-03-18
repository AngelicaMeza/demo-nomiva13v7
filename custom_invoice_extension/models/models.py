# -*- coding: utf-8 -*-

from odoo import models, fields, api
from num2words import lang_ES_VE, num2words
from odoo.tools.translate import _
from odoo.exceptions import UserError

class report_functions(models.Model):
    _inherit = "account.move"

    def get_rate(self, rate_dict):
        return list(rate_dict.values())[0]
    # campo que almacena el cambio de numeros a palabras
    son = fields.Char(compute="compute_numbers_to_words")

    # agregado de campo identificador al modulo de la factura
    debit_note= fields.Boolean(string="Nota de debito", default=False)

    # transformacion de cantidades en numeros a palabras
    def compute_numbers_to_words(self):
        # conversion
        for rec in self:
            converted_amount = rec.currency_id._convert(rec.amount_total, rec.company_currency_id, rec.company_id, rec.date)
            amount_txt = num2words(converted_amount, lang='es_VE', to="currency")
        
        # arreglos en el string resultado por cambios en la nomenclatura
        
        # cambio a monedas actuales actual:(fuertes -> soberanos) futuro:(fuertes/soberanos -> digitales)
        if rec.company_currency_id.name == "VES" and rec.company_currency_id.symbol == "Bs." and rec.company_currency_id.id == 3:
            if amount_txt.find("fuertes") != -1:
                amount_txt = amount_txt.replace("fuertes", "digitales")
                monetary_name = "digitales"
            else:
                amount_txt = amount_txt.replace("un bolívar", "un bolívar digital")
                monetary_name= "digital"
        # "de" despues de un numero redondo de millon o millones
        if "millones" in amount_txt[len(amount_txt)-27:] or "millón" in amount_txt[len(amount_txt)-27:]:
            amount_txt = amount_txt[:len(amount_txt)-17] + "de " + amount_txt[len(amount_txt)-17:]
        
        # representacion de los centimos
        amount_txt = amount_txt.replace("centavos", "ctms")
        
        
        # arreglo de representacion de parte decimal
        if "ctms" in amount_txt:
            y_position = amount_txt.find(monetary_name)+len(monetary_name)+1
            amount_txt = amount_txt[:y_position] + "con" + amount_txt[y_position+1:]

        rec.son = amount_txt

    # obtener el record del dollar para relizar operaciones de cambio de moneda en la factura
    def get_dollar_id(self):
        return self.env['res.currency'].search([('name', '=', 'USD'), ('id', '=', 2), ('symbol', '=', '$')])

# modificacion del wizard de creacion de notas de debito
# para añadir el campo identificador
class AccountDebitNote(models.TransientModel):
    _inherit="account.debit.note"

    def _prepare_default_values(self, move):
        if move.type in ('in_refund', 'out_refund'):
            type = 'in_invoice' if move.type == 'in_refund' else 'out_invoice'
        else:
            type = move.type
        default_values = {
                'ref': '%s, %s' % (move.name, self.reason) if self.reason else move.name,
                'date': self.date or move.date,
                'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
                'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
                'invoice_payment_term_id': None,
                'debit_origin_id': move.id,
                'type': type,
                'debit_note': True,
            }
        if not self.copy_lines or move.type in [('in_refund', 'out_refund')]:
            default_values['line_ids'] = [(5, 0, 0)]
        return default_values