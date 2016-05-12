import time
from lxml import etree

import netsvc
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _

class pool_budget(osv.osv):
    _name = 'pool.budget'
    
    _columns = {
            'account_id'    :fields.many2one('account.account','Account', required=True),
            'department_id' :fields.many2one('hr.department','Department', required=True),
                }
    
    def onchange_account_id(self, cr, uid, ids, account_id):
        pool_search = self.search(cr, uid, [('account_id','=',account_id)])
        pool_browse = self.browse(cr, uid, pool_search)
        
        if pool_browse:
            warning = {
                        "title": ("Duplicated Account !"),
                        "message": ("You can not insert with same account ")
                    }
            value = {'account_id' : ""}
            return {'warning': warning, 'value': value}
        
        return {'value': {'account_id' : account_id}}
    
    def check_pool_account(self, cr, uid, ids, account_id=None, department_id=None, context=None):
        budget_line_analytic_id = False
        pool_search = self.search(cr, uid, [('account_id','=',account_id)])
        pool_browse = self.browse(cr, uid, pool_search)
        
        if pool_browse:
            for pool in pool_browse:
                department_id = pool.department_id.id
                print "department_id", department_id, pool.department_id.name
                cr.execute("select id from account_analytic_account WHERE budget_expense = %s AND department_id = %s",(str(account_id),str(department_id),))
                
                budget_line_analytic_id = cr.fetchone()[0]
        value = {'account_analytic_id' : budget_line_analytic_id}
        
        return value
        #return value
    
pool_budget()