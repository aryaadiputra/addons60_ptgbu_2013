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

class budget_info_po(osv.osv):
    _name = 'budget.info.po'
    _description = 'Budget Info PO'
    
    def _amount_budget(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            date_end = line.order_id.date_order[:4]
            #date_from = str(line.period_id.date_start)
            #date_to = str(line.period_id.date_stop)
            #date_from = line.period_id.date_start
            #date_to = line.period_id.date_stop
            
            #acc_ids = line.budget_item_id.
            cr.execute("select sum(a.amount) as amount_budget from ad_budget_line a, account_period b "
                       " where a.analytic_account_id = %s and a.period_id = b.id and to_char(b.date_start,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
#            result = cr.dictfetchone()
#            #print "line.id",line.id
#            if result['amount_budget'] is None:
#                result.update({'amount_budget': 0.0})
#            result.update({'amount_budget':abs(result['amount_budget'])})
#            res.update({line.id:result})
            amount = cr.fetchone()
            amount = amount[0] or 0.00
            res[line['id']] = amount
        return res
    
    def _amount_spent(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            date_end = line.order_id.date_order[:4]
            #acc_ids = line.budget_item_id.
            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line "
                   "WHERE account_id=%s AND to_char(date,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_real = cr.fetchone()
            amount_real = amount_real[0] or 0.00
            #print amount_real
            
            cr.execute("select SUM(x.product_qty*x.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y "
                        " where y.state in ('approved') and x.order_id = y.id "
                        "  and x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_virtual1 = cr.fetchone()
            amount_virtual1 = amount_virtual1[0] or 0.00
            
            cr.execute("SELECT SUM(a.product_qty*a.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y, stock_move a "
                     " WHERE x.order_id = y.id and a.purchase_line_id = x.id and a.state in ('cancel','done') and "
                     " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
                       "  where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('approved') and b.state in ('open','paid','cancel')) and a.id=y.id) and "
                       " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            amount_virtual2 = cr.fetchone()
            amount_virtual2 = amount_virtual2[0] or 0.00
            res[line['id']] = (amount_virtual1 - amount_virtual2) + abs(amount_real)
        return res
    
    def _amount_current(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            purchase_id = line.order_id.id
            date_end = line.order_id.date_order[:4]
            #acc_ids = line.budget_item_id.
            cr.execute("select sum(a.product_qty * a.price_unit) from purchase_order c, purchase_order_line a, budget_info_po b "
                       " where c.id=a.order_id and a.order_id = %s and a.account_analytic_id=b.account_analytic_id and b.account_analytic_id = %s and c.id = b.order_id and to_char(c.date_order,'yyyy') = %s ",(purchase_id,str(account_analytic_id),str(date_end),))
            amount = cr.fetchone()
            amount = amount[0] or 0.00
            res[line['id']] = amount
        return res
    
    def _amount_utilized(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            purchase_id = line.order_id.id
            date_end = line.order_id.date_order[:4]
            #acc_ids = line.budget_item_id.
            
            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line "
                   "WHERE account_id=%s AND to_char(date,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_real = cr.fetchone()
            amount_real = amount_real[0] or 0.00
            
            #===================================================================
            # cr.execute("SELECT SUM(x.product_qty*x.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y "
            #        " WHERE x.state in ('approved','confirmed','done') and x.order_id = y.id and "
            #        " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
            #            " where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('confirmed','approved','done') and b.state not in ('open','paid','cancel')) and a.id=y.id) and "
            #           " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            # amount_spent = cr.fetchone()
            # amount_spent = amount_spent[0] or 0.00
            #===================================================================
            cr.execute("select SUM(x.product_qty*x.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y "
                        " where y.state in ('approved') and x.order_id = y.id "
                        "  and x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_virtual1 = cr.fetchone()
            amount_virtual1 = amount_virtual1[0] or 0.00
            
            cr.execute("SELECT SUM(a.product_qty*a.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y, stock_move a "
                     " WHERE x.order_id = y.id and a.purchase_line_id = x.id and a.state in ('cancel','done') and "
                     " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
                       "  where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('approved') and b.state in ('open','paid','cancel')) and a.id=y.id) and "
                       " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            amount_virtual2 = cr.fetchone()
            amount_virtual2 = amount_virtual2[0] or 0.00
            amount_spent = amount_virtual1 - amount_virtual2
            #res[line['id']] = amount_spent
            
            cr.execute("select sum(a.product_qty * a.price_unit) from purchase_order c, purchase_order_line a, budget_info_po b "
                       " where c.id=a.order_id and a.order_id = %s and a.account_analytic_id=b.account_analytic_id and b.account_analytic_id = %s and c.id = b.order_id and to_char(c.date_order,'yyyy') = %s ",(purchase_id,str(account_analytic_id),str(date_end),))
            amount_current = cr.fetchone()
            amount_current = amount_current[0] or 0.00
            
            res[line['id']] = amount_spent + amount_current + abs(amount_real)
        return res
 
    def _amount_remain(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            material_req_id = line.order_id.id
            date_end = line.order_id.date_order[:4]
            #acc_ids = line.budget_item_id.
            print "***account_analytic_id***", account_analytic_id, date_end
            
            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line "
                   "WHERE account_id=%s AND to_char(date,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_real = cr.fetchone()
            amount_real = amount_real[0] or 0.00
            
            cr.execute("select sum(a.amount) as amount_budget from ad_budget_line a, account_period b "
                       " where a.analytic_account_id = %s and a.period_id = b.id and to_char(b.date_start,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            amount_budget = cr.fetchone()
            amount_budget = amount_budget[0] or 0.00
            print "amount_budget ::::", amount_budget
            #===================================================================
            # cr.execute("SELECT SUM(x.product_qty*x.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y "
            #        " WHERE x.state in ('approved','confirmed','done') and x.order_id = y.id and "
            #        " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
            #            " where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('confirmed','approved','done') and b.state not in ('open','paid','cancel')) and a.id=y.id) and "
            #           " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            # amount_spent = cr.fetchone()
            # amount_spent = amount_spent[0] or 0.00
            #===================================================================
            cr.execute("select SUM(x.product_qty*x.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y "
                        " where y.state in ('approved') and x.order_id = y.id "
                        "  and x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_virtual1 = cr.fetchone()
            amount_virtual1 = amount_virtual1[0] or 0.00
            
            cr.execute("SELECT SUM(a.product_qty*a.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y, stock_move a "
                     " WHERE x.order_id = y.id and a.purchase_line_id = x.id and a.state in ('cancel','done') and "
                     " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
                       "  where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('approved') and b.state in ('open','paid','cancel')) and a.id=y.id) and "
                       " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            amount_virtual2 = cr.fetchone()
            amount_virtual2 = amount_virtual2[0] or 0.00
            amount_spent = amount_virtual1 - amount_virtual2
            #res[line['id']] = amount_spent
            
            cr.execute("select sum(a.product_qty * a.price_unit) from purchase_order c, purchase_order_line a, budget_info_po b "
                       " where c.id=a.order_id and a.order_id = %s and a.account_analytic_id=b.account_analytic_id and b.account_analytic_id = %s and c.id = b.order_id and to_char(c.date_order,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
            amount_current = cr.fetchone()
            amount_current = amount_current[0] or 0.00
            
            res[line['id']] = amount_budget - (amount_spent + amount_current + abs(amount_real))
            #res[line['id']] = amount_budget
        print "RES++++++++++++++", res
        return res
    

    
    _columns = {
        'name': fields.char('Name', 64),
        'account_analytic_id':fields.many2one('account.analytic.account', 'Analytic Account',),
        'order_id': fields.many2one('purchase.order', 'Material Request'),
        #'budget_line_id': fields.many2one('ad_budget.line', 'Budget Lines'),
        'amount_budget': fields.function(_amount_budget, digits=(20,0), method=True, string='Budget Amount', type='float'),
        'amount_spent': fields.function(_amount_spent, digits=(20,0), method=True, string='Budget Spent', type='float'),
        'amount_current': fields.function(_amount_current, digits=(20,0), method=True, string='Budget Current', type='float'),
        'amount_utilized': fields.function(_amount_utilized, digits=(20,0), method=True, string='Budget Utilized', type='float'),
        'amount_remain': fields.function(_amount_remain, digits=(20,0), method=True, string='Budget Remain', type='float'),
    }
budget_info_po()

class budget_note_po(osv.osv):
    _name = 'budget.note.po'
    
    _columns = {
            'order_id'      : fields.many2one('purchase.order', 'Purchase ID'),
            'date'          : fields.datetime('Notes Date',required=False),
            'description'   : fields.char('Description', size=300),
            'user'          : fields.many2one('res.users','User Name'),
                }
    
budget_note_po()

class purchase_order(osv.osv):

    _inherit = "purchase.order"
    _description = "Purchase Order"
    _order = "name desc"
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.product_qty, order.partner_address_id.id, line.product_id.id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res
    
    STATE_SELECTION = [
        ('draft', 'Request for Quotation'),
        ('wait', 'Waiting'),
        ('confirmed', 'Waiting Procurement Manager Approve'),
        ('confirmed2', 'Waiting Head of Procurement Division'),
        ('confirmed3', 'Waiting Head of Division Approve'),
        ('confirmed4', 'Waiting CEO Approve'),
        ('approved', 'Approved'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

    _columns = {
        'state'                 : fields.selection(STATE_SELECTION, 'State', readonly=True, help="The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception.", select=True),
        'budget_info_ids_po'    : fields.many2many('budget.info.po', 'budget_info_rel_po', 'order_id', 'budget_info_id_po', 'Budget Line', readonly=True),
        'budget_note'           : fields.text('Budget Note'),
        'budget_note_line_ids'  : fields.one2many('budget.note.po', 'order_id', 'Budget Note History'),
        
        #######DICOUNT#####################
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Purchase Price'), string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax"),
        'amount_tax': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Purchase Price'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Purchase Price'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums",help="The total amount"),
        ###################################
            }
    
    #################################################
    def create_date_manager_proc(self, cr, uid, ids):
        self.write(cr, uid, ids, {'manager_proc_app_date':time.strftime('%Y-%m-%d')})
        return True
    
    def create_date_div_proc(self, cr, uid, ids):
        self.write(cr, uid, ids, {'head_of_div_proc_app_date':time.strftime('%Y-%m-%d')})
        return True
    
    def create_date_div_req(self, cr, uid, ids):
        self.write(cr, uid, ids, {'head_of_div_req_app_date':time.strftime('%Y-%m-%d')})
        return True
    
    def create_date_ceo(self, cr, uid, ids):
        self.write(cr, uid, ids, {'ceo':time.strftime('%Y-%m-%d')})
        return True
    ##################################################
    
    def check_note(self,cr, uid, ids, *args):
        po = self.browse(cr, uid, ids)[0]
        budget_note = po.budget_note
        print "budget_note )))))))))))))))))))))))", budget_note
        if not budget_note:
            raise osv.except_osv(_('Please Insert Your Notes !'), _('Please Insert Your Notes In Budget Note.'))
        else:
            note_line_hstry = {
                                   'user'           : uid,
                                   'description'    : po.budget_note,
                                   'date'           : time.strftime('%Y-%m-%d %H:%M:%S'),
                                   'order_id'       : ids[0],
                      }
            self.pool.get('budget.note.po').create(cr, uid, note_line_hstry)
            #self.write(cr, uid, ids, {'budget_note' : ''})
        return True
    
    def check_budget_ceo_old(self,cr, uid, ids, *args):
        print "OLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA CEO"
        #print "remain_budget------------------------------->>", remain_budget
        mr_total = 0.0
        for po in self.browse(cr, uid, ids):
            amount_total = po.amount_total
            for order_line in po.order_line:
                if not order_line.account_analytic_id.id:
                    print "000000000000000000000000000"
                    return True
                else:
                    print "000000000007777777777777777777"
                    remain_budget = self.amount_remain(cr, uid, ids, )
        print "remain_budget------------------------------->>", remain_budget, "VS", amount_total
        mr_id = po.requisition_id.int_move_id.material_req_id.id
        for mr_lines in self.pool.get('material.requisition').browse(cr, uid, mr_id).line_ids:
            mr_total = mr_total + mr_lines.subtotal
            #print "mr_total+++++++++++++++++++++++++++++++++>>", mr_total
        #print "SISA bUDGET :::", (remain_budget + (remain_budget * 5/100))
        #print "amount_total +++++>>>>", amount_total
        #remain_budget_tol = (remain_budget + (remain_budget * 5/100))
        #print "remain_budget_tol=======>>>", remain_budget_tol
        
        #######################Over Budget########################
        if amount_total > (remain_budget + (remain_budget * 5 /100)):
            return True
        elif amount_total - remain_budget == 10000000:
            return True
        ############################################################
        #######################MR Vs PO############################
        elif amount_total > (mr_total + (mr_total * 10/100)):
            return True
        elif amount_total > (mr_total + 10000000):
            return True
        ############################################################
        #######################Amount Total >=100000000########################
        if amount_total >= 100000000:
            return True
        ############################################################
        return False
    
    def check_budget_kadiv_old(self,cr, uid, ids, *args):
        print "OLEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE KADIV"
        #print "remain_budget------------------------------->>", remain_budget
        mr_total = 0.0
        for po in self.browse(cr, uid, ids):
            amount_total = po.amount_total
            for order_line in po.order_line:
                if not order_line.account_analytic_id.id:
                    #print "000000000000000000000000000"
                    return True
                else:
                    remain_budget = self.amount_remain(cr, uid, ids, )
        #print "remain_budget------------------------------->>", remain_budget
        mr_id = po.requisition_id.int_move_id.material_req_id.id
        for mr_lines in self.pool.get('material.requisition').browse(cr, uid, mr_id).line_ids:
            mr_total = mr_total + mr_lines.subtotal
            #print "mr_total+++++++++++++++++++++++++++++++++>>", mr_total
        #print "SISA bUDGET :::", (remain_budget + (remain_budget * 5/100))
        #print "amount_total +++++>>>>", amount_total
        #remain_budget_tol = (remain_budget + (remain_budget * 5/100))
        #print "remain_budget_tol=======>>>", remain_budget_tol
        
        #######################Over Budget########################
        if amount_total > remain_budget:
            return True
        ############################################################
        #######################Over Budget########################
        if amount_total > (mr_total + (mr_total * 5/100)):
            self.check_note(cr, uid, ids)
            return True
        elif amount_total > (mr_total + 10000000):
            return True
        ############################################################
        #self.write(cr, uid, ids,{'budget_note' : ''})
        return False
    
    def check_budget_proc_manager(self,cr, uid, ids, *args):
        print "Proc Manager"
        for po in self.browse(cr, uid, ids):
            current_currency    = po.pricelist_id.currency_id.id
            amount_total        = po.amount_total
        print "current_currency", current_currency
        if current_currency != 12 and amount_total > 1000:
            return True
        elif amount_total > 10000000:
            return True
        
        return False
    
    
    def check_budget_proc_div(self,cr, uid, ids, *args):
        for po in self.browse(cr, uid, ids):
            current_currency    = po.pricelist_id.currency_id.id
            amount_total        = po.amount_total
            
        if current_currency != 12 and amount_total > 10000:
            return True
        elif amount_total > 10000000:
            return True
        
        return False
    
    
    def check_budget_kadiv(self,cr, uid, ids, *args):
        print "OLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA CEO"
        #print "remain_budget------------------------------->>", remain_budget
        mr_total = 0.0
        for po in self.browse(cr, uid, ids):
            amount_total = po.amount_total
            for order_line in po.order_line:
                if not order_line.account_analytic_id.id:
                    print "000000000000000000000000000"
                    return True
                else:
                    print "000000000007777777777777777777"
                    remain_budget = self.amount_remain(cr, uid, ids, )
        print "remain_budget------------------------------->>", remain_budget, "VS", amount_total
        if po.requisition_id:
            mr_id = po.requisition_id.int_move_id.material_req_id.id
            for mr_lines in self.pool.get('material.requisition').browse(cr, uid, mr_id).line_ids:
                mr_total = mr_total + mr_lines.subtotal
            #print "mr_total+++++++++++++++++++++++++++++++++>>", mr_total
        #print "SISA bUDGET :::", (remain_budget + (remain_budget * 5/100))
        #print "amount_total +++++>>>>", amount_total
        #remain_budget_tol = (remain_budget + (remain_budget * 5/100))
        #print "remain_budget_tol=======>>>", remain_budget_tol
        #line.price * line.product_qty > (amount_residual + (amount_residual * 5/100)) or (line.price * line.product_qty) - amount_residual > 100000000:
        #######################Over Budget########################
        if amount_total > remain_budget:
            return True
        elif amount_total - remain_budget > 50000000:
            return True
        ############################################################
        #######################MR Vs PO############################
#        if mr_id:
#            if amount_total > (mr_total + (mr_total * 10/100)):
#                return True
#            elif amount_total > (mr_total + 10000000):
#                return True
        ############################################################
        #######################Amount Total >=100000000########################
#        if amount_total >= 100000000:
#            return True
        ############################################################
        return False
    
    def check_budget_ceo(self,cr, uid, ids, *args):
        print "OLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA CEO"
        #print "remain_budget------------------------------->>", remain_budget
        ##############Variabel untuk Minum amount Per lIne######################
        var_amount = 50000000
        ########################################################################
        mr_total = 0.0
        for po in self.browse(cr, uid, ids):
            date_order = po.date_order
            amount_total = po.amount_total
            for order_line in po.order_line:
                subtotal = order_line.product_qty * order_line.price_unit 
                if not order_line.account_analytic_id.id:
                    if not order_line.account_analytic_id.id and subtotal > var_amount:
                        return True
                if order_line.account_analytic_id.id:
                    if self.amount_budget_plan(cr, uid, ids, order_line.account_analytic_id.id, date_order, context=None) == 0.00 and subtotal > var_amount:
                        return True
                    elif self.amount_budget_plan(cr, uid, ids, order_line.account_analytic_id.id, date_order, context=None) > 0.00:
                        remain_budget = self.amount_remain(cr, uid, ids, )
                        if po.requisition_id:
                            mr_id = po.requisition_id.int_move_id.material_req_id.id
                            for mr_lines in self.pool.get('material.requisition').browse(cr, uid, mr_id).line_ids:
                                mr_total = mr_total + mr_lines.subtotal
                            
                        #######################Over Budget########################
                        if amount_total > (remain_budget + (remain_budget * 5 /100)):
                            return True
                        elif amount_total - remain_budget >= 100000000:
                            return True
                    ############################################################
                    #######################MR Vs PO############################
            #        if mr_id:
            #            if amount_total > (mr_total + (mr_total * 10/100)):
            #                return True
            #            elif amount_total > (mr_total + 10000000):
            #                return True
                    ############################################################
                #######################Amount Total >=100000000########################
                if amount_total >= 100000000:
                    return True
                ############################################################
        return False
    
    
    def compute(self, cr, uid, ids, context=None):
        print "ddeeedfff"
        #mr_total = 0.0
        if ids:
            mat = int(str(ids[0]))
            cr.execute('delete from budget_info_po where order_id = %s ',(mat,))
            
        for lines in self.browse(cr, uid, ids)[0].order_line:
#            mr_id = lines.order_id.requisition_id.int_move_id.material_req_id.id
#            for mr_lines in self.pool.get('material.requisition').browse(cr, uid, mr_id).line_ids:
#                mr_total = mr_total + mr_lines.subtotal
#            print "mr_total", mr_total
            purchase_id = ids[0]
            print "purchase_id :::", purchase_id
            #subtotal = lines.product_qty * lines.price
            account_analytic_id = lines.account_analytic_id.id
            print "account_analytic_id :::", account_analytic_id
            #print "subtotal :::", lines.account_analytic_id.id,ids[0]
            #subtotal.update(subtotal)
            
            #self.pool.get('purchase.order.line').write(cr, uid, [lines.id], context=context)
            budget_obj =  self.pool.get('budget.info.po')
            if account_analytic_id and purchase_id:
                info = budget_obj.search(cr, uid, [('account_analytic_id','=', account_analytic_id),('order_id','=',purchase_id)])
                if not info:
                    budgets = {
                        'name': '/',
                        'account_analytic_id': account_analytic_id,
                        'order_id': purchase_id,
                    }
                    budget_id = budget_obj.create(cr, uid, budgets)
                    cr.execute('INSERT INTO budget_info_rel_po (order_id, budget_info_id_po) values (%s,%s)',(purchase_id,budget_id))
        return True
    
    def button_dummy(self, cr, uid, ids, context=None):
        print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        self.compute(cr, uid, ids, context)
        #self.amount_remain(cr, uid, ids, context)
        return True
    
    def amount_budget_plan(self, cr, uid, ids, account_analytic_id, date, context=None):
        res={}
        date = date[:4]
        cr.execute("SELECT SUM(amount) FROM ad_budget_line bl, account_period ap "
                   "WHERE bl.analytic_account_id = %s and bl.period_id = ap.id and to_char(ap.date_start,'yyyy') = %s", (str(account_analytic_id),str(date),))
        
                
        budget_plan = cr.fetchone()
        budget_plan = budget_plan[0] or 0.00
        return budget_plan
    
    def amount_remain(self, cr, uid, ids, context=None):
        res={}
        for po in self.browse(cr, uid, ids, context=None):
            for line in po.order_line:
                account_analytic_id = line.account_analytic_id.id
                material_req_id = line.order_id.id
                date_end = line.order_id.date_order[:4]
                #acc_ids = line.budget_item_id.
                if not account_analytic_id:
                    return False
                    
                print "***account_analytic_id***", account_analytic_id, date_end
                
                cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line "
                       "WHERE account_id=%s AND to_char(date,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
                amount_real = cr.fetchone()
                amount_real = amount_real[0] or 0.00
                
                cr.execute("select sum(a.amount) as amount_budget from ad_budget_line a, account_period b "
                           " where a.analytic_account_id = %s and a.period_id = b.id and to_char(b.date_start,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
                amount_budget = cr.fetchone()
                amount_budget = amount_budget[0] or 0.00
                print "amount_budget ::::", amount_budget
                #===================================================================
                # cr.execute("SELECT SUM(x.product_qty*x.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y "
                #        " WHERE x.state in ('approved','confirmed','done') and x.order_id = y.id and "
                #        " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
                #            " where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('confirmed','approved','done') and b.state not in ('open','paid','cancel')) and a.id=y.id) and "
                #           " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
                # amount_spent = cr.fetchone()
                # amount_spent = amount_spent[0] or 0.00
                #===================================================================
                cr.execute("select SUM(x.product_qty*x.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y "
                            " where y.state in ('approved') and x.order_id = y.id "
                            "  and x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
                amount_virtual1 = cr.fetchone()
                amount_virtual1 = amount_virtual1[0] or 0.00
                
                cr.execute("SELECT SUM(a.product_qty*a.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y, stock_move a "
                         " WHERE x.order_id = y.id and a.purchase_line_id = x.id and a.state in ('cancel','done') and "
                         " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
                           "  where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('approved') and b.state in ('open','paid','cancel')) and a.id=y.id) and "
                           " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
                amount_virtual2 = cr.fetchone()
                amount_virtual2 = amount_virtual2[0] or 0.00
                amount_spent = amount_virtual1 - amount_virtual2
                #res[line['id']] = amount_spent
                
                cr.execute("select sum(a.subtotal) from material_requisition c, material_requisition_line a, budget_info b "
                           " where c.id=a.requisition_id and a.requisition_id = %s and a.account_analytic_id=b.account_analytic_id and b.account_analytic_id = %s and c.id = b.material_req_id and to_char(c.date_end,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
                amount_current = cr.fetchone()
                amount_current = amount_current[0] or 0.00
                
                res[line['id']] = amount_budget - (amount_spent + amount_current + abs(amount_real))
                remain_budget = amount_budget - (amount_spent + abs(amount_real))
                #res[line['id']] = amount_budget
        print "RES++++++++++++++", res
        print "remain_budget ::::>>>", remain_budget
        return remain_budget
    
purchase_order()

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    
    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        print "ssssssssss"
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.product_qty)
            print "taxes------------------->>", taxes
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    
    _columns = {
            'discount': fields.float('Discount (%)', digits=(16,2)),
            'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute= dp.get_precision('Purchase Price')),
                }
purchase_order_line()