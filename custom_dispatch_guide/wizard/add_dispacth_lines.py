# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class DispatchLinesWizard(models.TransientModel):
	_name = 'dispatch.lines.wizard'
	_description = 'dispatch wizard'

	sale_order_id = fields.Many2many('sale.order', string='Number',domain="[('state','in',['sale','done'])]",required=True)

	def create_lines(self):
		id_dispatch=self._context.get('id_dispatch')
		dispatch_line = self.env['dispatch.guide.line'].search([('dispatch_id', '=', id_dispatch)])
		list_dispatch = [record.sale_order_id.id for record in dispatch_line]
		sale_ordes_repeat = ''
		
		for lines in self.sale_order_id:
			if lines.id in list_dispatch:
				sale_ordes_repeat += '%s, ' % lines.name
			else:
				if lines.id:
					vals = {
						'dispatch_id': id_dispatch,
						'sale_order_id': lines.id
					}

					dispatch_line.create({
						'dispatch_id':id_dispatch,
						'sale_order_id': lines.id
					})
		
		if sale_ordes_repeat != '':
			raise ValidationError(_('Los números de pedido ' + sale_ordes_repeat + 'ya se encuentran agregados. Elimínelos antes de continuar.'))
		return True