import time
import netsvc
import pooler
import datetime
from dateutil.relativedelta import relativedelta
import base64, urllib
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _
#select sum(z.price_unit*z.product_qty) as balance_virtual FROM purchase_order_line x, purchase_order y, stock_move z, stock_picking a
#                        where z.state = 'done' and z.purchase_line_id = x.id and x.state in ('confirmed','done')  and x.account_analytic_id = 4451 and to_char(x.date_planned,'yyyy') = '2012'
#                        and x.order_id = y.id and a.id = z.picking_id and a.invoice_state = '2binvoiced'
class budget_info(osv.osv):
    _name = 'budget.info'
    _description = 'Budget Info'
    
    def _amount_budget(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            date_end = line.material_req_id.date_end[:4]
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
            date_end = line.material_req_id.date_end[:4]
            #acc_ids = line.budget_item_id.
            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line "
                   "WHERE account_id=%s AND to_char(date,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_real = cr.fetchone()
            amount_real = amount_real[0] or 0.00
            print amount_real
            
            cr.execute("select SUM((x.product_qty * x.price_unit)-(x.product_qty * x.price_unit)*x.discount/100) as balance_virtual FROM purchase_order_line x, purchase_order y "
                        " where y.state in ('approved') and x.order_id = y.id "
                        "  and x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_virtual1 = cr.fetchone()
            amount_virtual1 = amount_virtual1[0] or 0.00
            
            cr.execute("SELECT SUM(a.product_qty*a.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y, stock_move a "
                     " WHERE x.order_id = y.id and a.purchase_line_id = x.id and a.state in ('cancel','done') and "
                     " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
                       "  where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('approved') and b.state not in ('draft')) and a.id=y.id) and "
                       " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            amount_virtual2 = cr.fetchone()
            amount_virtual2 = amount_virtual2[0] or 0.00
            print amount_virtual1, amount_virtual2, amount_real
            ###############ASLI#############################
            #res[line['id']] = (amount_virtual1 - amount_virtual2) + abs(amount_real)
            ################################################
            if (amount_virtual1 - amount_virtual2) < 0:
                res[line['id']] = abs(amount_real)
            else:
                res[line['id']] = (amount_virtual1 - amount_virtual2) + abs(amount_real)
            
        return res
    
    def _amount_current(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            material_req_id = line.material_req_id.id
            date_end = line.material_req_id.date_end[:4]
            #acc_ids = line.budget_item_id.
            cr.execute("select sum(a.subtotal) from material_requisition c, material_requisition_line a, budget_info b "
                       " where c.id=a.requisition_id and a.requisition_id = %s and a.account_analytic_id=b.account_analytic_id and b.account_analytic_id = %s and c.id = b.material_req_id and to_char(c.date_end,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
            amount1 = cr.fetchone()
            amount1 = amount1[0] or 0.00
            
            cr.execute(" select sum(e.subtotal) from purchase_order a, purchase_requisition b, stock_picking c, material_requisition d, material_requisition_line e, budget_info f "
                       " where a.requisition_id = b.id and b.int_move_id = c.id and c.material_req_id = d.id and a.state in ('done','approved') "
                       " and d.id = f.material_req_id  and e.account_analytic_id = f.account_analytic_id and d.id = e.requisition_id "
                       " and e.requisition_id = %s and f.account_analytic_id = %s and to_char(d.date_end,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
            amount2 = cr.fetchone()
            amount2 = amount2[0] or 0.00
            #print "xxxxxxxxxxxx",amount,material_req_id,str(account_analytic_id),str(date_end)
            res[line['id']] = amount1 - amount2
        return res
    
    def _amount_utilized(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            material_req_id = line.material_req_id.id
            date_end = line.material_req_id.date_end[:4]
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
            cr.execute("select SUM((x.product_qty * x.price_unit)-(x.product_qty * x.price_unit)*x.discount/100) as balance_virtual FROM purchase_order_line x, purchase_order y "
                        " where y.state in ('approved') and x.order_id = y.id "
                        "  and x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_virtual1 = cr.fetchone()
            amount_virtual1 = amount_virtual1[0] or 0.00
            
            cr.execute("SELECT SUM(a.product_qty*a.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y, stock_move a "
                     " WHERE x.order_id = y.id and a.purchase_line_id = x.id and a.state in ('cancel','done') and "
                     " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
                       "  where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('approved') and b.state not in ('draft')) and a.id=y.id) and "
                       " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            amount_virtual2 = cr.fetchone()
            amount_virtual2 = amount_virtual2[0] or 0.00
            
            
            ###############ASLI##########################
            #amount_spent = amount_virtual1 - amount_virtual2
            ################################################
            
            if (amount_virtual1 - amount_virtual2) < 0:
                amount_spent = 0.0
            else:
                amount_spent = (amount_virtual1 - amount_virtual2)
            #res[line['id']] = amount_spent
            #===================================================================
            cr.execute("select sum(a.subtotal) from material_requisition c, material_requisition_line a, budget_info b "
                       " where c.id=a.requisition_id and a.requisition_id = %s and a.account_analytic_id=b.account_analytic_id and b.account_analytic_id = %s and c.id = b.material_req_id and to_char(c.date_end,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
            amount1 = cr.fetchone()
            amount1 = amount1[0] or 0.00
            
            cr.execute(" select sum(e.subtotal) from purchase_order a, purchase_requisition b, stock_picking c, material_requisition d, material_requisition_line e, budget_info f "
                       " where a.requisition_id = b.id and b.int_move_id = c.id and c.material_req_id = d.id and a.state in ('done','approved') "
                       " and d.id = f.material_req_id  and e.account_analytic_id = f.account_analytic_id and d.id = e.requisition_id "
                       " and e.requisition_id = %s and f.account_analytic_id = %s and to_char(d.date_end,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
            amount2 = cr.fetchone()
            amount2 = amount2[0] or 0.00
            amount_current = amount1 - amount2
            #print amount1,amount2,amount_current,amount_budget - (amount_spent + amount_current + abs(amount_real))
            #===================================================================
            
            res[line['id']] = amount_spent + amount_current + abs(amount_real)
        return res
    
    def _amount_remain(self, cr, uid, ids, name, args, context=None):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            account_analytic_id = line.account_analytic_id.id
            material_req_id = line.material_req_id.id
            date_end = line.material_req_id.date_end[:4]
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
            cr.execute("select SUM((x.product_qty * x.price_unit)-(x.product_qty * x.price_unit)*x.discount/100) as balance_virtual FROM purchase_order_line x, purchase_order y "
                        " where y.state in ('approved') and x.order_id = y.id "
                        "  and x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_virtual1 = cr.fetchone()
            amount_virtual1 = amount_virtual1[0] or 0.00
            
            cr.execute("SELECT SUM(a.product_qty*a.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y, stock_move a "
                     " WHERE x.order_id = y.id and a.purchase_line_id = x.id and a.state in ('cancel','done') and "
                     " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
                       "  where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('approved') and b.state not in ('draft')) and a.id=y.id) and "
                       " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            amount_virtual2 = cr.fetchone()
            amount_virtual2 = amount_virtual2[0] or 0.00
            ##############ASLI#################
            #amount_spent = amount_virtual1 - amount_virtual2
            if (amount_virtual1 - amount_virtual2) < 0:
                amount_spent = 0.0
            else:
                amount_spent = (amount_virtual1 - amount_virtual2)
            
            #res[line['id']] = amount_spent
            #===================================================================
            cr.execute("select sum(a.subtotal) from material_requisition c, material_requisition_line a, budget_info b "
                       " where c.id=a.requisition_id and a.requisition_id = %s and a.account_analytic_id=b.account_analytic_id and b.account_analytic_id = %s and c.id = b.material_req_id and to_char(c.date_end,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
            amount1 = cr.fetchone()
            amount1 = amount1[0] or 0.00
            
            cr.execute(" select sum(e.subtotal) from purchase_order a, purchase_requisition b, stock_picking c, material_requisition d, material_requisition_line e, budget_info f "
                       " where a.requisition_id = b.id and b.int_move_id = c.id and c.material_req_id = d.id and a.state in ('done','approved') "
                       " and d.id = f.material_req_id  and e.account_analytic_id = f.account_analytic_id and d.id = e.requisition_id "
                       " and e.requisition_id = %s and f.account_analytic_id = %s and to_char(d.date_end,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
            amount2 = cr.fetchone()
            amount2 = amount2[0] or 0.00
            amount_current = amount1 - amount2
            #print amount1,amount2,amount_current,amount_budget - (amount_spent + amount_current + abs(amount_real))
            #===================================================================
            res[line['id']] = amount_budget - (amount_spent + amount_current + abs(amount_real))
        return res
    
    _columns = {
        'name': fields.char('Name', 64),
        'account_analytic_id':fields.many2one('account.analytic.account', 'Analytic Account',),
        'material_req_id': fields.many2one('material.requisition', 'Material Request'),
        #'budget_line_id': fields.many2one('ad_budget.line', 'Budget Lines'),
        'amount_budget': fields.function(_amount_budget, digits=(20,0), method=True, string='Budget Amount', type='float'),
        'amount_spent': fields.function(_amount_spent, digits=(20,0), method=True, string='Budget Spent', type='float'),
        'amount_current': fields.function(_amount_current, digits=(20,0), method=True, string='Budget Current', type='float'),
        'amount_utilized': fields.function(_amount_utilized, digits=(20,0), method=True, string='Budget Utilized', type='float'),
        'amount_remain': fields.function(_amount_remain, digits=(20,0), method=True, string='Budget Remain', type='float'),
    }
budget_info()

class material_requisition(osv.osv):
    _name = "material.requisition"
    _description="Material Requisition"
    
#    def tender_reset(self, cr, uid, ids, context=None):
#        self.write(cr, uid, ids, {'state':'draft'} ,context=context)
#        return True
    
    def create(self, cr, uid, vals, context=None):
        seq_name = self.pool.get('ir.sequence').get(cr, uid, 'material.requisition')
        vals.update({'name': seq_name})
        return super(material_requisition, self).create(cr, uid, vals, context)
    
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
            department = mr.department.id
            if not department:
                raise osv.except_osv(_('No Employee Defined !'),_("You must first select a Employee !") )
            for line in mr.line_ids:
                if line.product_id:
                    ######################Compute Asset#########################
                    
                    prod = line.product_id
                    account_expense = prod.property_account_expense.id
                    if prod.property_account_expense.user_type.report_type == 'asset':
                        print "ASSET1111"
                        div_id = self.pool.get('hr.department').browse(cr, uid, department).division_id.id
                        print "div_id", div_id
                        dept_browse = self.pool.get('hr.department').search(cr, uid, [('division_id','=',div_id),('dept_general','=',True)])
                        print "sssss", dept_browse, type(dept_browse)
                        if dept_browse:
                            try:
                                department=dept_browse[0]
                            except:
                                department = dept_browse
                        
                        analytic_account_search = self.pool.get('account.analytic.account').search(cr, uid, [('budget_expense','=',account_expense), ('department_id','=',department)])
                        analytic_account_browse = self.pool.get('account.analytic.account').browse(cr, uid, analytic_account_search)
                        print "Department ::::", department, "Account EXP ::", account_expense
                        if analytic_account_browse:
                            print "ada analitic"
                            for item in analytic_account_browse:
                                print "ITEM ::", item.name
                                budget_analytic_id = item.id
                                
                            budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('dept_relation','=',department)])
                            budget_line_browse = self.pool.get('ad_budget.line').browse(cr, uid, budget_line_search)
                            
                            if budget_line_browse:
                                #print "Dept ada", department
                                for budget_line_item in budget_line_browse:
                                    budget_line_analytic_id = budget_line_item.analytic_account_id.id
                            
                                value = {'product_uom_id': prod.uom_id.id,'account_analytic_id':budget_line_analytic_id}
                            else :
                                value = {'product_uom_id': prod.uom_id.id,'account_analytic_id':''}
                        else:
                            print "Tidak ada analitic"
                            value = {'product_uom_id': prod.uom_id.id, 'account_analytic_id':''}
                        self.pool.get('material.requisition.line').write(cr, uid, [line.id], value)
                    ############################################################
                    else:
                        print "NON ASSET111"
                        print "line.product_id :::::", line.product_id
                        department = mr.department.id
                        prod = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=context)
                        
                        account_expense = prod.property_account_expense.id
                        type_product    = prod.type
                        #print "account_expense ::", account_expense
                        #print "product ::::", product_id.name
                        if type_product == 'consu':
                            value = {'account_analytic_id':''}
                            warning = {
                                "title": ("Product Type"),
                                "message": (("You Can not Product selected with Type Consumable"))
                            }
                            return {'warning': warning ,'value': value}
                        
                        if not account_expense:
                            value = {'account_analytic_id':''}
                            warning = {
                                "title": ("Account Expense Product No Define"),
                                "message": (("Please Define Account Expense for Product '%s'") % (prod.name))
                            }
                            return {'warning': warning ,'value': value}
                        print "account_expense", account_expense
                        print "department", department
                        analytic_account_search = self.pool.get('account.analytic.account').search(cr, uid, [('budget_expense','=',account_expense), ('department_id','=',department)])
                        analytic_account_browse = self.pool.get('account.analytic.account').browse(cr, uid, analytic_account_search)
                        print "Department ::::", department, "Account EXP ::", account_expense
                        if analytic_account_browse:
                            print "ada analitic"
                            for item in analytic_account_browse:
                                print "ITEM ::", item.name
                                budget_analytic_id = item.id
                                
                            budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('dept_relation','=',department)])
                            budget_line_browse = self.pool.get('ad_budget.line').browse(cr, uid, budget_line_search)
                            
                            if budget_line_browse:
                                #print "Dept ada", department
                                for budget_line_item in budget_line_browse:
                                    budget_line_analytic_id = budget_line_item.analytic_account_id.id
                                    print "budget_line_analytic_id>>>>>>>>>>>>>>>>>>>>", budget_line_analytic_id
                                value = {'account_analytic_id':budget_line_analytic_id}
                            else :
                                value = {'account_analytic_id':''}
                        else:
                            print "Tidak ada analitic"
                            value = {'account_analytic_id':''}
                        self.pool.get('material.requisition.line').write(cr, uid, [line.id], value)
        ###########################################################################
        
        if ids:
            mat = int(str(ids[0]))
            cr.execute('delete from budget_info where material_req_id = %s ',(mat,))
        for lines in self.browse(cr, uid, ids)[0].line_ids:
            material_req_id = ids[0]
            subtotal = lines.product_qty * lines.price
            account_analytic_id = lines.account_analytic_id.id
            print "subtotal :::", lines.account_analytic_id.id,ids[0]
            #subtotal.update(subtotal)
            vals = {
                'subtotal' : subtotal
            }
            self.pool.get('material.requisition.line').write(cr, uid, [lines.id], vals, context=context)
            budget_obj =  self.pool.get('budget.info')
            if account_analytic_id and material_req_id:
                info = budget_obj.search(cr, uid, [('account_analytic_id','=', account_analytic_id),('material_req_id','=',material_req_id)])
                if not info:
                    budgets = {
                        'name': '/',
                        'account_analytic_id': account_analytic_id,
                        'material_req_id': material_req_id,
                    }
                    budget_id = budget_obj.create(cr, uid, budgets)
                    cr.execute('INSERT INTO budget_info_rel (material_req_id, budget_info_id) values (%s,%s)',(material_req_id,budget_id))
        return True
    
    def picking_cancel(self, cr, uid, ids, context=None):
        #print "picking_cancel"
        if not self.browse(cr, uid, ids)[0].description:
            raise osv.except_osv(_('Invalid action !'), _('Please Insert Your Reason Cancel In Tab Notes !'))
        else:
            ############Create Note MR######
            note_line_hstry = {
                           'user' : uid,
                           'description' : self.browse(cr, uid, ids)[0].description,
                           'date' : time.strftime('%Y-%m-%d %H:%M:%S'),
                           'requisition_id' : ids[0],
                                  }
            self.pool.get('note.line').create(cr, uid, note_line_hstry)
            self.write(cr, uid, ids, {'description' : ''})
            ################################
        
        if self.browse(cr, uid, ids)[0].state == 'done':
            picking_search = self.pool.get('stock.picking').search(cr, uid, [('material_req_id','=', ids)])
            q = len(picking_search)
            if picking_search:
                pb = self.pool.get('stock.picking').browse(cr, uid, picking_search[q-1])
                if pb.state == 'draft' or pb.state =='cancel':
                    self.pool.get('stock.picking').write(cr, uid, pb.id, {'state':'cancel'})
                else:
                    raise osv.except_osv(_('Invalid action !'), _('Cannot cancel Stock Picking in State Confirm !'))
        
        
        return True
    
    def action_cancel_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for inv_id in ids:
            wf_service.trg_delete(uid, 'material.requisition', inv_id, cr)
            wf_service.trg_create(uid, 'material.requisition', inv_id, cr)
        return True
    
    def check_budget(self,cr, uid, ids, *args):
        print "check_budget================>>", ids[0]
        tender_obj = self.pool.get('material.requisition')
        ext_note_line = self.pool.get('extra.note.line')
        
        for tender in tender_obj.browse(cr, uid, ids):
            for line in tender.line_ids:
                budget = line.account_analytic_id.id
                print "product :", line.product_id.name
                print "Budget", budget
                
                if not budget:
                    print "tidak ada"
                    
                    if not tender.ext_note:
                        print "tender.ext_note===+++++"
                        raise osv.except_osv(_('No Budget !'), _('Please Insert Extra Notes Because Your Request Non Budget Available.'))
                    else:
                        print "masukk000000000000000000"
                        ext_note_line_hstry = {
                                               'user' : uid,
                                               'description' : tender.ext_note,
                                               'date' : time.strftime('%Y-%m-%d %H:%M:%S'),
                                               'requisition_id' : ids[0],
                                  }
                        ext_note_line.create(cr, uid, ext_note_line_hstry)
                        
                    return True
                
        return False
    
    def create_lv_1(self, cr, uid, ids, context=None):
        for mr in self.browse(cr, uid, ids):
            if uid != 1 and uid <> mr.user_id.id:
                raise osv.except_osv(_('User False !'), _('Check Your Account.'))
            if not mr.line_ids:
                raise osv.except_osv(_('No Material Request Lines !'), _('Please create some request lines.'))
        
        self.write(cr, uid, ids, {'user_app':time.strftime('%Y-%m-%d %H:%M:%S')})
        self.write(cr, uid, ids, {'state':'lv_1'} ,context=context)
        return True
        
        self.write(cr, uid, ids, {'user_app':time.strftime('%Y-%m-%d %H:%M:%S')})
        self.write(cr, uid, ids, {'state':'lv_1'} ,context=context)
        return True
        
    def create_lv_2(self, cr, uid, ids, context=None):
        
        user = self.pool.get('res.users').browse(cr, uid, uid)
        dept_user = user.context_department_id.id
        super_user = user.super_user
        
        for mr in self.browse(cr, uid, ids):
            if uid != 1 and mr.department.manager_id.user_id.id <> uid and super_user == False:
                print "a"
                #raise osv.except_osv(_('User False !'), _('Check Your Account.'))
        self.write(cr, uid, ids, {'manager_app':time.strftime('%Y-%m-%d %H:%M:%S')})
        self.write(cr, uid, ids, {'state': 'lv_2'})
        return True
    
    def create_lv_3(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        div_user = user.context_division_id.id
        super_user = user.super_user
        
        for mr in self.browse(cr, uid, ids):
            if uid != 1 and mr.department.division_id.manager_id.user_id.id <> uid:
                raise osv.except_osv(_('User False !'), _('Check Your Account.'))
        
        self.write(cr, uid, ids, {'kadiv_app':time.strftime('%Y-%m-%d %H:%M:%S')})
        self.write(cr, uid, ids, {'state': 'lv_3'})
        return True
    
    def create_lv_4(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'ceo_app':time.strftime('%Y-%m-%d %H:%M:%S')})
        self.write(cr, uid, ids, {'state': 'lv_4'})
        return True
    
    def tender_reset(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def tender_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'warehouse_app':time.strftime('%Y-%m-%d %H:%M:%S')})
        self.write(cr, uid, ids, {'state':'done'}, context=context)
        
        self.create_order(cr, uid, ids, context)
        return True
    
    def create_order(self, cr, uid, ids, context={}):
        print "xxxxxxxxxxxxxxxxxxxxxxxxx"
        mr_obj = self.pool.get('material.requisition')
        mr_line_obj = self.pool.get('material.requisition.line')
        stock_picking_obj = self.pool.get('stock.picking')
        stock_move_obj = self.pool.get('stock.move')
        
        mr_search = mr_obj.search(cr, uid, [('id','=', ids)])
        mr_browse = mr_obj.browse(cr, uid, mr_search)
        
        for id_mr in mr_browse:
            id = id_mr.id
            ref = id_mr.name
            mr_line_search = mr_line_obj.search(cr, uid, [('requisition_id','=', id)])
            mr_line_browse = mr_line_obj.browse(cr, uid, mr_line_search)
            req_employee = id_mr.req_employee 
            record = {
                      'origin'          : ref,
                      'type'            : "internal",
                      'req_employee'    : req_employee.id,
                      'material_req_id' : id,
                      ######################
                      'mr_description'  : id_mr.origin,
                      ######################
                      }
            
            sp_id = stock_picking_obj.create(cr, uid, record)
            
            stock_lick_search = stock_picking_obj.search(cr, uid, [('origin','=', ref)])
            stock_lick_browse = stock_picking_obj.browse(cr, uid, stock_lick_search)
            
            for id_id in stock_lick_browse:
                id_id = id_id.id
            
            for id_mr_line in mr_line_browse:
                
                id_line = id_mr_line.id
                
                product_id = id_mr_line.product_id.id
                product_qty = id_mr_line.product_qty
                product_uom_id = id_mr_line.product_uom_id.id
                
                stock_move_obj.create(cr, uid, {
                        'product_uos_qty'       : id_mr_line.product_qty,
                        'date_expected'         : time.strftime('%Y-%m-%d %H:%M:%S'),
                        'date'                  : time.strftime('%Y-%m-%d %H:%M:%S'),
                        'product_qty'           : id_mr_line.product_qty,
                        'location_id'           : "12",
                        'name'                  : id_mr_line.product_id.name,
                        'product_id'            : id_mr_line.product_id.id,
                        'company_id'            : "1",
                        'picking_id'            : id_id,
                        'priority'              : "1",
                        'state'                 : "draft",
                        'location_dest_id'      : "11",
                        'product_uom'           : id_mr_line.product_uom_id.id,
                        
                        'price_unit'            : id_mr_line.price,
                        'analytic_id'           : id_mr_line.account_analytic_id.id,
                        'info'                  : id_mr_line.info,
                        'detail'                : id_mr_line.detail,
#                        'picking_id' : id,
#                        'product_id' : id_mr_line.product_id.id,
#                        'product_qty' : id_mr_line.product_qty,
#                        'product_uom_id' : id_mr_line.product_uom_id.id,
                        }) 
                
    
    def _get_approve_status(self, cr, uid, ids, field_name, arg, context=None):
        print "xxxxxxxxxxxxxxxxxxxxxxxxxx", ids
        result = {}
        
#        [('draft','Draft'),('lv_1','Waitting Manager Approve'),
#                                            ('lv_2','Waitting Kadiv Approve'),('lv_3','Waitting CFO'),
#                                            ('lv_4','Waitting Warehouse User'),
#                                            ('cancel','Cancelled'),('done','Done')]
        
        
        if len(ids) <= 1:
            for mr in self.browse(cr, uid, ids, context):
                if mr.state == 'draft':
                    try:
                        to_approve_name = mr.user_id.name or ""
                    except Exception,e:
                        to_approve_name = "Request User Name Not Defined"
                elif mr.state == 'lv_1':
                    try:
                        to_approve_name = mr.department.manager_id.name or ""
                    except Exception,e:
                        to_approve_name = "Manager Name Not Defined"
                elif mr.state == 'lv_2':
                    try:
                        to_approve_name = mr.department.division_id.manager_id.name or ""
                    except Exception,e:
                        to_approve_name = "Head of Division Name Not Defined"
                else:
                    to_approve_name = "/"
                
            print to_approve_name
            result[mr.id] = to_approve_name or ""
        return result
    
    
    def _get_status(self, cr, uid, ids, name, args, context=None):
        result = {}
        print "IDS", ids
        mr_id = ids[0]
        print "MR ID", mr_id
        int_state   = ""
        pr_state    = ""
        po_state    = ""
        in_state    = ""
        
        obj_picking = self.pool.get('stock.picking')
        int_search  = obj_picking.search(cr, uid, [('material_req_id','=', mr_id), ('type','=','internal'), ('state','not in',['cancel'])])
        if int_search:
            int_state   = obj_picking.browse(cr, uid, int_search)[0].state
        else:
            print "++++++++++++++++++++++++++++++++++++++++++++"
            int_state   = ""
        
        obj_requisition = self.pool.get('purchase.requisition')
        pr_search  = obj_requisition.search(cr, uid, [('material_req_id','=', mr_id), ('state','not in',['cancel'])])
        if pr_search:
            pr_state    = obj_requisition.browse(cr, uid, pr_search)[0].state
        else:
            pr_state    = ""
            
        obj_order   = self.pool.get('purchase.order')
        po_search   = obj_order.search(cr, uid, [('mr_number','=', mr_id)])
        if po_search:
            for po in obj_order.browse(cr, uid, po_search):
                if po.state == 'done':
                    po_state = 'done'
                else:
                    po_state = 'in_progress'
                
            
#        obj_incoming = self.pool.get('stock.picking')
#        incoming  = obj_incoming.search(cr, uid, [('material_req_id','=', mr_id), ('type','=','in'),('state','not in',['cancel'])])
#        if incoming:
#            print "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP"
#            #in_state   = obj_incoming.browse(cr, uid, incoming)[0].state
#            for i in obj_incoming.browse(cr, uid, incoming):
#                if i.state <> 'done':
#                    in_state = "in_progress"
#                else:
#                    print "masuk-------------------------"
#                    in_state = "done"
                    
                    
        for mr in self.browse(cr, uid, ids, context=context):
            result[mr.id] = {
                            'int_status'    : "",
                            'pr_status'     : "",
                            'po_status'     : "",
                            'in_status'     : "",
                             }
            print "int_state", int_state
            result[mr.id]['int_status']     = int_state
            result[mr.id]['pr_status']      = pr_state
            result[mr.id]['po_status']      = po_state
            print "in_state", in_state
            #result[mr.id]['in_status']      = in_state
            
        print "result",result
        return result
    
    def _get_material_request(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('material.requisition').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()
    
    def _get_stock_picking(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.picking').browse(cr, uid, ids, context=context):
            result[line.material_req_id.id] = True
        return result.keys()
    
    def _get_purchase_requisition(self, cr, uid, ids, context=None):
        result = {}             
        for line in self.pool.get('purchase.requisition').browse(cr, uid, ids, context=context):
            result[line.material_req_id.id] = True
        return result.keys()
    
    def _get_purchase_order(self, cr, uid, ids, context=None):
        result = {}             
        for line in self.pool.get('purchase.order').browse(cr, uid, ids, context=context):
            result[line.mr_number.id] = True
        return result.keys()
    
    def _get_incoming(self, cr, uid, ids, context=None):
        result = {}             
        for line in self.pool.get('stock.picking').browse(cr, uid, ids, context=context):
            result[line.purchase_id.mr_number.id] = True
        return result.keys()
    
    _columns = {
        'name'          : fields.char('Requisition Reference', size=32,required=True),
        'origin'        : fields.char('Description', size=32),
        'date_start'    : fields.datetime('Requisition Date',required=True),
        'date_end'      : fields.datetime('Requisition Deadline', required=True),
        'user_id'       : fields.many2one('res.users', 'Responsible', readonly=True),
        'exclusive'     : fields.selection([('exclusive','Purchase Requisition (exclusive)'),('multiple','Multiple Requisitions')],'Requisition Type', required=False, help="Purchase Requisition (exclusive):  On the confirmation of a purchase order, it cancels the remaining purchase order.\nPurchase Requisition(Multiple):  It allows to have multiple purchase orders.On confirmation of a purchase order it does not cancel the remaining orders"""),
        'description'   : fields.text('Description'),
        'company_id'    : fields.many2one('res.company', 'Company', required=True),
        'purchase_ids'  : fields.one2many('purchase.order','requisition_id','Purchase Orders',states={'done': [('readonly', True)]}),
        'line_ids'      : fields.one2many('material.requisition.line','requisition_id','Products to Purchase',required=True),
        'warehouse_id'  : fields.many2one('stock.warehouse', 'Warehouse'),        
        'state'         : fields.selection([('draft','Draft'),('lv_1','Waiting Manager Approve'),
                                            ('lv_2','Waiting Kadiv Approve'),('lv_3','Waiting CFO'),
                                            ('lv_4','Waiting Warehouse User'),
                                            ('cancel','Cancelled'),('done','Done')], 'State', required=True),
        
        'department': fields.many2one('hr.department', 'Department'),
        'department_rel_employee': fields.related('req_employee', 'department_id', relation='hr.department',type='many2one', string='Department',store=True, readonly=True),
        'division_rel_employee': fields.related('department', 'division_id', relation='hr.division',type='many2one', string='Division',store=True, readonly=True),
        
        'req_employee'  : fields.many2one('hr.employee', 'Request By', required=True),
        'user_id'       : fields.many2one('res.users', 'Created By',required=True),
        #'delegate'      : fields.many2one('res.users', 'Delegate to'),
        
        'user_app': fields.datetime('User Approve Date'),
        'manager_app': fields.datetime('Manager Approve Date'),
        'kadiv_app': fields.datetime('Kadiv Approve Date'),
        'ceo_app': fields.datetime('CEO Approve Date'),
        'warehouse_app': fields.datetime('Warehouse Approve Date'),
        'stock_picking_id': fields.many2many('stock.picking','mr_sp_rel','sp_id','mr_id','Stock Picking'),
        'ext_note':fields.text('Extra Notes', readonly=False,),
        'extra_note_line_ids': fields.one2many('extra.note.line', 'requisition_id','Extra Notes Lines'),
        'note_line_ids': fields.one2many('note.line', 'requisition_id','Notes Lines'),
        'budget_info_ids': fields.many2many('budget.info', 'budget_info_rel', 'material_req_id', 'budget_info_id', 'Budget Line', readonly=True),
        #'stock_picking_id2': fields.one2many('stock.picking', 'id', 'Stock Picking'),
        
        
        'approve_status': fields.function(_get_approve_status, method=True, string='To be Approve By',type= 'char', size=64),
                   
        
        'int_status': fields.function(_get_status, method=True, string='Internal Move Status', 
           type= 'selection', 
           selection = [
                ('draft', 'Draft'),
                ('auto', 'Waiting'),
                ('confirmed', 'Waiting Approval'),
                ('approval','Confirmed'),
                ('assigned', 'Available'),
                ('done', 'Done'),
                ('cancel', 'Cancelled'),
                ('', ''),
                    ],
            store={
                'material.requisition'  : (_get_material_request, None, 50),
                'stock.picking'         : (_get_stock_picking, None, 50),
                'purchase.requisition'  : (_get_purchase_requisition, None, 50),
                'purchase.order'        : (_get_purchase_order, None, 50),
                #'stock.picking'         : (_get_incoming, None, 50),
                    },
                    multi='all'),
        
        'pr_status': fields.function(_get_status, method=True, string='Purchase Requisition Status', 
           type= 'selection', 
           selection = [
                ('draft','Draft'),
                ('in_progress','In Progress'),
                ('cancel','Cancelled'),
                ('done','Done'),
                ('', ''),
                    ],
            store={
                'material.requisition'  : (_get_material_request, None, 50),
                'stock.picking'         : (_get_stock_picking, None, 50),
                'purchase.requisition'  : (_get_purchase_requisition, None, 50),
                'purchase.order'        : (_get_purchase_order, None, 50),
                #'stock.picking'         : (_get_incoming, None, 50),
                    },
                    multi='all'),
                    
        'po_status': fields.function(_get_status, method=True, string='Purchase Order Status', 
           type= 'selection', 
           selection = [
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
                ('cancel', 'Cancelled'),
                ('in_progress', 'In Progress'),
                ('', ''),
                    ],
            store={
                'material.requisition'  : (_get_material_request, None, 50),
                'stock.picking'         : (_get_stock_picking, None, 50),
                'purchase.requisition'  : (_get_purchase_requisition, None, 50),
                'purchase.order'        : (_get_purchase_order, None, 50),
                #'stock.picking'         : (_get_incoming, None, 50),
                    },
                    multi='all'),
                    
#        'in_status': fields.function(_get_status, method=True, string='Internal Move Status', 
#           type= 'selection', 
#           selection = [
#                ('draft', 'Draft'),
#                ('auto', 'Waiting'),
#                ('confirmed', 'Waiting Approval'),
#                ('approval','Confirmed'),
#                ('assigned', 'Available'),
#                ('done', 'Done'),
#                ('cancel', 'Cancelled'),
#                ('in_progress', 'In Progress'),
#                    ],
#            store={
#                'stock.picking'         : (_get_stock_picking, None, 50),
#                'purchase.requisition'  : (_get_purchase_requisition, None, 50),
#                'purchase.order'        : (_get_purchase_order, None, 50),
#                #'stock.picking'         : (_get_incoming, None, 50),
#                    },
#                    multi='all'),
        
        
    }
    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
        'exclusive': 'multiple',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'material.requisition', context=c),
        'user_id': lambda self, cr, uid, context: uid,
        'name': '/',#lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'material.requisition'),
        'department': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, context=c).context_department_id.id,
        #'req_employee': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)]),),
        
     }
    
    def onchange_request_employee(self,cr,uid,ids,req_employee,context=None):
        #print "req_employee",req_employee
        if not context:
            context={}
            
        if req_employee:
            employee = self.pool.get('hr.employee').browse(cr,uid,req_employee,context)
            return {'value':{'department':employee.department_id.id}}
        else:
            return {'value':{'department':'', 'req_employee':''}}
    
material_requisition()


class material_requisition_line(osv.osv):
    
    _name = "material.requisition.line"
    _description="Material Requisition Line"
    _rec_name = 'product_id'
    
    def _get_budget(self, cr, uid, ids, field_name, arg=None, context=None):
        result = {}
        val={}
        for budget in self.browse(cr, uid, ids, context=context):
            #result[budget.id] = budget.account_analytic_id
            if budget.account_analytic_id:
                val.update({budget.id:'yes'})
            else:
                val.update({budget.id:'no'})
        return val
    
    _columns = {
        'product_id'            : fields.many2one('product.product', 'Product' ),
        'info'                  : fields.char('Information',size=128),
        'product_uom_id'        : fields.many2one('product.uom', 'Product UoM'),
        'product_qty'           : fields.float('Quantity', digits=(16,2)),
        'requisition_id'        : fields.many2one('material.requisition','Purchase Requisition', ondelete='cascade'),
        'company_id'            : fields.many2one('res.company', 'Company', required=True),
        'price'                 : fields.float('Price', required=False),
        'with_budget'           : fields.function(_get_budget, method=True, string="Budget / No Budget", type='selection', selection=[('yes','Budget'),('no','No Budget')]),
        'account_analytic_id'   :fields.many2one('account.analytic.account', 'Analytic Account',),
        #'subtotal': fields.function(_amount_line, method=True, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'subtotal'              : fields.float('Subtotal', required=False),
        'description'           : fields.char('Description', size=32,required=False),
        'detail'                : fields.text('Detail'),
        #'budget_line_ids': fields.many2many('ad_budget.line', 'mr_line_rel', 'mr_line_id', 'budget_line_id', 'analytic_id', 'Budget Line', readonly=True),
    }

    def onchange_product_id(self, cr, uid, ids, department,product_id,product_uom_id, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        
        budget_analytic = False
        value = {'product_uom_id': ''}
        
        if not department:
            raise osv.except_osv(_('No Employee Defined !'),_("You must first select a Employee !") )
        
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            
            account_expense = prod.property_account_expense.id
            type_product    = prod.type
            #print "account_expense ::", account_expense
            #print "product ::::", product_id.name
            if type_product == 'consu':
                value = {'product_id':'', 'product_uom_id': '','product_qty':1.0,'price':'' ,'account_analytic_id':''}
                warning = {
                    "title": ("Product Type"),
                    "message": (("You Can not Product selected with Type Consumable"))
                }
                return {'warning': warning ,'value': value}
            
            if not account_expense:
                value = {'product_id':'', 'product_uom_id': '','product_qty':1.0,'price':'' ,'account_analytic_id':''}
                warning = {
                    "title": ("Account Expense Product No Define"),
                    "message": (("Please Define Account Expense for Product '%s'") % (prod.name))
                }
                return {'warning': warning ,'value': value}
            
            ###############################################
            
            if prod.property_account_expense.user_type.report_type == 'asset':
                print "ASSET"
                div_id = self.pool.get('hr.department').browse(cr, uid, department).division_id.id
                print "div_id", div_id
                dept_browse = self.pool.get('hr.department').search(cr, uid, [('division_id','=',div_id),('dept_general','=',True)])
                print "sssss", dept_browse, type(dept_browse)
                if dept_browse:
                    try:
                        department=dept_browse[0]
                    except:
                        department = dept_browse
                
                analytic_account_search = self.pool.get('account.analytic.account').search(cr, uid, [('budget_expense','=',account_expense), ('department_id','=',department)])
                analytic_account_browse = self.pool.get('account.analytic.account').browse(cr, uid, analytic_account_search)
                print "Department ::::", department, "Account EXP ::", account_expense
                if analytic_account_browse:
                    print "ada analitic"
                    for item in analytic_account_browse:
                        print "ITEM ::", item.name
                        budget_analytic_id = item.id
                        
                    budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('dept_relation','=',department)])
                    budget_line_browse = self.pool.get('ad_budget.line').browse(cr, uid, budget_line_search)
                    
                    if budget_line_browse:
                        #print "Dept ada", department
                        for budget_line_item in budget_line_browse:
                            budget_line_analytic_id = budget_line_item.analytic_account_id.id
                    
                        value = {'product_uom_id': prod.uom_id.id,'price':prod.standard_price,'account_analytic_id':budget_line_analytic_id}
                    else :
                        value = {'product_uom_id': prod.uom_id.id,'price':prod.standard_price,'account_analytic_id':''}
                else:
                    print "Tidak ada analitic"
                    value = {'product_uom_id': prod.uom_id.id, 'price':prod.standard_price,'account_analytic_id':''}
                
            else:
                print "NON ASSET"
                analytic_account_search = self.pool.get('account.analytic.account').search(cr, uid, [('budget_expense','=',account_expense), ('department_id','=',department)])
                analytic_account_browse = self.pool.get('account.analytic.account').browse(cr, uid, analytic_account_search)
                print "Department ::::", department, "Account EXP ::", account_expense
                if analytic_account_browse:
                    print "ada analitic"
                    for item in analytic_account_browse:
                        print "ITEM ::", item.name
                        budget_analytic_id = item.id
                        
                    budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('dept_relation','=',department)])
                    budget_line_browse = self.pool.get('ad_budget.line').browse(cr, uid, budget_line_search)
                    
                    if budget_line_browse:
                        #print "Dept ada", department
                        for budget_line_item in budget_line_browse:
                            budget_line_analytic_id = budget_line_item.analytic_account_id.id
                    
                        value = {'product_uom_id': prod.uom_id.id,'price':prod.standard_price,'account_analytic_id':budget_line_analytic_id}
                    else :
                        value = {'product_uom_id': prod.uom_id.id,'price':prod.standard_price,'account_analytic_id':''}
                else:
                    print "Tidak ada analitic"
                    value = {'product_uom_id': prod.uom_id.id, 'price':prod.standard_price,'account_analytic_id':''}
############################Diremove MR bisa tanpa budget#################################
#            else:
#                value = {'product_id':'', 'product_uom_id': '','product_qty':1.0,'price':'' ,'account_analytic_id':''}
#                warning = {
#                    "title": ("Budget Product No Define"),
#                    "message": ("Please Check Budget Item for this Product")
#                }
#                raise osv.except_osv(_('Error !'), _('Budget Product No Define.'))
            
            #value = {'product_uom_id': prod.uom_id.id,'product_qty':1.0,'price':prod.standard_price,'account_analytic_id':budget_analytic_id}
        return {'value': value}

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.requisition.line', context=c),
        'product_qty': 1,
    }
material_requisition_line()

class extra_note_line(osv.osv):
    _name = "extra.note.line"
    _description = "Extra Note Lines"
    
    _columns = {
            'requisition_id' : fields.many2one('material.requisition','Purchase Requisition', ondelete='cascade'),
            'date' : fields.datetime('Notes Date',required=False),
            'description' : fields.char('Description', size=64),
            'user' : fields.many2one('res.users','User Name'),
                }
    
extra_note_line()

class note_line(osv.osv):
    _name = "note.line"
    _description = "Note Lines"
    
    _columns = {
            'requisition_id' : fields.many2one('material.requisition','Purchase Requisition', ondelete='cascade'),
            'date' : fields.datetime('Notes Date',required=False),
            'description' : fields.char('Description', size=64),
            'user' : fields.many2one('res.users','User Name'),
                }
    
note_line()