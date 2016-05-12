#from osv import fields, osv
#from tools.translate import _
#import pooler

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from osv import fields, osv
from tools.translate import _
import netsvc
import tools
import decimal_precision as dp
import logging
import pooler

class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
                'analytic_id'       : fields.many2one('account.analytic.account', 'Analytic Account'),
                'info'              : fields.char('Information', size=300),
                'product_id'        : fields.many2one('product.product', 'Product', required=True, select=True, states={'done': [('readonly', True)]}),
                'detail'            : fields.text('Detail'),
    }
    
    def action_cancel(self, cr, uid, ids, context=None):
        """ Cancels the moves and if all moves are cancelled it cancels the picking.
        @return: True
        """
        if not len(ids):
            return True
        if context is None:
            context = {}
        pickings = {}
        picking_obj = self.pool.get('stock.picking')
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('confirmed', 'waiting', 'assigned', 'draft'):
                if move.picking_id:
                    pickings[move.picking_id.id] = True
            if move.move_dest_id and move.move_dest_id.state == 'waiting':
                self.write(cr, uid, [move.move_dest_id.id], {'state': 'confirmed'})
                if context.get('call_unlink',False) and move.move_dest_id.picking_id:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
        self.write(cr, uid, ids, {'state': 'cancel', 'move_dest_id': False})
        if not context.get('call_unlink',False):
            for pick in picking_obj.browse(cr, uid, pickings.keys()):
                if all(move.state == 'cancel' for move in pick.move_lines):
                    picking_obj.write(cr, uid, [pick.id], {'state': 'cancel'})
                elif all(move.state in ['done','cancel'] for move in pick.move_lines):
                    picking_obj.write(cr, uid, [pick.id], {'state': 'done'})

        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_trigger(uid, 'stock.move', id, cr)
        return True
        
stock_move()

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    def action_cancel_draft(self, cr, uid, ids, context=None):
        for picking in self.browse(cr, uid, ids):
            for line in picking.move_lines:
                self.pool.get('stock.move').write(cr, uid, [line.id], {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for voucher_id in ids:
            wf_service.trg_create(uid, 'stock.picking', voucher_id, cr)
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        print "qqqqqqqqqqqqqqqqqq"
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty = {}
            prodlot_ids = {}
            product_avail = {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                #Commented in order to process the less number of stock moves from partial picking wizard
                #assert partial_data, _('Missing partial picking data for move #%s') % (move.id)
                product_qty = partial_data.get('product_qty') or 0.0
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom') or False
                product_price = partial_data.get('product_price') or 0.0
                product_currency = partial_data.get('product_currency') or False
                prodlot_id = partial_data.get('prodlot_id') or False
                prodlot_ids[move.id] = prodlot_id
                if move.product_qty == product_qty:
                    complete.append(move)
                elif move.product_qty > product_qty:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    if product.id in product_avail:
                        product_avail[product.id] += qty
                    else:
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, product_price)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                        if product.qty_available <= 0:
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context)[product.id]
                            new_std_price = ((amount_unit * product_avail[product.id])\
                                + (new_price * qty))/(product_avail[product.id] + qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})


            for move in too_few:
                product_qty = move_product_qty[move.id]

                if not new_picking:
                    prt_ids=[]
                    for pr_track in pick.purchase_req_tracking:
                        prt_ids.append(pr_track.id)
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick.type)),
                                'move_lines' : [],
                                'purchase_req' : [],
                                'purchase_req_tracking' : [(6,0,prt_ids)],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)

                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty' : move.product_qty - product_qty,
                            'product_uos_qty':move.product_qty - product_qty, #TODO: put correct uos_qty
                        })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                if prodlot_ids.get(move.id):
                    move_obj.write(cr, uid, [move.id], {'prodlot_id': prodlot_ids[move.id]})
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)


            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking])
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
            else:
                self.action_move(cr, uid, [pick.id])
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}
            print "LLLLLLLLLLLLLLLLLLLLL"
        return res
    
    def approval_action(self, cr, uid, ids, context=None):
        """ Changes picking state to approval.
        @return: True
        """
        self.write(cr, uid, ids, {'state':'approval'})
        return True
    
    def cancel_action(self, cr, uid, ids, context=None):
        """ Changes picking state to approval.
        @return: True
        """
        self.write(cr, uid, ids, {'state':'confirmed'})
        return True
    
    def action_assign(self, cr, uid, ids, *args):
        """ Changes state of picking to available if all moves are confirmed.
        @return: True
        """
        move_obj = self.pool.get('stock.move')
        for pick in self.browse(cr, uid, ids):
            move_ids = [x.id for x in pick.move_lines if x.state == 'confirmed']
            if not move_ids:
                raise osv.except_osv(_('Warning !'),_('Not enough stock, unable to reserve the products.'))
            move_obj.action_assign(cr, uid, move_ids)
            
            for pick2 in self.browse(cr, uid, ids):
                #print "NA", pick2.not_available
                for ml in pick2.move_lines:
                    #print 'ml.name',ml.product_id.name
                    if ml.state=='confirmed':
                        #print ml.state 
                        self.pool.get('stock.picking').write(cr,uid,ids,{'not_available':True})
                print "NA", pick2.not_available
        return True

    def goto_pr(self, cr, uid, ids, context=None):
        for sp in self.browse(cr,uid,ids):
            move    = sp.move_lines
            to_pr = []
            for sm in move:
                if sm.state=='confirmed':
                    to_pr.append(sm)
                    print 'to_pr',to_pr
            
#            if sp.material_req_id:
#                material_req_id = sp.material_req_id.id
#            else:
#                material_req_id = False
            
            data = {
                    'origin'            : sp.name,
                    'req_employee'      : sp.req_employee.id,
                    'int_move_id'       : sp.id,
                    ##################################################
                    'department'        : sp.req_employee.department_id.id,
                    'mr_description'    : sp.mr_description,
                    #'material_req_id'   : material_req_id,
                    ##################################################
                    }
            db_pool = pooler.get_pool(cr.dbname)
            pr_id   = db_pool.get('purchase.requisition').create(cr,uid,data)
            
            if len(to_pr)==0:
                self.pool.get('stock.picking').write(cr,uid,ids,{'not_available':False})
            else:
                for move_line in to_pr:
                    product_id      = move_line.product_id.id
                    product_qty     = move_line.product_qty
                    price           = move_line.price_unit
                    analytic_id     = move_line.analytic_id.id
                    product_uom_id  = move_line.product_uom.id
                    ket             = move_line.info
                    detail          = move_line.detail
            
                    pr_line = {
                               'product_id'         : product_id,
                               'product_qty'        : product_qty,
                               'requisition_id'     : pr_id,
                               'account_analytic_id': analytic_id,
                               'price'              : price,
                               'product_uom_id'     : product_uom_id,
                               'ket'                : ket,
                               'detail'             : detail,
                               }
                    
                    pr_line_id  = db_pool.get('purchase.requisition.line').create(cr,uid,pr_line)
                    #print "IDS :::", ids
                    self.pool.get('stock.picking').write(cr, uid, ids, {'pr_created':True,
                                                                        'purchase_req_tracking' : [(6,0,[pr_id])]})
                    #@self.pool.get('stock.picking').write(cr, uid, ids, {'not_available':False,'pr_created':True})
                    #self.pool.get('stock.picking').write(cr, uid, ids, {'pr_created':True})

            ret= {
                'name':_("Purchase Requisition"),
                'view_mode': 'form,tree',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'purchase.requisition',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'domain': '[]',
                'res_id': pr_id,
                'context': {}
            }
        
        return ret
    
    _columns = {
                'pr_created'        : fields.boolean('PR Created'),
                #'approved'          : fields.boolean('Approved'),
                'not_available'     : fields.boolean('NA'),
                'req_employee'      : fields.many2one('hr.employee', 'Request By', required=False, readonly=True),
                'material_req_id'   : fields.many2one('material.requisition', 'Material Requisition', readonly=True),
                'purchase_req'      : fields.one2many('purchase.requisition', 'int_move_id','Purchase Requisition'),
                'purchase_req_tracking': fields.many2many('purchase.requisition', 'stock_pr_rel', 'pr_id','stock_id', 'Purchase Requisition'),
                
                ##########################################################
                'mr_description'    : fields.char('Description', size=64),
                ##########################################################
                'state': fields.selection([
                ('draft', 'Draft'),
                ('auto', 'Waiting'),
                ('confirmed', 'Waiting Approval'),
                ('approval','Confirmed'),
                ('assigned', 'Available'),
                ('done', 'Done'),
                ('cancel', 'Cancelled'),
                ], 'State', readonly=True, select=True,
                help="* Draft: not confirmed yet and will not be scheduled until confirmed\n"\
                     "* Confirmed: still waiting for the availability of products\n"\
                     "* Available: products reserved, simply waiting for confirmation.\n"\
                     "* Waiting: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"\
                     "* Done: has been processed, can't be modified or cancelled anymore\n"\
                     "* Cancelled: has been cancelled, can't be confirmed anymore"),
                }
                ##########################################################
    _defaults ={
                'not_available'     : False,
                }
    
stock_picking()