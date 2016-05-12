import time
import netsvc

#from account_budget.account_budget import crossovered_budget_lines
import decimal_precision as dp
from osv import fields,osv
from tools.translate import _


class budget_line(osv.osv):
    _name = "budget.line"
    
    _columns = {
        'line_id':fields.integer('ID'),
        'general_budget_id' : fields.char('Budget Positions', size=64),
        'planned_amount' : fields.float('Planned Amount', required=False),
        'real_budget_dump' : fields.float('Real Budget', required=False),
        'percentage_dump' : fields.float('Percentage', required=False),
            }

budget_line()


class purchase_requisition_line(osv.osv):
    _inherit = "purchase.requisition.line"
    
    
    def onchange_product_id(self, cr, uid, ids, product_id,product_uom_id, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        value = {'product_uom_id': ''}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            value = {'product_uom_id': prod.uom_id.id,'product_qty':1.0, 'price':prod.standard_price}
        return {'value': value}
    
    
    _columns = {
        'price' : fields.float('Price', required=False),
        'account_analytic_id':fields.many2one('account.analytic.account', 'Analytic Account',),
            }

purchase_requisition_line()


class purchase_requisition(osv.osv):
    
    _inherit = "purchase.requisition"
    

    def compute(self, cr, uid, ids, context={}):

        obj_budget_line = self.pool.get('budget.line')
        obj_purchase_requisition = self.pool.get('purchase.requisition')
        obj_analytic_account = self.pool.get('account.analytic.account')
        obj_analytic_line = self.pool.get('account.analytic.line')
        obj_budget = self.pool.get('crossovered.budget')
        obj_budget_lines = self.pool.get('crossovered.budget.lines')
        
        pr_search = obj_purchase_requisition.search(cr,uid,[('id','=',ids)])
        pr_id = obj_purchase_requisition.browse(cr,uid, pr_search)
       
        pr_search = obj_purchase_requisition.search(cr,uid,[('id','=',ids)])
        pr_id = obj_purchase_requisition.browse(cr,uid, pr_search)
        
        for pr in pr_id:
            pr_id = pr.id
            dept_id = pr.department.id
            print "PR ID : ", pr_id
            print "DEPT : ", dept_id
            
        
        if not dept_id:
            print "kosong"
        
            warning = {}
                
            print "False"
            raise osv.except_osv(_('Warning'), _('Please Define Your Department'))
            return True
            
        old_pr_budget = obj_budget_line.search(cr, uid, [('line_id', '=', pr_id)])
        old_pr_budget_browse = obj_budget_line.browse(cr, uid, old_pr_budget)
        
        if old_pr_budget:
            print "ADA"
            
            obj_budget_line.unlink(cr, uid, old_pr_budget, context=context)
     
        print "LANJUTKAN"
        
        crossovered_budget = obj_budget.search(cr, uid, [('department', '=', dept_id)])
        crossovered_budget_id = obj_budget.browse(cr, uid, crossovered_budget)
    
        for check_budget in crossovered_budget_id:
            check_budget_id = check_budget.id
            print "check_budget_id : ", check_budget_id
            crossovered_budget_line = obj_budget_lines.search(cr, uid, [('crossovered_budget_id', '=', check_budget_id)])
            crossovered_budget_line_id = obj_budget_lines.browse(cr, uid, crossovered_budget_line)
            
            for check_budget_line in crossovered_budget_line_id:
                analytic_account_id = check_budget_line.analytic_account_id.id
                print "analytic_account_id", analytic_account_id
                
                budget_id = check_budget_line.id
                print "Account ID : ", budget_id
                
                acc_ids = [x.id for x in check_budget_line.general_budget_id.account_ids]
                
                #x = int(acc_ids)
                print "acc_ids" , acc_ids
                
                general_budget_name = check_budget_line.general_budget_id.name
                print "general_budget_name : ", general_budget_name
                
                planned_amount = check_budget_line.planned_amount
                print "planned_amount : ", planned_amount
                
                general_account_search = obj_analytic_line.search(cr, uid, [('account_id', '=', budget_id)])
                general_account_browse = obj_analytic_line.browse(cr, uid, general_account_search)
                
               
                #cr.execute("SELECT SUM(amount) FROM account_analytic_line WHERE account_id=%s" , (budget_id,))
                
                cr.execute("SELECT SUM(amount) FROM account_analytic_line WHERE account_id=%s AND general_account_id=ANY(%s)" , (analytic_account_id, acc_ids))
                remaining_budget = cr.fetchone()[0] or 0.0
                
                print "TOTAL : ", remaining_budget
                
                real_budget = planned_amount + remaining_budget
                percentage = 100 + ((remaining_budget / planned_amount) * 100)
                print "%%%%%", percentage
                
                obj_budget_line.create(cr, uid, {
                                    'line_id' : pr_id,
                                    'general_budget_id' : general_budget_name,
                                    'planned_amount' : planned_amount,
                                    'real_budget_dump' : real_budget,
                                    'percentage_dump' : percentage,
                                    }) 
                
        return True
    
    
    _columns = {
        #'mobile_phone': fields.char('Mobile Numbers', size=32,required=False, readonly=True),
        'department': fields.many2one('hr.department', 'Department',readonly=False, required=False),
        'crossovered_budget_line': fields.one2many('budget.line', 'line_id', 'Budget Lines',readonly=True),
            }
    
    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
        'exclusive': 'multiple',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.requisition', context=c),
        'user_id': lambda self, cr, uid, context: uid,
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'purchase.order.requisition'), 
        #'department': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, context=c).context_department_id.id,
        #'mobile_phone': lambda self,cr,uid,c: self.pool.get('hr.employee').browse(cr, uid, uid, context=c).mobile_phone,
                }

purchase_requisition()
