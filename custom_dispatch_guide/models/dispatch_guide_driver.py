# from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError

# class DispatchGuideDriver(models.Model):
# 	_inherit = 'hr.employee'

# 	is_driver = fields.Boolean(string='Es conductor')
# 	identification_driver = fields.Char(string='Cédula de identidad', size=8)
# 	vehicle_brand = fields.Char(string='Marca')
# 	vehicle_model = fields.Char(string='Modelo')
# 	vehicle_colour = fields.Char(string='Color')
# 	vehicle_plate = fields.Char(string='Placa')

# 	@api.constrains('identification_driver')
# 	def validation_document_ident(self):
# 		if self.identification_driver and (not self.identification_driver.isdigit() or not len(self.identification_driver) in range(7,9)):
# 			raise ValidationError(_('La cédula del conductor tiene un formato incorrecto. Debe ser un valor numérico no negativo entre 7 y 8 dígitos. Ej: 12345678'))