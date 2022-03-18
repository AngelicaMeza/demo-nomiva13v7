# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def ret_and_reconcile(self, pay_amount, pay_account_id,
        pay_journal_id, writeoff_acc_id,
        writeoff_journal_id, date,
        name, to_wh,type_retencion):

        move = super().ret_and_reconcile(pay_amount, pay_account_id, pay_journal_id, writeoff_acc_id,
            writeoff_journal_id, date, name, to_wh,type_retencion)
        
        if type_retencion in ('wh_islr', 'wh_iva'):
            move.write({
                'use_multirate': self.use_multirate,
                'rate_id': self.rate_id,
                'use_manual_rate': self.use_manual_rate,
                'manual_rate': self.manual_rate,
            })

        return move