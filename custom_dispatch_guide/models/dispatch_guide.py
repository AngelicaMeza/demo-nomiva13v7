# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class DispatchGuide(models.Model):
    """ Modelo orden de despachos. """
    _name = 'dispatch.guide'
    _description = 'Despacho'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
    ], string='State', required=True, default='draft', copy=False)
    name = fields.Char('Name', default='Nuevo', readonly=True)
    date = fields.Date('Date', default=lambda self: fields.datetime.now(), readonly=True)
    dispatch_type = fields.Selection([
        ('sale', 'Orden de Entrega'),
        ('proforma', 'Proforma')
    ], string='Dispatch_type',default='sale',required=True)
    driver = fields.Char(string="Name driver", required=True)
    # driver= fields.Many2one('hr.employee', string='Name driver',required=True)
    identification_driver = fields.Char(string='Identification', required=True)
    vehicle_brand = fields.Char('Vehicle brand')
    vehicle_model = fields.Char('Vehicle model')
    vehicle_colour = fields.Char('Vehicle Colour')
    vehicle_plate = fields.Char('Vehicle plate')
    notes = fields.Text('Observations')
    dispatch_lines_ids = fields.One2many('dispatch.guide.line', 'dispatch_id', string='Lines guide')

    @api.model
    def create(self, vals):
        new_id = super().create(vals)
        new_id.name = self.env['ir.sequence'].next_by_code('despatch.number')
        return new_id

    def action_done(self):
        if not self.dispatch_lines_ids:
            raise ValidationError(_('''it has no loaded dispatch lines'''))
        if not self.identification_driver:
            raise ValidationError(_('''El conductor asignado no posee cédula de identidad'''))
        
        # bultos_vacios = ''
        
        # for lines in self.dispatch_lines_ids:
        #     if lines.package == 0:
        #         bultos_vacios += '%s, ' % lines.sale_order_id.name

        # if bultos_vacios:
        #     raise ValidationError(_('Los números de pedido %s no tienen bultos cargados' % bultos_vacios))

        return self.write({'state': 'done'})

    def action_draft(self):
        return self.write({'state': 'draft'})

    def unlink(self):
        for guide in self:
            if guide.state not in ('draft'):
                raise ValidationError(_('''Unable to delete dispatch guide in done status''' ))
        return models.Model.unlink(self)

    def action_add_lines(self):
        ctx = self._context.copy()
        ctx['id_dispatch'] = self.id
        return {
            'name': _('Add dispatch Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'dispatch.lines.wizard',
            'view_mode': 'form',
            'context': ctx,
            'target': 'new',
        }

    @api.onchange('dispatch_lines_ids')
    def no_repeat_lines(self):
        if self.dispatch_lines_ids:
            lines = [items.sale_order_id for items in self.dispatch_lines_ids]
            last_item = lines.pop()
            if last_item in lines:
                raise ValidationError(_('El número de pedido %s ya fue seleccionado' % last_item.name))

    # @api.onchange('driver')
    # def driver_onchange(self):
    #     if self.driver:
    #         self.vehicle_brand = self.driver.vehicle_brand
    #         self.vehicle_model = self.driver.vehicle_model
    #         self.vehicle_colour = self.driver.vehicle_colour
    #         self.vehicle_plate = self.driver.vehicle_plate

class DispatchGuideLine(models.Model):
    """ Modelo orden de despachos. """
    _name = 'dispatch.guide.line'
    _description = 'Despacho'

    # @api.depends('sale_order_id')
    # def _compute_zone(self):
    #     for rec in self:
    #         if rec.sale_order_id:
    #             if rec.sale_order_id.zone_id.zone_code == '00':
    #                 rec.zone=rec.sale_order_id.zone_id.name
    #             else:    
    #                 rec.zone=rec.sale_order_id.zone_id.name + '-' + str(rec.sale_order_id.zone_id.zone_code)

    dispatch_id = fields.Many2one('dispatch.guide', 'Dispatch guide',copy=False,ondelete="cascade")
    sale_order_id = fields.Many2one('sale.order', 'Number order',domain="[('state','in',['sale','done'])]",required=True)
    partner = fields.Char(related='sale_order_id.partner_id.name',string='Partner')
    shipping_address = fields.Char(compute='_compute_display_address', string='Dirección de entrega')
    phone = fields.Char(related='sale_order_id.partner_id.phone',string='Phone')
    # zone = fields.Char('Zone',store=True, compute='_compute_zone')
    # package = fields.Integer('Package')

    @api.depends('sale_order_id.partner_shipping_id')
    def _compute_display_address(self):
        for record in self:
            record.shipping_address = record.sale_order_id.partner_shipping_id._display_address(without_company=True)
    # @api.onchange('package')
    # def _onchange_package(self):
    #     for rec in self:
    #         if rec.package < 0:
    #             rec.package=0

