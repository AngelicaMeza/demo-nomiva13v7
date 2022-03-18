

from odoo import models, api, _
from odoo.exceptions import UserError, Warning
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RepComprobanteIslr(models.AbstractModel):
    _name = 'report.custom_dispatch_guide.report_dispatch_guide'

    # _inherit = 'report.abstract_report'
    # _template = 'l10n_ve_withholding_iva.template_wh_vat'

    @api.model
    def _get_report_values(self, docids, data=None):
      
        data = {'form': self.env['dispatch.guide'].browse(docids)}

        if data['form'].state == 'done':
            return {
                'docs': data['form'],
                'model': self.env['report.custom_dispatch_guide.report_dispatch_guide'],
                'doc_model': self.env['report.custom_dispatch_guide.report_dispatch_guide'],
           
            }
        else:
            raise UserError(_("The Dispatch Guide must be in the Done state in order to print"))
