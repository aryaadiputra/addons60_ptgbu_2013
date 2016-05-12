# -*- encoding: utf-8 -*-

import time
import netsvc
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta

class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"
    _columns = {
        'line_ids' : fields.one2many('purchase.requisition.line','requisition_id','Products to Purchase',states={'done': [('readonly', True)], 'in_progress': [('readonly', True)]}),       
        'origin': fields.char('Origin', size=32, required=True),
    }
    
    
purchase_requisition()
    
class purchase_requisition_line(osv.osv):
    _inherit = "purchase.requisition.line"
    _columns = {
        'ket' : fields.char('Keterangan', size=300, required=False),
        'qty_remain': fields.float('Remain', required=False, digits=(16,2)),
        'qty_order': fields.float('Order', required=False, digits=(16,2)),
        'line_ids' : fields.one2many('purchase.requisition.line','requisition_id','Products to Purchase',states={'done': [('readonly', True)], 'in_progress': [('readonly', True)]}),       
    }

    _defaults = {
                 'qty_order': 0.0,
                 'qty_remain': 0.0,
                 }

    
purchase_requisition_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    _columns = {
        "rfq_number" : fields.char("Request for Quotation", size=64),
                }
    
    def generate(self, cr, uid, ids, context=None):
        
        a = self.browse(cr, uid, ids)
        
        for b in a:
            b.requisition_id.id
            
            for l in b.order_line:
                self.pool.get('purchase.order.line').unlink(cr, uid, l.id, context=context)
        
        pr_id = self.pool.get('purchase.requisition').browse(cr, uid, b.requisition_id.id)
        
        pr_line = pr_id.line_ids
        
        for line in pr_line:
            product_qty = line.product_qty - line.qty_order
            print "line.product_uom_id.id::", line.product_uom_id.name
            print "IDS:::", ids[0]
            y = {
                'order_id': ids[0],
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_uom': line.product_uom_id.id,
                'price_unit': line.price,
                'product_qty': product_qty,
                'date_planned': time.strftime('%Y-%m-%d %H:%M:%S'),
                
                 }
            
            self.pool.get('purchase.order.line').create(cr, uid, y)
        
        return True

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        print "wkf_confirm_order"
        todo = []
        order = 0.0
        remain = 0.0
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(_('Error !'),_('You can not confirm purchase order without Purchase Order Lines.'))
            for line in po.order_line:
                if po.requisition_id :
                    for req in po.requisition_id.line_ids:
                        print "ID", req.id, "Line ID", line.id
                        if (line.product_id.id == req.product_id.id and line.pr_line_id.id == req.id) or (line.product_id.id == req.product_id.id and line.pr_line_id == False): 
                            order = req.qty_order + line.product_qty
                            remain = req.product_qty - order
                            print "req.product_qty - order", req.product_qty, order, remain
                            if line.product_id.uom_id.id != line.product_id.uom_po_id.id : 
                                order = req.qty_order + line.product_qty/line.product_id.factor
                                remain = req.product_qty - order
                            print "+++++++++++++++",req.qty_order,line.product_qty,line.product_id.factor,remain
                            
                            if remain < 0:
                                print "aaaaa((0"
                                #raise osv.except_osv(_('Error !'),_('Qty Purchase Requisiton tidak tersisa ! '))
                            self.pool.get('purchase.requisition.line').write(cr, uid, [req.id], {'qty_order': order, 'qty_remain': remain })   
                if line.state=='draft':
                    todo.append(line.id)
            message = _("Purchase order '%s' is confirmed.") % (po.name,)
            self.log(cr, uid, po.id, message)
        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            if po.name == "/":
                self.write(cr, uid, [id], {'name' : self.pool.get('ir.sequence').get(cr, uid, 'purchase.order')})
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid, 'purchase_order_release_date' : time.strftime('%Y-%m-%d')})
        return True
    
    def action_cancel_cancel(self, cr, uid, ids, *args):
        print "???------------------------->>"
        if not len(ids):
            return False
        self.write(cr, uid, ids, {'state':'cancel'})
        #===================================================================
        for purchase in self.browse(cr, uid, ids):
            for x in purchase.order_line :
                if purchase.requisition_id.id:
                    id_line = self.pool.get('purchase.requisition.line').search(cr,uid,[('product_id','=',x.product_id.id),('requisition_id','=',purchase.requisition_id.id)])
                    if id_line:
                        data = self.pool.get('purchase.requisition.line').browse(cr,uid,id_line)[0] 
                        qty = x.product_qty 
     
                        if x.product_id.uom_id.id != x.product_id.uom_po_id.id :
                            qty =  x.product_qty / x.product_id.factor
                        #print data.qty_remain,data.qty_order
                        if data.qty_remain <= data.qty_order:
                            self.pool.get('purchase.requisition.line').write(cr,uid,id_line,{'qty_order':data.qty_order - qty, 'qty_remain':data.qty_remain + qty})
        #===================================================================
        return True
        
    def action_cancel_draft(self, cr, uid, ids, *args):
        print "action_cancel_draft",ids
        if not len(ids):
            return False
        self.write(cr, uid, ids, {'state':'draft','shipped':0})
        wf_service = netsvc.LocalService("workflow")
        for p_id in ids:
            # Deleting the existing instance of workflow for PO
            wf_service.trg_delete(uid, 'purchase.order', p_id, cr)
            wf_service.trg_create(uid, 'purchase.order', p_id, cr)
        #===================================================================
#        for purchase in self.browse(cr, uid, ids):
#            for x in purchase.order_line :
#                if purchase.requisition_id.id:
#                    id_line = self.pool.get('purchase.requisition.line').search(cr,uid,[('product_id','=',x.product_id.id),('requisition_id','=',purchase.requisition_id.id)])
#                    data = self.pool.get('purchase.requisition.line').browse(cr,uid,id_line)[0] 
#                    qty = x.product_qty 
# 
#                    if x.product_id.uom_id.id != x.product_id.uom_po_id.id :
#                        qty =  x.product_qty / x.product_id.factor
#                    #print data.qty_remain,data.qty_order
#                    if data.qty_remain <= data.qty_order:
#                        self.pool.get('purchase.requisition.line').write(cr,uid,id_line,{'qty_order':data.qty_order - qty, 'qty_remain':data.qty_remain + qty})
#        #===================================================================
        for (id,name) in self.name_get(cr, uid, ids):
            message = _("Purchase order '%s' has been set in draft state.") % name
            self.log(cr, uid, id, message)
        return True
    
    def action_cancel(self, cr, uid, ids, context=None):
        print "action_cancel---------------------->>>"
        for purchase in self.browse(cr, uid, ids, context=context):
            for pick in purchase.picking_ids:
                if pick.state not in ('draft','cancel'):
                    raise osv.except_osv(
                        _('Could not cancel purchase order !'),
                        _('You must first cancel all picking attached to this purchase order.'))
            for pick in purchase.picking_ids:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
            for inv in purchase.invoice_ids:
                if inv and inv.state not in ('cancel','draft'):
                    raise osv.except_osv(
                        _('Could not cancel this purchase order !'),
                        _('You must first cancel all invoices attached to this purchase order.'))
                if inv:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)

            for x in purchase.order_line :
                if purchase.requisition_id.id:
                    id_line = self.pool.get('purchase.requisition.line').search(cr,uid,[('product_id','=',x.product_id.id),('requisition_id','=',purchase.requisition_id.id)])
                    data = self.pool.get('purchase.requisition.line').browse(cr,uid,id_line)[0] 
                    qty = x.product_qty 
                    if x.product_id.uom_id.id != x.product_id.uom_po_id.id :
                        qty =  x.product_qty / x.product_id.factor
                    self.pool.get('purchase.requisition.line').write(cr,uid,id_line,{'qty_order':data.qty_order - qty, 'qty_remain':data.qty_remain + qty})
                    
        self.write(cr,uid,ids,{'state':'cancel'})
        for (id,name) in self.name_get(cr, uid, ids):
            message = _("Purchase order '%s' is cancelled.") % name
            self.log(cr, uid, id, message)
        
        return True
    
    _defaults = {
            "name" : "/",
            "rfq_number" : lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'request.for.quotation'),
                 }
    
    _sql_constraints = [
        ('name_uniq', 'unique(rfq_number)', 'Request for Quotation Number must be unique !'),
    ]

purchase_order()

