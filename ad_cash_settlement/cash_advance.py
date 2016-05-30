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
from lxml import etree

import netsvc
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _

#class ticket_travel(osv.osv):
#    _name = "ticket.travel"
#    _description = "Ticket Travel"
#    
#    _columns = {
#            'tt_partner_id'            : fields.many2one('res.partner','Supplier'),
#            'tt_address_invoice_id'    : fields.many2one('res.partner.address','Invoice Address'),
#            'tt_account_id'            : fields.many2one('account.account', 'Account'),
#            'tt_date'                  : fields.datetime('Date'),
#            'tt_currency_id'           : fields.many2one('res.currency','Currency'),
#            'tt_name'                  : fields.char('Desciption', size=128),
#            'tt_line_ids'              : fields.one2many('ticket.travel.line','ticket_id','Lines'),
#                }
#ticket_travel()

class budget_info_ca(osv.osv):
    _name = 'budget.info.ca'
    _description = 'Budget Info'
    
    def _amount_budget(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            #date_end = line.voucher_id.date_end[:4]
            date_end = line.cash_advance_id.req_date[:4]
            #date_from = str(line.period_id.date_start)
            #date_to = str(line.period_id.date_stop)
            #date_from = line.period_id.date_start
            #date_to = line.period_id.date_stop
            #print "+++++++++++++++", account_analytic_id, date_end
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
            #print "amount", amount
            amount = amount[0] or 0.00
            res[line['id']] = amount
        return res
    
    def _amount_spent(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            #date_end = line.material_req_id.date_end[:4]
            date_end = line.cash_advance_id.req_date[:4]
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
            cash_advance_id = line.cash_advance_id.id
            date_end = line.cash_advance_id.req_date[:4]
            #acc_ids = line.budget_item_id.
            
            cr.execute("select sum(a.amount) from cash_advance c, cash_advance_line a, budget_info_ca b "
                       " where c.id=a.voucher_id and a.voucher_id = %s and a.account_analytic_id=b.account_analytic_id and b.account_analytic_id = %s and c.id = b.cash_advance_id and to_char(c.req_date,'yyyy') = %s ",(cash_advance_id,str(account_analytic_id),str(date_end),))
            
            amount1 = cr.fetchone()
            amount1 = amount1[0] or 0.00
            
#            cr.execute(" select sum(e.subtotal) from purchase_order a, purchase_requisition b, stock_picking c, material_requisition d, material_requisition_line e, budget_info f "
#                       " where a.requisition_id = b.id and b.int_move_id = c.id and c.material_req_id = d.id and a.state in ('done','approved') "
#                       " and d.id = f.material_req_id  and e.account_analytic_id = f.account_analytic_id and d.id = e.requisition_id "
#                       " and e.requisition_id = %s and f.account_analytic_id = %s and to_char(d.date_end,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
#            amount2 = cr.fetchone()
#            amount2 = amount2[0] or 0.00    
            amount2 = 0.00
            #print "xxxxxxxxxxxx",amount,material_req_id,str(account_analytic_id),str(date_end)
            res[line['id']] = amount1 - amount2
        return res
    
    def _amount_utilized(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            cash_advance_id = line.cash_advance_id.id
            date_end = line.cash_advance_id.req_date[:4]
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
            #===================================================================
            cr.execute("select sum(a.amount) from cash_advance c, cash_advance_line a, budget_info_ca b "
                       " where c.id=a.voucher_id and a.voucher_id = %s and a.account_analytic_id=b.account_analytic_id and b.account_analytic_id = %s and c.id = b.cash_advance_id and to_char(c.req_date,'yyyy') = %s ",(cash_advance_id,str(account_analytic_id),str(date_end),))
            
            amount1 = cr.fetchone()
            amount1 = amount1[0] or 0.00
            
#            cr.execute(" select sum(e.subtotal) from purchase_order a, purchase_requisition b, stock_picking c, material_requisition d, material_requisition_line e, budget_info f "
#                       " where a.requisition_id = b.id and b.int_move_id = c.id and c.material_req_id = d.id and a.state in ('done','approved') "
#                       " and d.id = f.material_req_id  and e.account_analytic_id = f.account_analytic_id and d.id = e.requisition_id "
#                       " and e.requisition_id = %s and f.account_analytic_id = %s and to_char(d.date_end,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
#            amount2 = cr.fetchone()
#            amount2 = amount2[0] or 0.00    
            amount2 = 0.00
            amount_current = amount1 - amount2
            #===================================================================
            
            res[line['id']] = amount_spent + amount_current + abs(amount_real)
        return res
    
    def _amount_remain(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            cash_advance_id = line.cash_advance_id.id
            date_end = line.cash_advance_id.req_date[:4]
            #acc_ids = line.budget_item_id.
            
            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line "
                   "WHERE account_id=%s AND to_char(date,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_real = cr.fetchone()
            amount_real = amount_real[0] or 0.00
            
            cr.execute("select sum(a.amount) as amount_budget from ad_budget_line a, account_period b "
                       " where a.analytic_account_id = %s and a.period_id = b.id and to_char(b.date_start,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            amount_budget = cr.fetchone()
            amount_budget = amount_budget[0] or 0.00
            
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
            #===================================================================
            cr.execute("select sum(a.amount) from cash_advance c, cash_advance_line a, budget_info_ca b "
                       " where c.id=a.voucher_id and a.voucher_id = %s and a.account_analytic_id=b.account_analytic_id and b.account_analytic_id = %s and c.id = b.cash_advance_id and to_char(c.req_date,'yyyy') = %s ",(cash_advance_id,str(account_analytic_id),str(date_end),))
            
            amount1 = cr.fetchone()
            amount1 = amount1[0] or 0.00
            
#            cr.execute(" select sum(e.subtotal) from purchase_order a, purchase_requisition b, stock_picking c, material_requisition d, material_requisition_line e, budget_info f "
#                       " where a.requisition_id = b.id and b.int_move_id = c.id and c.material_req_id = d.id and a.state in ('done','approved') "
#                       " and d.id = f.material_req_id  and e.account_analytic_id = f.account_analytic_id and d.id = e.requisition_id "
#                       " and e.requisition_id = %s and f.account_analytic_id = %s and to_char(d.date_end,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
#            amount2 = cr.fetchone()
#            amount2 = amount2[0] or 0.00    
            amount2 = 0.00
            amount_current = amount1 - amount2
            #print amount1,amount2,amount_current,amount_budget - (amount_spent + amount_current + abs(amount_real))
            #===================================================================
            res[line['id']] = amount_budget - (amount_spent + amount_current + abs(amount_real))
        return res
    
    _columns = {
        'name': fields.char('Name', 64),
        'account_analytic_id':fields.many2one('account.analytic.account', 'Analytic Account',),
        #'material_req_id': fields.many2one('material.requisition', 'Material Request'),
        'cash_advance_id': fields.many2one('cash.advance', 'Cash Advance', ondelete='cascade'),
        #'budget_line_id': fields.many2one('ad_budget.line', 'Budget Lines'),
        'amount_budget': fields.function(_amount_budget, digits=(20,0), method=True, string='Budget Amount', type='float'),
        'amount_spent': fields.function(_amount_spent, digits=(20,0), method=True, string='Budget Spent', type='float'),
        'amount_current': fields.function(_amount_current, digits=(20,0), method=True, string='Budget Current', type='float'),
        'amount_utilized': fields.function(_amount_utilized, digits=(20,0), method=True, string='Budget Utilized', type='float'),
        'amount_remain': fields.function(_amount_remain, digits=(20,0), method=True, string='Budget Remain', type='float'),
    }
budget_info_ca()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    _columns = {
            'advance_id' : fields.many2one('cash.advance', 'Advance ID'),
                }
account_invoice()

class parent_ticket_travel_line(osv.osv):
    _name = "parent.ticket.travel.line"
    _description = "Parent Ticket Travel Line"
    
    
    
    def _get_employee_id(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        print "IDS", ids
        for rec in self.browse(cr, uid, ids, context):
            res[rec.id] = 5
        return res

    _columns = {
            'advance_id'            : fields.many2one('cash.advance', 'Cash Advance', ondelete='cascade'),
            'partner_id'            : fields.many2one('res.partner','Supplier'),
            'address_invoice_id'    : fields.many2one('res.partner.address','Invoice Address'),
            'account_id'            : fields.many2one('account.account', 'Account'),
            'date'                  : fields.datetime('Date'),
            'currency_id'           : fields.many2one('res.currency','Currency'),
            'name'                  : fields.char('Desciption', size=128),
            'line_ids'              : fields.one2many('ticket.travel.line','parent_travel_id','Lines', required=True),
            #'department_id'         : fields.related('employee_id', 'department_id', relation='hr.department',type='many2one', string='Department',store=True, readonly=True), 
            #'employee_id'           : fields.many2one("hr.employee","Employee",required=True, readonly=True, states={"draft":[("readonly",False)]}),
            'employee_id'           : fields.many2one('hr.employee','Employee'),
            }
    
    def onchange_partner_id(self, cr, uid, ids, partner_id):
        invoice_addr_id = False
        contact_addr_id = False
        #pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(tt_partner_id)+'')])
        acc_id = False
        
        if partner_id:
            res = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact', 'invoice'])
            contact_addr_id = res['contact']
            invoice_addr_id = res['invoice']
            property_obj = self.pool.get('ir.property')
            
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            acc_id = p.property_account_payable.id
        
        result = {'value': {
            'address_contact_id': contact_addr_id,
            'address_invoice_id': invoice_addr_id,
            'account_id': acc_id,
            #'payment_term': partner_payment_term,
            #'fiscal_position': fiscal_position
            }}
        return result
    
    def onchange_get_employee(self, cr, uid, ids, employee_id, context=None):
        value={}
        if employee_id:
            value={'employee_id':employee_id}
#        print "ddddddddddddd", 
#        print "employee_id---------------->>", employee_id
#        self.write(cr, uid, ids, {'employee_id' : employee_id})
        return {'value':value}
    
parent_ticket_travel_line()

class ticket_travel_line(osv.osv):
    _name = "ticket.travel.line"
    _description = "Ticket Travel Line"
    
    _columns = {
            'parent_travel_id'      : fields.many2one('parent.ticket.travel.line','Parent'),
            'product_id'            : fields.many2one('product.product','Product'),
            'account_id'            : fields.many2one('account.account', 'Account'),
            'account_analytic_id'   : fields.many2one('account.analytic.account', 'Analytic Account'),
            'amount'                : fields.float('Price', digits_compute=dp.get_precision('Account')),
            'quantity'              : fields.float('Quantity'),
            'name'                  : fields.char('Desciption', size=128),
            'advance_type_id'       : fields.many2one('advance.type','Advance Type', ),
                }
    
    _defaults = {
            'quantity' : 1,
                 }
    
    
    def onchange_advance_type(self, cr, uid, ids, advance_type_id, employee_id, partner_id):
        employee        = self.pool.get('hr.employee')
        partner         = self.pool.get('res.partner')
        advance_type    = self.pool.get('advance.type')
        analytic        = self.pool.get('account.analytic.account')
        division        = False
        
        department     = employee.browse(cr, uid, employee_id).department_id.id
        #division       = employee.browse(cr, uid, employee_id).user_id.context_division_id.id
        
        if employee.browse(cr, uid, employee_id).user_id:
            division   = employee.browse(cr, uid, employee_id).user_id.context_division_id.id
        
        if advance_type_id:
            print "222222222"
            account_id = advance_type.browse(cr, uid, advance_type_id).account_id.id
            if department:
                analytic_search     = analytic.search(cr, uid, [('department_id','=',department),('budget_expense','=',account_id)])
            elif division:
                analytic_search     = analytic.search(cr, uid, [('division_id','=',division),('budget_expense','=',account_id)])
            else:
                raise osv.except_osv(_('Department or Division not Define'), _('Please Check your Department or Division'))
        
            check_pool_budget = self.pool.get('pool.budget').check_pool_account(cr, uid, ids, account_id, department)
        
            if check_pool_budget['account_analytic_id']:
                print "check_pool_budget", check_pool_budget
                value = {'account_analytic_id' : check_pool_budget['account_analytic_id'], 'account_id' : account_id}
            else:
                if advance_type_id:
                    account_id          = advance_type.browse(cr, uid, advance_type_id).account_id.id
                    if department:
                        analytic_search     = analytic.search(cr, uid, [('department_id','=',department),('budget_expense','=',account_id)])
                    elif division:
                        analytic_search     = analytic.search(cr, uid, [('division_id','=',division),('budget_expense','=',account_id)])
                    else:
                        raise osv.except_osv(_('Department or Division not Define'), _('Please Check your Department or Division'))
                    if analytic_search:
                        budget_analytic_id  = analytic.browse(cr, uid, analytic_search)[0].id
                        
                        if department:
                            budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('dept_relation','=',department)])
                        else:
                            budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('div_relation','=',division)])
                        budget_line_browse = self.pool.get('ad_budget.line').browse(cr, uid, budget_line_search)
                        
                        if budget_line_browse:
                            print "masuk"
                            #print "Dept ada", department
                            for budget_line_item in budget_line_browse:
                                budget_line_analytic_id = budget_line_item.analytic_account_id.id
                            print "Adella Collection", account_id
                            value = {'account_analytic_id' : budget_line_analytic_id, 'account_id' : account_id}
                        else :
                            value = {'account_analytic_id' : '', 'account_id' : ''}
                    else:
                        
                        value = {'account_analytic_id' : '', 'account_id' : ''}
                
                else :
                    value = {'account_analytic_id' : '', 'account_id' : ''}
        else:
            print "okokokoko"
            value = {'account_analytic_id' : '', 'account_id' : ''}    
        return {'value': value}
    
#    ######################################################################
#    
ticket_travel_line()

class advance_note_line(osv.osv):
    _name = "advance.note.line"
    _description = "Advance Note Lines"
    
    _columns = {
            'advance_id' : fields.many2one('cash.advance','Cash Advance', ondelete='cascade'),
            'note_date' : fields.datetime('Notes Date',required=False),
            'note_desc' : fields.char('Description', size=64),
            'note_user_id' : fields.many2one('res.users','User Name'),
                }
    
advance_note_line()

class cash_advance(osv.osv):
#    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
#        if context is None:
#            context = {}
#        result = super(account_move_line, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('type', False)

    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        if context.get('invoice_id', False):
            company_id = self.pool.get('account.invoice').browse(cr, uid, context['invoice_id'], context=context).company_id.id
            context.update({'company_id': company_id})
        periods = self.pool.get('account.period').find(cr, uid, context=context)
        return periods and periods[0] or False

    def _get_journal(self, cr, uid, context=None):
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        invoice_pool = self.pool.get('account.invoice')
        if context.get('invoice_id', False):
            currency_id = invoice_pool.browse(cr, uid, context['invoice_id'], context=context).currency_id.id
            journal_id = journal_pool.search(cr, uid, [('currency', '=', currency_id)], limit=1)
            return journal_id and journal_id[0] or False
        if context.get('journal_id', False):
            return context.get('journal_id')
        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            return context.get('search_default_journal_id')

        ttype = context.get('type', 'bank')
        if ttype in ('payment', 'receipt'):
            ttype = 'bank'
        res = journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
        return res and res[0] or False

    def _get_tax(self, cr, uid, context=None):
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        journal_id = context.get('journal_id', False)
        if not journal_id:
            ttype = context.get('type', 'bank')
            res = journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
            if not res:
                return False
            journal_id = res[0]

        if not journal_id:
            return False
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id
            return tax_id
        return False

    def _get_currency_base(self, cr, uid, context=None):
        
        currency_search = self.pool.get('res.currency').search(cr, uid, [('base','=',True)])
        currency_browse = self.pool.get('res.currency').browse(cr, uid, currency_search)
        
        for cur_id in currency_browse:
            id_currency = cur_id.id
            
        return id_currency
        
    def _get_currency(self, cr, uid, context=None):
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        journal_id = context.get('journal_id', False)
        if journal_id:
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
#            currency_id = journal.company_id.currency_id.id
            if journal.currency:
                return journal.currency.id
        return False

    def _get_partner(self, cr, uid, context=None):
        if context is None: context = {}
        return context.get('partner_id', False)

    def _get_reference(self, cr, uid, context=None):
        if context is None: context = {}
        return context.get('reference', False)

    def _get_narration(self, cr, uid, context=None):
        if context is None: context = {}
        return context.get('narration', False)

    def _get_amount(self, cr, uid, context=None):
        if context is None:
            context= {}
        return context.get('amount', 0.0)

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if context is None: context = {}
        return [(r['id'], (str("%.2f" % r['amount']) or '')) for r in self.read(cr, uid, ids, ['amount'], context, load='_classic_write')]

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        mod_obj = self.pool.get('ir.model.data')
        if context is None: context = {}

        def get_res_id(view_type, condition):
            result = False
            if view_type == 'tree':
                result = mod_obj.get_object_reference(cr, uid, 'cash_advance', 'view_voucher_tree')
            elif view_type == 'form':
                if condition:
                    result = mod_obj.get_object_reference(cr, uid, 'cash_advance', 'view_vendor_receipt_form')
                else:
                    result = mod_obj.get_object_reference(cr, uid, 'cash_advance', 'view_vendor_payment_form')
            return result and result[1] or False

        if not view_id and context.get('invoice_type', False):
            view_id = get_res_id(view_type,context.get('invoice_type', False) in ('out_invoice', 'out_refund'))

        if not view_id and context.get('line_type', False):
            view_id = get_res_id(view_type,context.get('line_type', False) == 'customer')

        res = super(cash_advance, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='partner_id']")
        if context.get('type', 'sale') in ('purchase', 'payment'):
            for node in nodes:
                node.set('domain', "[('supplier', '=', True)]")
            res['arch'] = etree.tostring(doc)
        return res

    def _compute_writeoff_amount(self, cr, uid, line_dr_ids, line_cr_ids, amount):
        debit = credit = 0.0
        for l in line_dr_ids:
            debit += l['amount']
        for l in line_cr_ids:
            credit += l['amount']
        return abs(amount - abs(credit - debit))

    def onchange_line_ids(self, cr, uid, ids, line_dr_ids, line_cr_ids, amount):
        if not line_dr_ids and not line_cr_ids:
            return {'value':{}}
        line_dr_ids = [x[2] for x in line_dr_ids]
        line_cr_ids = [x[2] for x in line_cr_ids]
        return {'value': {'writeoff_amount': self._compute_writeoff_amount(cr, uid, line_dr_ids, line_cr_ids, amount)}}

    def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
        if not ids: return {}
        res = {}
        debit = credit = 0.0
        for voucher in self.browse(cr, uid, ids, context=context):
            for l in voucher.line_dr_ids:
                debit += l.amount
            for l in voucher.line_cr_ids:
                credit += l.amount
            res[voucher.id] =  abs(voucher.amount - abs(credit - debit))
        return res
    
    def check_adv_method(self, cr, uid, ids):
        for adv in self.browse(cr, uid, ids):
            if adv.advance_method == 'travel':
                return True
        return False
    
    def check_employee_req(self, cr, uid, ids):
        for adv in self.browse(cr, uid, ids):
            employee_id = adv.employee_id.id
            hod_id = self.pool.get('hr.division').search(cr, uid, [('manager_id','=',employee_id)])
            if hod_id and adv.advance_method == 'travel':
                return True
        return False
    
    def create_note(self, cr, uid, ids):
        for adv in self.browse(cr, uid, ids):
            note = adv.narration
            
        if note != "":
            notes = {
                "note_user_id"  : uid,
                "note_desc"     : note,
                "note_date"     : time.strftime('%Y-%m-%d'),
                "advance_id"    : ids[0]
                     }
            self.pool.get('advance.note.line').create(cr, uid, notes)
            self.write(cr, uid, ids, {'narration' : ""})
        return True
        
    def onchange_employee (self, cr, uid, ids, employee_id):
        
        try:
        
            employee_search = self.pool.get('hr.employee').search(cr, uid, [('id', '=', employee_id)])
        
            for onchange in self.pool.get('hr.employee').browse(cr, uid, employee_search):
                
                employee_partner = onchange.address_home_id.partner_id.id
                account_partner = onchange.address_home_id.partner_id.property_account_payable.id
                
            return {'value':{'partner_id': employee_partner, 'account_id': account_partner}}
        
        except: 
               
            result = {}
            
            warning = {
                    "title": ("The Employee not to set as Partner !"),
                    "message": ("Please Set Employee Partner before ")
                }
            
            
            return {'warning': warning, 'value':{'employee_id':result, 'partner_id': result, 'account_id':result}}

    _name = 'cash.advance'
    _description = 'Cash Advance'
    _order = "date desc, id desc"
#    _rec_name = 'number'
    _columns = {
        'type':fields.selection([
            ('sale','Sale'),
            ('purchase','Purchase'),
            ('payment','Payment'),
            ('receipt','Receipt'),
        ],'Default Type', readonly=True, states={'draft':[('readonly',False)]}),
        'name':fields.char('Memo', size=256, required=True ,readonly=False,),
        'req_date':fields.date('Cash Advance Request Date', readonly=False, help="Request Advance Date"),
        'date':fields.date('Advance Date', readonly=False, select=True, help="Effective date for accounting entries"),
        'journal_id':fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'account_id':fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'line_ids':fields.one2many('cash.advance.line','voucher_id','Voucher Lines', readonly=True, states={'draft':[('readonly',False)]}),
        'line_cr_ids':fields.one2many('cash.advance.line','voucher_id','Credits',
            domain=[('type','=','cr')], context={'default_type':'cr'}, readonly=True, states={'draft':[('readonly',False)], 'approve2-1':[('readonly',False)], 'approve3':[('readonly',False)]}),
        'line_dr_ids':fields.one2many('cash.advance.line','voucher_id','Cash Advance Lines',
            domain=[('type','=','dr')], context={'default_type':'dr'}, ),
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'narration':fields.text('Notes', readonly=False),
        'currency_id':fields.many2one('res.currency', 'Currency', readonly=True, states={'draft':[('readonly',False)]}),
#        'currency_id': fields.related('journal_id','currency', type='many2one', relation='res.currency', string='Currency', store=True, readonly=True, states={'draft':[('readonly',False)]}),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'state':fields.selection(
            [('draft','Draft'),
             ('proforma','Pro-forma'),
             ('approve','Waiting Head of Division Approve'),
             ('approve2','Waiting CEO Approve'),
             ('approve2-1','Waiting HRD Approve'),
             ('approve3','Waiting Treasury Approve'),
             ('approve4','Waiting CFO Approve'),
             ('posted','Posted'),
             ('cancel','Cancelled')
            ], 'State', readonly=False, size=32,
            help=' * The \'Draft\' state is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma state,voucher does not have an voucher number. \
                        \n* The \'Posted\' state is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Cancelled\' state is used when user cancel voucher.'),
        'amount': fields.float('Total', digits_compute=dp.get_precision('Account'), required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'tax_amount':fields.float('Tax Amount', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft':[('readonly',False)]}),
        'reference': fields.char('Ref #', size=64, readonly=True, states={'draft':[('readonly',False)]}, help="Transaction reference number."),
        'number': fields.char('Number', size=32, readonly=False,),
        'move_id':fields.many2one('account.move', 'Account Entry'),
        'move_ids': fields.related('move_id','line_id', type='one2many', relation='account.move.line', string='Journal Items', readonly=True),
        'partner_id':fields.many2one('res.partner', 'Partnerxxx', change_default=1, readonly=False),
        'audit': fields.related('move_id','to_check', type='boolean', relation='account.move', string='Audit Complete ?'),
        'pay_now':fields.selection([
            ('pay_now','Pay Directly'),
            ('pay_later','Pay Later or Group Funds'),
        ],'Payment', select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'tax_id':fields.many2one('account.tax', 'Tax', readonly=True, states={'draft':[('readonly',False)]}),
        'pre_line':fields.boolean('Previous Payments ?', required=False),
        'date_due': fields.date('Due Date', readonly=True, select=True, states={'draft':[('readonly',False)]}),
        'payment_option':fields.selection([
                                           ('without_writeoff', 'Keep Open'),
                                           ('with_writeoff', 'Reconcile with Write-Off'),
                                           ], 'Payment Difference', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'writeoff_acc_id': fields.many2one('account.account', 'Write-Off account', readonly=True, states={'draft': [('readonly', False)]}),
        'comment': fields.char('Write-Off Comment', size=64, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'analytic_id': fields.many2one('account.analytic.account','Write-Off Analytic Account', readonly=True, states={'draft': [('readonly', False)]}),
        'writeoff_amount': fields.function(_get_writeoff_amount, method=True, string='Write-Off Amount', type='float', readonly=True),
        'employee_id': fields.many2one("hr.employee","Employee",required=True, readonly=True, states={"draft":[("readonly",False)]}),
        'account_advance_id':fields.many2one('account.account','Account Expenses', required=False, readonly=False,),
        #'advance_currency': fields.many2one('res.currency', 'Currencies', required=True),
        
        #############################################
        'payment_adm': fields.selection([
            ('cash','Cash'),
            ('free_transfer','Non Payment Administration Transfer'),
            ('transfer','Transfer'),
            #('cheque','Cheque'),
            ],'Payment Adm', readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'adm_acc_id': fields.many2one('account.account', 'Account Adm', readonly=True, states={'draft': [('readonly', False)]}),
        'adm_comment': fields.char('Comment Adm', size=128, required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'adm_amount': fields.float('Amount Adm', readonly=True, states={'draft': [('readonly', False)]}),
         'bank_id': fields.many2one("res.bank", "Bank", required=False, readonly=True, states={"draft":[("readonly", False)]}, select=2),
        'cheque_number': fields.char('Cheque No', size=128, required=False, readonly=True, states={'draft': [('readonly', False)]}),
        "cheque_start_date": fields.date("Cheque Date", required=False, readonly=True, states={"draft":[("readonly", False)]}),
        "cheque_end_date": fields.date("Cheque Expire Date", required=False, readonly=True, states={"draft":[("readonly", False)]}),
        ##############################################
        ##################Advance Type################
        "status" : fields.selection([
            ('advance','Advance'),
            ('settled','Settled'),
            ],'Status', select=True),
                
        'advance_method' : fields.selection([
            ('general','General'),
            ('travel','Travel'),
            ],'Advance Method', select=True),
                
        'from_date_travel':fields.date('From', select=True, help="Start Travel Date"),
        'to_date_travel':fields.date('To', select=True, help="End Travel Date"),
        'user_id'       : fields.many2one('res.users', 'Created By',required=True),
        'department_id' : fields.related('employee_id', 'department_id', relation='hr.department',type='many2one', string='Department',store=True, readonly=True), 
        ##############################################
        #############Notes Historical#################
        'note_line_ids':fields.one2many('advance.note.line','advance_id','Note Lines', readonly=True),
        ####################Ticket Travel##########################
#        'tt_partner_id'            : fields.many2one('res.partner','Supplier'),
#        'tt_address_invoice_id'    : fields.many2one('res.partner.address','Invoice Address'),
#        'tt_account_id'            : fields.many2one('account.account', 'Account'),
#        'tt_date'                  : fields.datetime('Date'),
#        'tt_currency_id'           : fields.many2one('res.currency','Currency'),
#        'tt_name'                  : fields.char('Desciption', size=128),
#        'tt_line_ids'              : fields.one2many('ticket.travel.line','ticket_id','Lines', required=True),
        'prnts_line_ids'              : fields.one2many('parent.ticket.travel.line','advance_id','Lines', required=True),
        ################################################
        #######################Budget INfo#########################
        'budget_info_ids_ca': fields.many2many('budget.info.ca', 'budget_info_rel_ca', 'cash_advance_id', 'budget_info_id', 'Budget Line', readonly=True),
        #'budget_info_ids': fields.many2many('budget.info', 'budget_info_rel', 'material_req_id', 'budget_info_id', 'Budget Line', readonly=True),
        #'budget_info_ids': fields.many2many('budget.info.ca', 'budget_info_rel_ca', 'material_req_id', 'budget_info_id', 'Budget Line', readonly=True),
        ################################################
    }
    _defaults = {
        'period_id': _get_period,
        'partner_id': _get_partner,
        'journal_id':_get_journal,
        #INI yang Aslinya >>>>>>>>>>>'currency_id': _get_currency,
        'currency_id': _get_currency_base,
        'reference': _get_reference,
        'narration':_get_narration,
        'amount': _get_amount,
        'type': 'purchase',
        'state': 'draft',
        'pay_now': 'pay_later',
        'name': '',
        'req_date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'cash.advance',context=c),
        'tax_id': _get_tax,
        'payment_option': 'without_writeoff',
        'comment': _('Write-Off'),
        'payment_adm':"cash",
        'status' : 'advance',
        'user_id': lambda self, cr, uid, context: uid,
    }
    
    def compute(self, cr, uid, ids, context=None):
        print ids, "----------------------------"
        
        #######################Compute Ganti Budget Dept###########################
#        for mr in self.browse(cr, uid, ids):
#            department_select = mr.department
#            for line in mr.line_ids:
#                old_account = line.account_analytic_id.budget_expense.id
#                analytic_account_search = self.pool.get('account.analytic.account').search(cr, uid, [('budget_expense','=',old_account), ('department_id','=',department_select)])
#                analytic_account_browse = self.pool.get('account.analytic.account').browse(cr, uid, analytic_account_search)
#                
#                value = {'department':'', 'req_employee':''}
#                
#                return {'value' : value}
        for mr in self.browse(cr, uid, ids):
            if ids:
                mat = int(str(ids[0]))
                cr.execute('delete from budget_info_ca where cash_advance_id = %s ',(mat,))
            for lines in self.browse(cr, uid, ids)[0].line_ids:
                cash_advance_id = ids[0]
                #subtotal = lines.product_qty * lines.price
                subtotal = lines.amount
                account_analytic_id = lines.account_analytic_id.id
                print "subtotal :::", lines.account_analytic_id.id,ids[0]
                #subtotal.update(subtotal)
                vals = {
                    'subtotal' : subtotal
                }
                #self.pool.get('cash.advance.line').write(cr, uid, [lines.id], vals, context=context)
                budget_obj =  self.pool.get('budget.info.ca')
                if account_analytic_id and cash_advance_id:
                    info = budget_obj.search(cr, uid, [('account_analytic_id','=', account_analytic_id),('cash_advance_id','=',cash_advance_id)])
                    if not info:
                        budgets = {
                            'name': '/',
                            'account_analytic_id': account_analytic_id,
                            'cash_advance_id': cash_advance_id,
                        }
                        print "budgets", budgets
                        budget_id = budget_obj.create(cr, uid, budgets)
                        print "==========",cash_advance_id,budget_id
                        cr.execute('INSERT INTO budget_info_rel_ca (cash_advance_id, budget_info_id) values (%s,%s)',(cash_advance_id,budget_id))
                        #cr.execute('INSERT INTO budget_info_rel (material_req_id, budget_info_id) values (%s,%s)',(material_req_id,budget_id))
            return True
    
    
    def check_ticket_line(self, cr, uid, ids, context=None):
        for ca in self.browse(cr, uid, ids):           
            if ca.prnts_line_ids and ca.advance_method == 'travel':
                for line1 in ca.prnts_line_ids:
                    if not line1.line_ids:
                        
                        raise osv.except_osv(_('No Ticket Lines !'), _('Please create some request lines.'))
        return True
    
    def compute_tax(self, cr, uid, ids, context=None):
        tax_pool = self.pool.get('account.tax')
        partner_pool = self.pool.get('res.partner')
        position_pool = self.pool.get('account.fiscal.position')
        voucher_line_pool = self.pool.get('cash.advance.line')
        voucher_pool = self.pool.get('cash.advance')
        if context is None: context = {}

        for voucher in voucher_pool.browse(cr, uid, ids, context=context):
            voucher_amount = 0.0
            for line in voucher.line_ids:
                voucher_amount += line.untax_amount or line.amount
                line.amount = line.untax_amount or line.amount
                voucher_line_pool.write(cr, uid, [line.id], {'amount':line.amount, 'untax_amount':line.untax_amount})

            if not voucher.tax_id:
                self.write(cr, uid, [voucher.id], {'amount':voucher_amount, 'tax_amount':0.0})
                continue

            tax = [tax_pool.browse(cr, uid, voucher.tax_id.id, context=context)]
            partner = partner_pool.browse(cr, uid, voucher.partner_id.id, context=context) or False
            taxes = position_pool.map_tax(cr, uid, partner and partner.property_account_position or False, tax)
            tax = tax_pool.browse(cr, uid, taxes, context=context)

            total = voucher_amount
            total_tax = 0.0

            if not tax[0].price_include:
                for tax_line in tax_pool.compute_all(cr, uid, tax, voucher_amount, 1).get('taxes', []):
                    total_tax += tax_line.get('amount', 0.0)
                total += total_tax
            else:
                for line in voucher.line_ids:
                    line_total = 0.0
                    line_tax = 0.0

                    for tax_line in tax_pool.compute_all(cr, uid, tax, line.untax_amount or line.amount, 1).get('taxes', []):
                        line_tax += tax_line.get('amount', 0.0)
                        line_total += tax_line.get('price_unit')
                    total_tax += line_tax
                    untax_amount = line.untax_amount or line.amount
                    voucher_line_pool.write(cr, uid, [line.id], {'amount':line_total, 'untax_amount':untax_amount})

            self.write(cr, uid, [voucher.id], {'amount':total, 'tax_amount':total_tax})
        return True

    def onchange_price(self, cr, uid, ids, line_ids, tax_id, partner_id=False, context=None):
        tax_pool = self.pool.get('account.tax')
        partner_pool = self.pool.get('res.partner')
        position_pool = self.pool.get('account.fiscal.position')
        res = {
            'tax_amount': False,
            'amount': False,
        }
        voucher_total = 0.0
        voucher_line_ids = []

        total = 0.0
        total_tax = 0.0
        for line in line_ids:
            line_amount = 0.0
            line_amount = line[2] and line[2].get('amount',0.0) or 0.0
            voucher_line_ids += [line[1]]
            voucher_total += line_amount

        total = voucher_total
        total_tax = 0.0
        if tax_id:
            tax = [tax_pool.browse(cr, uid, tax_id, context=context)]
            if partner_id:
                partner = partner_pool.browse(cr, uid, partner_id, context=context) or False
                taxes = position_pool.map_tax(cr, uid, partner and partner.property_account_position or False, tax)
                tax = tax_pool.browse(cr, uid, taxes, context=context)

            if not tax[0].price_include:
                for tax_line in tax_pool.compute_all(cr, uid, tax, voucher_total, 1).get('taxes', []):
                    total_tax += tax_line.get('amount')
                total += total_tax

        res.update({
            'amount':total or voucher_total,
            'tax_amount':total_tax
        })
        return {
            'value':res
        }

    def onchange_term_id(self, cr, uid, ids, term_id, amount):
        term_pool = self.pool.get('account.payment.term')
        terms = False
        due_date = False
        default = {'date_due':False}
        if term_id and amount:
            terms = term_pool.compute(cr, uid, term_id, amount)
        if terms:
            due_date = terms[-1][0]
            default.update({
                'date_due':due_date
            })
        return {'value':default}

    def onchange_journal_voucher(self, cr, uid, ids, line_ids=False, tax_id=False, price=0.0, partner_id=False, journal_id=False, ttype=False, context=None):
        """price
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        default = {
            'value':{},
        }

        if not partner_id or not journal_id:
            return default

        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        account_id = False
        tr_type = False
        if journal.type in ('sale','sale_refund'):
            account_id = partner.property_account_receivable.id
            tr_type = 'sale'
        elif journal.type in ('purchase', 'purchase_refund','expense'):
            account_id = partner.property_account_payable.id
            tr_type = 'purchase'
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
            tr_type = 'receipt'

        default['value']['account_id'] = account_id
        default['value']['type'] = ttype or tr_type

        vals = self.onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, context)
        default['value'].update(vals.get('value'))

        return default

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        """price
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        if context is None:
            context = {}
        if not journal_id:
            return {}
        context_multi_currency = context.copy()
        if date:
            context_multi_currency.update({'date': date})

        line_pool = self.pool.get('cash.advance.line')
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')

        vals = self.onchange_journal(cr, uid, ids, journal_id, [], False, partner_id, context)
        vals = vals.get('value')
        currency_id = vals.get('currency_id', currency_id)
        default = {
            'value':{'line_ids':[], 'line_dr_ids':[], 'line_cr_ids':[], 'pre_line': False, 'currency_id':currency_id},
        }

        if not partner_id:
            return default

        if not partner_id and ids:
            line_ids = line_pool.search(cr, uid, [('voucher_id', '=', ids[0])])
            if line_ids:
                line_pool.unlink(cr, uid, line_ids)
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        account_id = False
        if journal.type in ('sale','sale_refund'):
            account_id = partner.property_account_receivable.id
        elif journal.type in ('purchase', 'purchase_refund','expense'):
            account_id = partner.property_account_payable.id
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id

        default['value']['account_id'] = account_id

        if journal.type not in ('cash', 'bank'):
            return default

        total_credit = 0.0
        total_debit = 0.0
        account_type = 'receivable'
        if ttype == 'payment':
            account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            account_type = 'receivable'

        if not context.get('move_line_ids', False):
            domain = [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)]
            if context.get('invoice_id', False):
                domain.append(('invoice', '=', context['invoice_id']))
            ids = move_line_pool.search(cr, uid, domain, context=context)
        else:
            ids = context['move_line_ids']
        ids.reverse()
        moves = move_line_pool.browse(cr, uid, ids, context=context)

        company_currency = journal.company_id.currency_id.id
        if company_currency != currency_id and ttype == 'payment':
            total_debit = currency_pool.compute(cr, uid, currency_id, company_currency, total_debit, context=context_multi_currency)
        elif company_currency != currency_id and ttype == 'receipt':
            total_credit = currency_pool.compute(cr, uid, currency_id, company_currency, total_credit, context=context_multi_currency)

        for line in moves:
            if line.credit and line.reconcile_partial_id and ttype == 'receipt':
                continue
            if line.debit and line.reconcile_partial_id and ttype == 'payment':
                continue
            total_credit += line.credit or 0.0
            total_debit += line.debit or 0.0
        for line in moves:
            if line.credit and line.reconcile_partial_id and ttype == 'receipt':
                continue
            if line.debit and line.reconcile_partial_id and ttype == 'payment':
                continue
            original_amount = line.credit or line.debit or 0.0
            amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, line.currency_id and abs(line.amount_currency) or original_amount, context=context_multi_currency),
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
            }

            if line.credit:
                amount = min(amount_unreconciled, currency_pool.compute(cr, uid, company_currency, currency_id, abs(total_debit), context=context_multi_currency))
                rs['amount'] = amount
                total_debit -= amount
            else:
                amount = min(amount_unreconciled, currency_pool.compute(cr, uid, company_currency, currency_id, abs(total_credit), context=context_multi_currency))
                rs['amount'] = amount
                total_credit -= amount

            default['value']['line_ids'].append(rs)
            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if ttype == 'payment' and len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif ttype == 'receipt' and len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price)

        return default

    def onchange_date(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        """
        @param date: latest value from user input for field date
        @param args: other arguments
        @param context: context arguments, like lang, time zone
        @return: Returns a dict which contains new values, and context
        """
        if context is None: context = {}
        period_pool = self.pool.get('account.period')
        res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=context)
        if context.get('invoice_id', False):
            company_id = self.pool.get('account.invoice').browse(cr, uid, context['invoice_id'], context=context).company_id.id
            context.update({'company_id': company_id})
        pids = period_pool.find(cr, uid, date, context=context)
        if pids:
            if not 'value' in res:
                res['value'] = {}
            res['value'].update({'period_id':pids[0]})
        return res

    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, context=None):
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id

        vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
        vals['value'].update({'tax_id':tax_id})
        currency_id = journal.company_id.currency_id.id
        if journal.currency:
            currency_id = journal.currency.id
        #vals['value'].update({'currency_id':currency_id})
        return vals

    def proforma_voucher(self, cr, uid, ids, context=None):
        self.action_move_line_create(cr, uid, ids, context=context)
        return True
    
    def proforma_voucher2(self, cr, uid, ids, context=None):
        self.action_move_line_create2(cr, uid, ids, context=context)
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for voucher_id in ids:
            wf_service.trg_create(uid, 'cash.advance', voucher_id, cr)
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def cancel_voucher(self, cr, uid, ids, context=None):
        obj_settlement = self.pool.get('cash.settlement')
        obj_inv = self.pool.get('account.invoice')
        
        settlement_search = obj_settlement.search(cr, uid, [('cash_advance_id','=',ids)])
        settlement_browse = obj_settlement.browse(cr, uid, settlement_search)
        
        invoice_search = obj_inv.search(cr, uid, [('advance_id','=',ids[0])])
        invoice_browse = obj_inv.browse(cr, uid, invoice_search)
        
        for inv in invoice_browse:
            #############Linked Budget###############
            if inv.state not in ('draft', 'cancel'):
                raise osv.except_osv(_('Invalid action !'), _('Cannot cancel Cash Advance Request(s) which are Invoice already opened or paid !'))
            else:
                obj_inv.unlink(cr, uid, invoice_search, context=context)
            #########################################
        
        for a in settlement_browse:
            if a.state not in ('draft', 'cancel'):
                raise osv.except_osv(_('Invalid action !'), _('Cannot cancel Cash Advance Request(s) which are Settlement already opened or paid !'))
            else:
                obj_settlement.unlink(cr, uid, settlement_search, context=context)
        
        reconcile_pool = self.pool.get('account.move.reconcile')
        move_pool = self.pool.get('account.move')

        for voucher in self.browse(cr, uid, ids, context=context):
            recs = []
            for line in voucher.move_ids:
                if line.reconcile_id:
                    recs += [line.reconcile_id.id]
                if line.reconcile_partial_id:
                    recs += [line.reconcile_partial_id.id]

            reconcile_pool.unlink(cr, uid, recs)

            if voucher.move_id:
                move_pool.button_cancel(cr, uid, [voucher.move_id.id])
                move_pool.unlink(cr, uid, [voucher.move_id.id])
        res = {
            'state':'cancel',
            'move_id':False,
        }
        self.write(cr, uid, ids, res)
        return True

    def unlink(self, cr, uid, ids, context=None):
        for t in self.read(cr, uid, ids, ['state'], context=context):
            if t['state'] not in ('draft', 'cancel'):
                raise osv.except_osv(_('Invalid action !'), _('Cannot delete Voucher(s) which are already opened or paid !'))
        return super(cash_advance, self).unlink(cr, uid, ids, context=context)

    # TODO: may be we can remove this method if not used anyware
    def onchange_payment(self, cr, uid, ids, pay_now, journal_id, partner_id, ttype='sale'):
        res = {}
        if not partner_id:
            return res
        res = {'account_id':False}
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        if pay_now == 'pay_later':
            partner = partner_pool.browse(cr, uid, partner_id)
            journal = journal_pool.browse(cr, uid, journal_id)
            if journal.type in ('sale','sale_refund'):
                account_id = partner.property_account_receivable.id
            elif journal.type in ('purchase', 'purchase_refund','expense'):
                account_id = partner.property_account_payable.id
            else:
                account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
            res['account_id'] = account_id
        return {'value':res}
    
    def check_amount(self, cr, uid, ids, context=None):
        a = self.browse(cr, uid, ids)
        for b in a:
            for line in b.line_ids:
                if not line.advance_type_id:
                    raise osv.except_osv(_('Error Amount !'), _('Please Insert Advance Type'))
            
            total_amount = b.amount
            
        cr.execute("SELECT SUM(amount) FROM cash_advance_line WHERE voucher_id in (%s)"% (tuple(ids)))
        sum_amount = cr.fetchone()[0]
        
        if total_amount != sum_amount:
            raise osv.except_osv(_('Error Amount !'), _('Please check your Total Amount !'))
    
    #####################Ticket##########################
    def onchange_partner_invoice(self, cr, uid, ids, context=None):
        
        return True
    
    def create_invoice(self, cr, uid, ids, context=None):
        print "create_invoice------------------>>"
        inv_obj         = self.pool.get('account.invoice')
        inv_line_obj    = self.pool.get('account.invoice.line')
        
        inv_line = []
        
        for parent_tic in self.browse(cr, uid, ids):
            print "parent_tic-----------------------------------------", parent_tic
            for tic in parent_tic.prnts_line_ids:
                print "tic++++++++++++++++++++++++++++++", tic
                partner_id           = tic.partner_id.id
                account_id           = tic.account_id.id
                address_invoice_id   = tic.address_invoice_id.id
                currency_id          = tic.currency_id.id
                name                 = tic.name
                
                for tic_line in tic.line_ids:
                    vals_inv_line={
                            "product_id"    : tic_line.product_id.id,
                            "quantity"      : tic_line.quantity,
                            "name"          : tic_line.name,
                            "price_unit"    : tic_line.amount,
                            "account_id"    : tic_line.account_id.id,
                            "account_analytic_id" : tic_line.account_analytic_id.id
                                }
                    inv_line.append((0,0,vals_inv_line))
                print "IDS", ids
                inv = {
                    "partner_id"            : partner_id,
                    "currency_id"           : currency_id,
                    "address_invoice_id"    : address_invoice_id,
                    "account_id"            : account_id,
                    "invoice_line"          : inv_line,
                    "name"                  : name,
                    "type"                  : "in_invoice",
                    "advance_id"            : ids[0],
                       }
                if parent_tic.advance_method == "travel":
                    inv_obj.create(cr, uid, inv)
                    inv_line = []
        
        return True
    ################################################
    
    def action_move_line_create2(self, cr, uid, ids, context=None):
        
        def _get_payment_term_lines(term_id, amount):
            term_pool = self.pool.get('account.payment.term')
            if term_id and amount:
                terms = term_pool.compute(cr, uid, term_id, amount)
                return terms
            return False
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        currency_pool = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        seq_obj = self.pool.get('ir.sequence')
        period_obj = self.pool.get('account.period')
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.move_id:
                continue
            context_multi_currency = context.copy()
            context_multi_currency.update({'date': inv.date})
            
            ###
            period_id = period_obj.browse(cr,uid,[period_obj.find(cr, uid, inv.date, context=None)[0]],context=None)[0].id
            self.write(cr, uid, ids, {'period_id' : period_id})
            ###
            
            if inv.number:
                name = inv.number
            elif inv.journal_id.sequence_id:
                name = seq_obj.get_id(cr, uid, inv.journal_id.sequence_id.id)
            else:
                raise osv.except_osv(_('Error !'), _('Please define a sequence on the journal !'))
            if not inv.reference:
                ref = name.replace('/','')
            else:
                ref = inv.reference

            move = {
                'name': name,
                'journal_id': inv.journal_id.id,
                'narration': inv.narration,
                'date': inv.date,
                'ref': ref,
                'period_id': period_id or inv.period_id and inv.period_id.id or False
            }
            move_id = move_pool.create(cr, uid, move)

            #create the first line manually
            company_currency = inv.journal_id.company_id.currency_id.id
            current_currency = inv.currency_id.id
            debit = 0.0
            credit = 0.0
            # TODO: is there any other alternative then the voucher type ??
            # -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt
            print "inv.amount", inv.amount
            if inv.type in ('purchase', 'payment'):
                credit = currency_pool.compute(cr, uid, current_currency, company_currency, inv.amount, context=context_multi_currency)
                
            elif inv.type in ('sale', 'receipt'):
                debit = currency_pool.compute(cr, uid, current_currency, company_currency, inv.amount, context=context_multi_currency)
                
            #credit = 100
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            
            sign = debit - credit < 0 and -1 or 1
            
            #create the first line of the voucher
            if inv.advance_method == 'travel':
                first_line_desc = inv.name + " " + inv.from_date_travel + " s/d " + " " + inv.to_date_travel
            else:
                first_line_desc = inv.name
            print "111111111111", inv.journal_id.default_credit_account_id.id
            move_line = {
                'name': first_line_desc or '/',
                'debit': debit,
                'credit': credit,
                #'account_id': inv.account_id.id,
                'account_id': inv.journal_id.default_credit_account_id.id,
                'move_id': move_id,
                'journal_id': inv.journal_id.id,
                'period_id': period_id or inv.period_id.id,
                'partner_id': inv.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * inv.amount or 0.0,
                'date': inv.date,
                'date_maturity': inv.date_due
            }
            move_line_pool.create(cr, uid, move_line)
            rec_list_ids = []
            line_total = debit - credit
            if inv.type == 'sale':
                line_total = line_total - currency_pool.compute(cr, uid, inv.currency_id.id, company_currency, inv.tax_amount, context=context_multi_currency)
            elif inv.type == 'purchase':
                line_total = line_total + currency_pool.compute(cr, uid, inv.currency_id.id, company_currency, inv.tax_amount, context=context_multi_currency)
            amount_total_debit = 0.0
            desc_merge = ''
            for line in inv.line_ids:
                #create one move line per voucher line where amount is not 0.0
                #############Jika Ingin Desc Per Line############
                desc_merge = desc_merge + " " + line.name + ","
                
                if not line.amount:
                    continue
                #we check if the voucher line is fully paid or not and create a move line to balance the payment and initial invoice if needed
                if line.amount == line.amount_unreconciled:
                    amount = line.move_line_id.amount_residual #residual amount in company currency
                else:
                    amount = currency_pool.compute(cr, uid, current_currency, company_currency, line.untax_amount or line.amount, context=context_multi_currency)
                print "22222222222222", line.account_id.id
                move_line = {
                    'journal_id': inv.journal_id.id,
                    'period_id': period_id or inv.period_id.id,
                    'name': first_line_desc or '/',
                    #'name': line.name and line.name or '/',
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': inv.partner_id.id,
                    'currency_id': company_currency <> current_currency and current_currency or False,
                    #'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': inv.date
                }
                if amount < 0:
                    amount = -amount
                    if line.type == 'dr':
                        line.type = 'cr'
                    else:
                        line.type = 'dr'

                if (line.type=='dr'):
                    line_total += amount
                    move_line['debit'] = amount
                else:
                    line_total -= amount
                    move_line['credit'] = amount
                
                amount_total_debit = amount_total_debit + move_line['debit']
                
                if inv.tax_id and inv.type in ('sale', 'purchase'):
                    move_line.update({
                        'account_tax_id': inv.tax_id.id,
                    })
                if move_line.get('account_tax_id', False):
                    tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                    if not (tax_data.base_code_id and tax_data.tax_code_id):
                        raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))
                sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                move_line['amount_currency'] = company_currency <> current_currency and sign * line.amount or 0.0
            move_line['account_id'] = inv.account_advance_id.id
            move_line['debit'] = amount_total_debit
            #DI Geser#
            voucher_line = move_line_pool.create(cr, uid, move_line)
            if line.move_line_id.id:
                rec_ids = [voucher_line, line.move_line_id.id]
                rec_list_ids.append(rec_ids)

            
        
            #            #----------------------tambah disini buat gbu-------------
            #print "pppppppppppppppp"
            diff_adm = inv.adm_amount
            if inv.payment_adm == 'transfer' or inv.payment_adm == 'cheque':
                debit_adm = currency_pool.compute(cr, uid, current_currency, company_currency, diff_adm, context=context_multi_currency)
                credit_adm = currency_pool.compute(cr, uid, current_currency, company_currency, diff_adm, context=context_multi_currency)
                sign_adm = debit_adm - credit_adm < 0 and -1 or 1
                if inv.payment_adm == 'transfer':
                    cost_name = inv.adm_comment
                else:
                    cost_name = 'Cheque Fee'
                print "33333333333333333333", inv.journal_id.default_credit_account_id.id
                move_line_adm_c = {
                    'name': cost_name,
                    'account_id': inv.journal_id.default_credit_account_id.id,
                    'move_id': move_id,
                    'partner_id': inv.partner_id.id,
                    'date': inv.date,
                    'debit': 0,# < 0 and -diff or 0.0,
                    'credit': credit_adm,#diff > 0 and diff or 0.0,
                    'currency_id': company_currency <> current_currency and current_currency or False,
                    'amount_currency': company_currency <> current_currency and sign_adm * -diff_adm or 0.0,
                }
                account_id = inv.adm_acc_id.id
                print "4444444444444444", account_id
                move_line_adm_d = {
                    'name': cost_name,
                    'account_id': account_id,
                    'move_id': move_id,
                    'partner_id': inv.partner_id.id,
                    'date': inv.date,
                    'debit': debit_adm,# < 0 and -diff or 0.0,
                    'credit': 0,#diff > 0 and diff or 0.0,
                    'currency_id': company_currency <> current_currency and current_currency or False,
                    'amount_currency': company_currency <> current_currency and sign_adm * diff_adm or 0.0,
                }
                #print "xxxx3xxxx",move_line_adm_c
                #print "xxxx4xxxx",move_line_adm_d
                if diff_adm != 0:
                    move_line_pool.create(cr, uid, move_line_adm_c)
                    move_line_pool.create(cr, uid, move_line_adm_d)
            #------------------------------------------------------


            inv_currency_id = inv.currency_id or inv.journal_id.currency or inv.journal_id.company_id.currency_id
#            if not currency_pool.is_zero(cr, uid, inv_currency_id, line_total):
#                
#                diff = line_total
#                account_id = False
#                if inv.payment_option == 'with_writeoff':
#                    account_id = inv.writeoff_acc_id.id
#                elif inv.type in ('sale', 'receipt'):
#                    account_id = inv.partner_id.property_account_receivable.id
#                else:
#                    account_id = inv.partner_id.property_account_payable.id
#                print "55555555555555555", account_id
#                move_line = {
#                    'name': name,
#                    'account_id': account_id,
#                    'move_id': move_id,
#                    'partner_id': inv.partner_id.id,
#                    'date': inv.date,
#                    'credit': diff > 0 and diff or 0.0,
#                    'debit': diff < 0 and -diff or 0.0,
#                    #'amount_currency': company_currency <> current_currency and currency_pool.compute(cr, uid, company_currency, current_currency, diff * -1, context=context_multi_currency) or 0.0,
#                    #'currency_id': company_currency <> current_currency and current_currency or False,
#                }
#                move_line_pool.create(cr, uid, move_line)
            self.write(cr, uid, [inv.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            move_pool.post(cr, uid, [move_id], context={})
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    move_line_pool.reconcile_partial(cr, uid, rec_ids)
        
        cash_advance = self.browse(cr, uid, ids)
        
        obj_cash_advance_line = self.pool.get('cash.advance.line')
        print "ids----------->>", ids
        cash_advance_line_search = obj_cash_advance_line.search(cr, uid, [('voucher_id','=',ids)])
        cash_advance_line_browse = obj_cash_advance_line.browse(cr, uid, cash_advance_line_search)
        
        lines = []
        lines_history = []
        
        for advance_line in cash_advance_line_browse:
            vals_line={
                        "name": advance_line.name,
                        #"account_id": inv.account_advance_id.id,
                        #"account_id": advance_line.account_id.id,
                        #"account_id": line.account_id.id,
                        "amount": advance_line.amount,
                        #"quantity": line.quantity,
                        #"invoice_line_tax_id": [(6,0,[t.id for t in line.taxes])],
                        #"product_id": line.product_id.id,
                        ###############Link Budget################
                        'advance_type_id' : advance_line.advance_type_id.id,
                        'account_id' : advance_line.advance_type_id.account_id.id,
                        'account_analytic_id' : advance_line.account_analytic_id.id
                        ##########################################
                    }
            lines.append((0,0,vals_line))
            
            vals_history_line={
                        "name_history": advance_line.name,
                        #"account_id": advance_line.account_id.id,
                        #"account_id": line.account_id.id,
                        "amount_history": advance_line.amount,
                        #"quantity": line.quantity,
                        #"invoice_line_tax_id": [(6,0,[t.id for t in line.taxes])],
                        #"product_id": line.product_id.id,
                    }
            lines_history.append((0,0,vals_history_line))
        
        obj_cash_settlement = self.pool.get('cash.settlement')
        
        req_date = inv.date
        
        vals={
                "employee_id": inv.employee_id.id,
                "partner_id": inv.partner_id.id,
                #"journal_id": inv.journal_id.id,
                "type": 'purchase',
                "line_dr_ids": lines,
                "line_history_ids": lines_history,
                #"account_id": 191,
                "account_advance_id": inv.account_advance_id.id,
                "account_id": inv.account_id.id,
                "name": inv.name,
                "amount":inv.amount,
                "reserved": inv.amount,
                "date_req": req_date,
                "cash_advance_ref": name,
                "cash_advance_id": inv.id,
                "currency_id" : inv.currency_id.id,
                "advance_method" : inv.advance_method,
                #"amount":total,
                #"account_expense_id":account_journal_debit,
                #"origin": replen.name,
                #"state": "approved",
                #partner.property_account_payable.id
                #partner.id
            }
        
        cash_settlement = obj_cash_settlement.create(cr, uid, vals)
        return True

    def copy(self, cr, uid, id, default={}, context=None):
        default.update({
            'state': 'draft',
            'number': False,
            'move_id': False,
            'line_cr_ids': False,
            'line_dr_ids': False,
            'reference': False
        })
        if 'date' not in default:
            default['date'] = time.strftime('%Y-%m-%d')
        return super(cash_advance, self).copy(cr, uid, id, default, context)

cash_advance()

class cash_advance_line(osv.osv):
    _name = 'cash.advance.line'
    _description = 'Cash Advance Lines'
    _order = "move_line_id"

    def _compute_balance(self, cr, uid, ids, name, args, context=None):
        currency_pool = self.pool.get('res.currency')
        rs_data = {}
        for line in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            ctx.update({'date': line.voucher_id.date})
            res = {}
            company_currency = line.voucher_id.journal_id.company_id.currency_id.id
            voucher_currency = line.voucher_id.currency_id.id
            move_line = line.move_line_id or False

            if not move_line:
                res['amount_original'] = 0.0
                res['amount_unreconciled'] = 0.0

            elif move_line.currency_id:
                res['amount_original'] = currency_pool.compute(cr, uid, move_line.currency_id.id, voucher_currency, move_line.amount_currency, context=ctx)
            elif move_line and move_line.credit > 0:
                res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.credit, context=ctx)
            else:
                res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.debit, context=ctx)

            if move_line:
                res['amount_unreconciled'] = currency_pool.compute(cr, uid, move_line.currency_id and move_line.currency_id.id or company_currency, voucher_currency, abs(move_line.amount_residual_currency), context=ctx)
            rs_data[line.id] = res
        return rs_data

    _columns = {
        'voucher_id':fields.many2one('cash.advance', 'Voucher', required=1, ondelete='cascade'),
        'name':fields.char('Description', size=256),
        'account_id':fields.many2one('account.account','Account', required=False),
        'partner_id':fields.related('voucher_id', 'partner_id', type='many2one', relation='res.partner', string='Partner'),
        'untax_amount':fields.float('Untax Amount'),
        'amount':fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'type':fields.selection([('dr','Debit'),('cr','Credit')], 'Cr/Dr'),
        'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),
        'move_line_id': fields.many2one('account.move.line', 'Journal Item'),
        'date_original': fields.related('move_line_id','date', type='date', relation='account.move.line', string='Date', readonly=1),
        'date_due': fields.related('move_line_id','date_maturity', type='date', relation='account.move.line', string='Due Date', readonly=1),
        'amount_original': fields.function(_compute_balance, method=True, multi='dc', type='float', string='Original Amount', store=True),
        'amount_unreconciled': fields.function(_compute_balance, method=True, multi='dc', type='float', string='Open Balance', store=True),
        'company_id': fields.related('voucher_id','company_id', relation='res.company', type='many2one', string='Company', store=True, readonly=True),
        ############Link Budget#############
        'advance_type_id':fields.many2one('advance.type','Advance Type', ),
        ####################################
    }
    ##########################Link Budget#################################
    def onchange_advance_type(self, cr, uid, ids, advance_type_id, employee_id, partner_id):
        employee        = self.pool.get('hr.employee')
        partner         = self.pool.get('res.partner')
        advance_type    = self.pool.get('advance.type')
        analytic        = self.pool.get('account.analytic.account')
        division        = False
        
        department     = employee.browse(cr, uid, employee_id).department_id.id
        #division       = employee.browse(cr, uid, employee_id).user_id.context_division_id.id
        
        if employee.browse(cr, uid, employee_id).user_id:
            division   = employee.browse(cr, uid, employee_id).user_id.context_division_id.id
        
        if advance_type_id:
            print "11111111111111"
            account_id = advance_type.browse(cr, uid, advance_type_id).account_id.id
            if department:
                analytic_search     = analytic.search(cr, uid, [('department_id','=',department),('budget_expense','=',account_id)])
            elif division:
                analytic_search     = analytic.search(cr, uid, [('division_id','=',division),('budget_expense','=',account_id)])
            else:
                raise osv.except_osv(_('Department or Division not Define'), _('Please Check your Department or Division'))
        
            check_pool_budget = self.pool.get('pool.budget').check_pool_account(cr, uid, ids, account_id, department)
        
            if check_pool_budget['account_analytic_id']:
                value = check_pool_budget
            else:
                if advance_type_id:
                    account_id          = advance_type.browse(cr, uid, advance_type_id).account_id.id
                    if department:
                        analytic_search     = analytic.search(cr, uid, [('department_id','=',department),('budget_expense','=',account_id)])
                    elif division:
                        analytic_search     = analytic.search(cr, uid, [('division_id','=',division),('budget_expense','=',account_id)])
                    else:
                        raise osv.except_osv(_('Department or Division not Define'), _('Please Check your Department or Division'))
                    if analytic_search:
                        budget_analytic_id  = analytic.browse(cr, uid, analytic_search)[0].id
                        
                        if department:
                            budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('dept_relation','=',department)])
                        else:
                            budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('div_relation','=',division)])
                        budget_line_browse = self.pool.get('ad_budget.line').browse(cr, uid, budget_line_search)
                        
                        if budget_line_browse:
                            #print "Dept ada", department
                            for budget_line_item in budget_line_browse:
                                budget_line_analytic_id = budget_line_item.analytic_account_id.id
                                
                            value = {'account_analytic_id' : budget_line_analytic_id}
                        else :
                            value = {'account_analytic_id' : ''}
                    else:
                        
                        value = {'account_analytic_id' : ''}
                
                else :
                    value = {'account_analytic_id' : ''}
        else:
            print "okokokoko"
            value = {'account_analytic_id' : ''}    
        return {'value': value}
    ######################################################################
    
    _defaults = {
        'name': ''
    }

    def onchange_move_line_id(self, cr, user, ids, move_line_id, context=None):
        """
        Returns a dict that contains new values and context

        @param move_line_id: latest value from user input for field move_line_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        res = {}
        move_line_pool = self.pool.get('account.move.line')
        if move_line_id:
            move_line = move_line_pool.browse(cr, user, move_line_id, context=context)
            if move_line.credit:
                ttype = 'dr'
            else:
                ttype = 'cr'
            account_id = move_line.account_id.id
            res.update({
                'account_id':account_id,
                'type': ttype
            })
        return {
            'value':res,
        }

    def default_get(self, cr, user, fields_list, context=None):
        """
        Returns default values for fields
        @param fields_list: list of fields, for which default values are required to be read
        @param context: context arguments, like lang, time zone

        @return: Returns a dict that contains default values for fields
        """
        if context is None:
            context = {}
        journal_id = context.get('journal_id', False)
        partner_id = context.get('partner_id', False)
        journal_pool = self.pool.get('account.journal')
        partner_pool = self.pool.get('res.partner')
        values = super(cash_advance_line, self).default_get(cr, user, fields_list, context=context)
        if (not journal_id) or ('account_id' not in fields_list):
            return values
        journal = journal_pool.browse(cr, user, journal_id, context=context)
        account_id = False
        ttype = 'cr'
        if journal.type in ('sale', 'sale_refund'):
            account_id = journal.default_credit_account_id and journal.default_credit_account_id.id or False
            ttype = 'cr'
        elif journal.type in ('purchase', 'expense', 'purchase_refund'):
            account_id = journal.default_debit_account_id and journal.default_debit_account_id.id or False
            ttype = 'dr'
        elif partner_id:
            partner = partner_pool.browse(cr, user, partner_id, context=context)
            if context.get('type') == 'payment':
                ttype = 'dr'
                account_id = partner.property_account_payable.id
            elif context.get('type') == 'receipt':
                account_id = partner.property_account_receivable.id

        values.update({
            'account_id':account_id,
            'type':ttype
        })
        return values
cash_advance_line()