# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from osv import osv, fields
import netsvc
import pooler
from tools.translate import _
import decimal_precision as dp
from osv.orm import browse_record, browse_null

class purchase_order(osv.osv):
    _inherit='purchase.order'
    
    _columns={
           'purchase_compare_line': fields.one2many('purchase.compare', 'order_id', 'Purchase Compare',),
           'payment_term': fields.many2one('account.payment.term', 'Payment Term',readonly=True, states={'draft':[('readonly',False)]},
            help="If you use payment terms, the due date will be computed automatically at the generation "\
                "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "\
                "The payment term may compute several due dates, for example 50% now, 50% in one month."),
            'move_po_notes': fields.char("Notes", size=64),
            'journal_id':fields.many2one('account.journal', 'Payment Method', required=False),
            'dest_material_addrs' : fields.many2one('res.partner.address', 'Goods Receive Address',),
            'dest_invoice_addrs' : fields.many2one('res.partner.address', 'Invoice Receive Address',),
              }
            
    
#    def action_invoice_create(self, cr, uid, ids, *args):
#        res = False
#
#        journal_obj = self.pool.get('account.journal')
#        for o in self.browse(cr, uid, ids):
#            il = []
#            todo = []
#            for ol in o.order_line:
#                todo.append(ol.id)
#                if ol.product_id:
#                    a = ol.product_id.product_tmpl_id.property_account_expense.id
#                    if not a:
#                        a = ol.product_id.categ_id.property_account_expense_categ.id
#                    if not a:
#                        raise osv.except_osv(_('Error !'), _('There is no expense account defined for this product: "%s" (id:%d)') % (ol.product_id.name, ol.product_id.id,))
#                else:
#                    a = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category').id
#                fpos = o.fiscal_position or False
#                a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, a)
#                il.append(self.inv_line_create(cr, uid, a, ol))
#
#            a = o.partner_id.property_account_payable.id
#            journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase'),('company_id', '=', o.company_id.id)], limit=1)
#            if not journal_ids:
#                raise osv.except_osv(_('Error !'),
#                    _('There is no purchase journal defined for this company: "%s" (id:%d)') % (o.company_id.name, o.company_id.id))
#            inv = {
#                'name': o.partner_ref or o.name,
#                'reference': o.partner_ref or o.name,
#                'account_id': a,
#                'type': 'in_invoice',
#                'partner_id': o.partner_id.id,
#                'currency_id': o.pricelist_id.currency_id.id,
#                'address_invoice_id': o.partner_address_id.id,
#                'address_contact_id': o.partner_address_id.id,
#                'journal_id': len(journal_ids) and journal_ids[0] or False,
#                'origin': o.name,
#                'invoice_line': il,
#                'fiscal_position': o.fiscal_position.id or o.partner_id.property_account_position.id,
#                'payment_term': o.payment_term.id or o.partner_id.property_payment_term and o.partner_id.property_payment_term.id or False,
#                'company_id': o.company_id.id,
#            }
#            inv_id = self.pool.get('account.invoice').create(cr, uid, inv, {'type':'in_invoice'})
#            self.pool.get('account.invoice').button_compute(cr, uid, [inv_id], {'type':'in_invoice'}, set_total=True)
#            self.pool.get('purchase.order.line').write(cr, uid, todo, {'invoiced':True})
#            self.write(cr, uid, [o.id], {'invoice_ids': [(4, inv_id)]})
#            res = inv_id
#        return res
    def do_merge(self, cr, uid, ids, context=None):
        """
        To merge similar type of purchase orders.
        Orders will only be merged if:
        * Purchase Orders are in draft
        * Purchase Orders belong to the same partner
        * Purchase Orders are have same stock location, same pricelist
        Lines will only be merged if:
        * Order lines are exactly the same except for the quantity and unit

         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: the ID or list of IDs
         @param context: A standard dictionary

         @return: new purchase order id

        """
        wf_service = netsvc.LocalService("workflow")
        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'move_dest_id', 'account_analytic_id'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

    # compute what the new orders should contain

        new_orders = {}
        print "xxxxxxxxxxxxxxxxx"
        for porder in [order for order in self.browse(cr, uid, ids, context=context) if order.state == 'draft']:
            order_key = make_key(porder, ('partner_id', 'location_id', 'pricelist_id'))
            new_order = new_orders.setdefault(order_key, ({}, []))
            new_order[1].append(porder.id)
            order_infos = new_order[0]
            
            if not order_infos:
                order_infos.update({
                    'origin': porder.origin,
                    'date_order': time.strftime('%Y-%m-%d'),
                    'partner_id': porder.partner_id.id,
                    'partner_address_id': porder.partner_address_id.id,
                    'dest_address_id': porder.dest_address_id.id,
                    'warehouse_id': porder.warehouse_id.id,
                    'location_id': porder.location_id.id,
                    'pricelist_id': porder.pricelist_id.id,
                    'state': 'draft',
                    'order_line': {},
                    'notes': '%s' % (porder.notes or '',),
                    'fiscal_position': porder.fiscal_position and porder.fiscal_position.id or False,
                })
            else:
                if porder.notes:
                    order_infos['notes'] = (order_infos['notes'] or '') + ('\n%s' % (porder.notes,))
                if porder.origin:
                    order_infos['origin'] = (order_infos['origin'] or '') + ' ' + porder.origin

            for order_line in porder.order_line:
                line_key = make_key(order_line, ('name', 'date_planned', 'taxes_id', 'price_unit', 'notes', 'product_id', 'move_dest_id', 'account_analytic_id'))
                o_line = order_infos['order_line'].setdefault(line_key, {})
                if o_line:
                    # merge the line with an existing line
                    o_line['product_qty'] += order_line.product_qty * order_line.product_uom.factor / o_line['uom_factor']
                else:
                    # append a new "standalone" line
                    for field in ('product_qty', 'product_uom'):
                        field_val = getattr(order_line, field)
                        if isinstance(field_val, browse_record):
                            field_val = field_val.id
                        o_line[field] = field_val
                    o_line['uom_factor'] = order_line.product_uom and order_line.product_uom.factor or 1.0


        allorders = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_orders.iteritems():
            print "ini===============>>"
            # skip merges with only one order
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # cleanup order line data
            for key, value in order_data['order_line'].iteritems():
                del value['uom_factor']
                value.update(dict(key))
            order_data['order_line'] = [(0, 0, value) for value in order_data['order_line'].itervalues()]

            # create the new order
            neworder_id = self.create(cr, uid, order_data)
            orders_info.update({neworder_id: old_ids})
            allorders.append(neworder_id)
            print "neworder_id:", neworder_id
            
            # make triggers pointing to the old orders point to the new order
            for old_id in old_ids:
                wf_service.trg_redirect(uid, 'purchase.order', old_id, neworder_id, cr)
                wf_service.trg_validate(uid, 'purchase.order', old_id, 'purchase_cancel', cr)
                
        #####################################################
        
        print "order_data:", order_data
        pr_seq_len = len(order_infos['origin'].split(" "))
        
        for number in range(pr_seq_len):
            
            pr_name = order_infos['origin'].split(" ")[number]
            
            if pr_name:
                
                pur_req_search = self.pool.get('purchase.requisition').search(cr, uid, [('name','=',pr_name)])
                pur_req_browse = self.pool.get('purchase.requisition').browse(cr, uid, pur_req_search)
                
                for pr_id in pur_req_browse:
                    
                    po_search = self.search(cr, uid, [('requisition_id','=',pr_id.id)])
                    po_browse = self.browse(cr, uid, po_search)
                        
                    for po in po_browse:
                        new_po = self.browse(cr, uid, [neworder_id])
                        for new_po in new_po:
                            po_new = new_po.name
                        self.write(cr, uid, [po.id],{'move_po_notes':po_new})
                        
        #####################################################
        
        return orders_info
    
    _defaults = {
            #'dest_material_addrs' : lambda self,cr,uid,c: self.pool.get('res.company').browse(cr, uid, None)[0].partner_id.id,
                 }
    
purchase_order()

class purchase_order_line(osv.osv):
    _inherit="purchase.order.line"
    
    _columns = {
            'ket' : fields.char('Keterangan', size=300, required=False),
                }
purchase_order_line()

class purchase_compare(osv.osv):
    _name = 'purchase.compare'
    
    _columns = {
            'order_id': fields.many2one('purchase.order', 'Order Reference', select=True, required=True, ondelete='cascade'),
            'name':fields.char("Desciption", size=64),
            'cheapest_price_partner': fields.char('Partner Cheapest',size=64,),
            'cheapest_price':fields.float("Cheapest Price"),
            'qty_cheapest_price':fields.float("Cheapest Price Quantity"),
            'date_cheapest_price': fields.date('Date',),
            'last_price_partner': fields.char('Partner Last',size=64,),
            'last_price':fields.float("Last Price"),
            'qty_last_price':fields.float("Lastest Price Quantity"),
            'date_last_price': fields.date('Date',),
            
                }
purchase_compare()