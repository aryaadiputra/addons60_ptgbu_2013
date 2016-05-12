import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter

import netsvc
import pooler
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _


class account_move(osv.osv):
    _inherit = "account.move.line"
    
    _columns = {
            #'dept_id': fields.many2one('hr.department', "Department",),
                }
    
    def compute_vat(self, cr, uid, ids, context=None):
        #print "cccccccccccccc"
        search_vat = self.search(cr, uid, [('name','=','VAT In - VAT In'), ('analytic_account_id','=',False)])
        print "search_vat", search_vat
        no = 0
        total = 0
        for i in self.browse(cr, uid, search_vat):
            account_id      = i.account_id.id
            date            = i.date
            move_id         = i.move_id.id
            currency_id     = i.currency_id.id
            journal_id      = i.journal_id.id
            amount          = i.credit - i.debit
            amount_currency = i.amount_currency
            ref             = i.ref
            search_vat2 = self.search(cr, uid, [('move_id','=',move_id), ('analytic_account_id','<>', False), ('account_id','=',account_id)],order='move_id')
            mvline=False
            if search_vat2:
                mvline          = search_vat2[0]
                mvlinedata      = self.browse(cr,uid,mvline)
                #account_id      = mvlinedata.account_id.id
                dept            = mvlinedata.analytic_account_id.department_id.id
                no += 1
                analytic_search      = self.pool.get('account.analytic.account').search(cr,uid,[('budget_expense','=',account_id),('department_id','=',dept)])
                total += i.credit - i.debit
                
                print no, "+++++++", ids,"^^^^^^^^^", i.move_id.id, "+++++",i.name, "-----------", i.id, 'wwwwwwwwwwwwwww', analytic_search, account_id, dept, i.currency_id.id, i.debit - i.credit, total
                new_name = i.name +" *"
                self.write(cr, uid, [i.id], {'name' : new_name, 'analytic_account_id' : analytic_search[0]})
                
#                vals_lines = {
#                        'amount' : amount,
#                        'user_id' : 1,
#                        'name' : 'VAT In - VAT In *',
#                        'unit_amount' : 1,
#                        'date' : date,
#                        'company_id' : 1,
#                        'account_id' : analytic_search[0],
#                        'general_account_id' : account_id,
#                        'currency_id' : currency_id,
#                        'move_id' : i.id,
#                        'journal_id' : journal_id,
#                        'amount_currency' : amount_currency,
#                        'ref' : ref,
#                        
#                              }
#                
#                self.pool.get('account.analytic.line').create(cr, uid, vals_lines)
            
    
account_move()