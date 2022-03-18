# -*- coding: utf-8 -*-

from ast import literal_eval
from os import write
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

# check de indentificacion de operacion de identificacion
class requisition(models.Model):
    _inherit = "stock.picking.type"

    # requisition_VV= fields.Boolean(default=False)
    # requisition_AC= fields.Boolean(default=False)
    requisition_op = fields.Boolean(string="Operación de requisición", default=False)
    requisition_warehouse = fields.Many2one("stock.warehouse" ,string="Almacén de requisición")

    def am_i_admin(self):
        for record in self:
            if record.env.user.has_group('stock.group_stock_manager'):
                record.im_admin = True
            else:
                record.im_admin = False

    im_admin = fields.Boolean(compute=am_i_admin )
    
    def _compute_picking_count_approval(self):
        for record in self:
            record.count_picking_waiting_approval = record.env['stock.picking'].search(['&',('state', '=', "waiting_approval_r"), ('picking_type_id', '=', record.id)], count=True)

    def _compute_picking_count_approval_all(self):
        for record in self:
            record.count_picking_waiting_approval_all = record.env['stock.picking'].search(['&',('state', '=', "waiting_approval_all"), ('picking_type_id', '=', record.id)], count=True)

    def _compute_picking_count_approved(self):
        for record in self:
            record.count_picking_approved = record.env['stock.picking'].search(['&',('state', '=', "approved"), ('picking_type_id', '=', record.id)], count=True)

    def get_action_picking_tree_waiting_approval(self):
        return self._get_action('requisition.action_picking_tree_waiting_approval')

    def get_action_picking_tree_approved(self):
        return self._get_action('requisition.action_picking_tree_approved')

    def get_action_picking_tree_waiting_approval_all(self):
        return self._get_action('requisition.action_picking_tree_waiting_approval_all')
    
    count_picking_waiting_approval_all = fields.Integer(compute=_compute_picking_count_approval_all, stored=True, readonly=True)
    count_picking_waiting_approval = fields.Integer(compute=_compute_picking_count_approval, stored=True, readonly=True)
    count_picking_approved = fields.Integer(compute=_compute_picking_count_approved, stored=True, readonly=True)

    def _get_action(self, action_xmlid):
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['display_name'] = self.display_name

        default_immediate_tranfer = False
        if self.env['ir.config_parameter'].sudo().get_param('stock.no_default_immediate_tranfer'):
            default_immediate_tranfer = False

        context = {
            'search_default_picking_type_id': [self.id],
            'default_picking_type_id': self.id,
            'default_immediate_transfer': default_immediate_tranfer,
            'default_company_id': self.company_id.id,
        }

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        return action

# codigo de identificacion unico de almacen
class warehouse(models.Model):
    _inherit="stock.warehouse"

    requisitions = fields.Boolean(string="Acepta requisiciones", required=True, stored=True )
    warehouse_code = fields.Integer(string="código de almacén", required=True, stored=True )
    _sql_constraints=[('warehouse_code_int_uniq','UNIQUE(warehouse_code)','El código de almacén debe ser único'),]

    @api.constrains('warehouse_code')
    def _check_warehouse_code(self):
        if self.warehouse_code > 999 or self.warehouse_code < 1:
            raise ValidationError('El código no puede ser cero (0) o tener mas de 3 dígitos')

# selector de almacen por usuario
class users_warehouse(models.Model):
    _inherit="res.users"

    user_warehouse_id = fields.Many2many("stock.warehouse")

# modificacion del flujo de aprobaciones
class aprove_flow(models.Model):
    _inherit="stock.picking"

    # flujo de aprobaciones
    #begining
    # usuario de aprobacion
    approve_user = fields.Many2one(
        'res.users',
        string='Aprobado por',
        readonly=True,
        copy=False,)

    requi = fields.Boolean(related="picking_type_id.requisition_op", string="requi")

    # agregado de estado Esperando aprobación
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('waiting_approval_r', 'Esperando aprobación'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('waiting_approval_all', 'Esperando aprobación'),
        ('approved', 'Aprobado'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")
    
    # modificacion del flujo de estados
    @api.depends('move_type', 'immediate_transfer', 'move_lines.state', 'move_lines.picking_id')
    def _compute_state(self):
        ''' State of a picking depends on the state of its related stock.move
        - Draft: only used for "planned pickings"
        - Waiting: if the picking is not ready to be sent so if
        - (a) no quantity could be reserved at all or if
        - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
        - Waiting another move: if the picking is waiting for another move
        - Ready: if the picking is ready to be sent so if:
        - (a) all quantities are reserved or if
        - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
        - Done: if the picking is done.
        - Cancelled: if the picking is cancelled
        '''
        for picking in self:
            if not picking.move_lines:
                picking.state = 'draft'
            elif any(move.state == 'draft' for move in picking.move_lines):  # TDE FIXME: should be all ?
                picking.state = 'draft'
            elif all(move.state == 'cancel' for move in picking.move_lines):
                picking.state = 'cancel'
            elif all(move.state in ['cancel', 'done'] for move in picking.move_lines):
                picking.state = 'done'
            else:
                relevant_move_state = picking.move_lines._get_relevant_state_among_moves()
                if picking.immediate_transfer and relevant_move_state not in ('draft', 'cancel', 'done'):
                    picking.state = 'assigned'
                elif relevant_move_state == 'partially_available':
                    picking.state = 'assigned'
                elif relevant_move_state == 'confirmed' and picking.state != "assigned" and picking.requi != False:
                    picking.state = 'waiting_approval_r'
                else:
                    picking.state = relevant_move_state

    def do_unreserve(self):
        for picking in self:
            picking.move_lines._do_unreserve()
            picking.package_level_ids.filtered(lambda p: not p.move_ids).unlink()
        self.state="confirmed"

    # accion del nuevo boton aprobar
    def action_approval(self):
        for picking in self:
            picking.approve_user = self.env.uid
            picking.state = 'confirmed'
    
    # ocultar el boton de editar segun condicion
    x_css = fields.Html(
        string='CSS',
        sanitize=False,
        compute='_compute_css',
        store=False,
    )
    @api.depends('state')
    def _compute_css(self):
        for application in self:
            if application.state not in ["draft", "waiting_approval_r"] and not (self.env.user.has_group('requisition.group_stock_edit_button') or self.env.user.has_group('stock.group_stock_manager')):
                application.x_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                application.x_css = False
    
    #end

    # cambios vale de entrega
    #begining
    # campos de informacion del conductor
    driver_name = fields.Char(string="Conductor")
    driver_identification = fields.Char(string="Cédula de identidad")
    vehicle_brand = fields.Char(string="Marca")
    vehicle_plate = fields.Char(string="Placa")
    vehicle_model = fields.Char(string="Modelo")
    vehicle_colour = fields.Char(string="Color")
    #end

    # calculo de las ubicaciones permitidas
    @api.depends('picking_type_id')
    def compute_locations(self):
        if self.picking_type_id:
            for rec in self:
                for child in rec.env.user.user_warehouse_id:
                    self.warehouse_locations += child.lot_stock_id.compute_childs()
        else:
            self.warehouse_locations = False

    warehouse_locations = fields.One2many('stock.location','location_id', compute=compute_locations, readonly='True')

    def need_approve(self):
        for picking in self:
            picking.state = 'waiting_approval_all'

    def action_approval_all(self):
        for picking in self:
            picking.approve_user = self.env.uid
            picking.state = 'approved'


class stockmove(models.Model):
    _inherit="stock.move"

    def _search_picking_for_assignation(self):
        self.ensure_one()
        picking = self.env['stock.picking'].search([
                ('group_id', '=', self.group_id.id),
                ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_dest_id.id),
                ('picking_type_id', '=', self.picking_type_id.id),
                ('name', '=', self.origin),
                ('printed', '=', False),
                ('immediate_transfer', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned'])], limit=1)
        return picking

class stocklocation(models.Model):
    _inherit="stock.location"

    def compute_childs(self):
        childs = self.browse(self.id)
        for child in self.child_ids:
            if child.child_ids:
                childs += child.compute_childs()
            else:
                childs += self.browse(child.id)
        return childs
        
        # for rec in self:
        #     childs = rec.browse(rec.id)
        #     childs += rec.browse(rec.child_ids.ids)
        #     for child in childs:
        #         if child.child_ids:
        #             childs += self.browse(child.child_ids.ids)
        #     return(childs)

    def compute_field(self):
        for warehouse in self.env.user.user_warehouse_id:
            self.childs_ids_all += warehouse.lot_stock_id.compute_childs()

    childs_ids_all = fields.One2many('stock.location', 'location_id', compute=compute_field)


class PurchaseRequisitionInherit(models.Model):

    _inherit = "purchase.requisition"

    def _get_picking_in(self):

        pick_in = self.env['stock.picking.type'].search(
            [('warehouse_id','in', self.env.user.user_warehouse_id.ids), ('code', '=', 'incoming')],
            limit=1,
        )
        return pick_in

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True, default=_get_picking_in)
