import time
import pooler
from report import report_sxw
#from common_report_header import common_report_header
from tools.translate import _
#import ad_budget_line
import time
    
class budget_detail(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(budget_detail, self).__init__(cr, uid, name, context=context)
        self.result_sum_dr = 0.0
        self.result_sum_cr = 0.0
        self.result = {}
        self.result_temp = []
        self.localcontext.update( {
            'sum_dr': self.sum_dr,
            'sum_cr': self.sum_cr,
            'get_lines_another': self.get_lines_another,
            'get_data': self.get_data,
            'get_period': self.get_period,
            'get_transaction': self.get_transaction,
            'get_department' : self._get_department,
            'get_period_actual': self.get_period_actual,
            'get_period_under': self.get_period_under,
            'get_transaction_period': self.get_transaction_period,
            'get_budget_item' : self._get_budget_item,
            'get_as_of_date' : self._get_as_of_date,
            'get_period_unutilized' : self.get_period_unutilized,
            'get_desc_budget_line' : self.get_desc_budget_line,
            'get_period_budget_total' : self.get_period_budget_total,
            'get_period_actual_total' : self.get_period_actual_total,
            'get_transaction_period_total' : self.get_transaction_period_total,
        })
        self.context = context
            
    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'budget_item_id' in data['form'] and [data['form']['budget_item_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
            lang_dict = self.pool.get('res.users').read(self.cr,self.uid,self.uid,['context_lang'])
            data['lang'] = lang_dict.get('context_lang') or False
        return super(budget_detail, self).set_context(objects, data, new_ids, report_type=report_type)
    
    def sum_dr(self): 
        return self.result_sum_dr

    def sum_cr(self):
        return self.result_sum_cr
    
    def _get_budget_item(self, data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['form']['id']])
        item = obj_data[0].budget_item_select
        return item
    
    def _get_department(self, data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['form']['id']])
        dept = obj_data[0].department_select
        return dept
    
    def _get_as_of_date(self, data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['form']['id']])
        as_of = obj_data[0].as_of_date
        return as_of
    
    def get_period(self, as_of, period, budget_item_id, date_start, date_end, type, item, dept=False,  context=None):
#        print "+++++++++++???????????????????????????????????????//+",period, budget_item_id, date_start, date_end, type, item, dept
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        peri_pool = db_pool.get('account.period')
        res = {}
        res[budget_item_id] = 0.0
        ########################ARYA############################
        if type == 'view':
#            print ">>>>>>>>>>Masuk<<<<<<<<<"
            budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
            budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
            total_view = 0.0
            #res[budget_item_id] = 0.0
            periode_id = peri_pool.search(cr,uid,[('date_start','<=',as_of),('date_stop','>=',as_of)])[0]
            periode_obj= peri_pool.browse(cr,uid,periode_id)
            for budget in budgets:
#                print "ANAK VIEW ==>", budget.id
                if dept:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                else:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id)])
                if line_ids:
                    for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
#                        print "View SELECT----------------------->>", budget.id
                        date_from = '2012-10-01'
                        date_to = '2012-10-31'
                        analytic_account_id = line.analytic_account_id.id
                        
#                        periode_ids = peri_pool.search(cr,uid,[('date_start','>=',period_obj.fiscalyear_id.date_start),('date_start','<=',period_obj.date_stop)])
                        
#                        print "analytic_account_id :::::", analytic_account_id, date_from, date_to
                        if line.amount <> 0.00 or line.amount == 0.00:
                            amount = float(line.amount)
#                            if periode_id == period:
#                                cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
#                                       "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
#                                result = cr.dictfetchone()
##                            print "amount**********************%%%", result
#                                if result['balance_real'] is None:
#                                    amount = result['balance_real'] = 0.0
#                                else:
#                                    amount = abs(result['balance_real'])
                            #print "xxxx",xxx
                            res[budget_item_id] = res[budget_item_id] + amount
#                        print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww", res[budget_item_id]
            return res[budget_item_id]
        ####################################################

        
        if dept:
#            print "******************************************************", dept
            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
        else:
#            print "000000000000000000000000000000000000000000000000000000000", dept
            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id)])
        #line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id)])
#        print "line_ids", line_ids
        #line_id = self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids)
        total = 0.0
        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
            #print "++", line.id, "==", line.amount, "IOW", line.balance_real
#            print "#######################################################################"
            budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
            budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
            
            for budget in budgets:
#                print "*********************************************8", budget
            
                if line.amount <> 0.00 or line.amount == 0.00:
                    amount = float(line.amount)
                    
                    res[budget_item_id] = res[budget_item_id] + amount
#                if line.amount <> 0.00:
#                    res[budget_item_id] = float(line.amount - line.balance_real)
#                    print "res[budget_item_id]^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", res[budget_item_id]
                    total = total + res[budget_item_id]
                    #print "total"
                    #return total
                else:
#                    print "----------------------->>>+++ MASUK****", line.amount
                    res[budget_item_id] = 0.00
                    #return 0.0
        return total
    
    def get_period_budget_total(self, fy, as_of, budget_item_id, type, dept=False,  context=None):
       
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        peri_pool = db_pool.get('account.period')
        fy_pool = db_pool.get('account.fiscalyear')
        
        end_fy = fy_pool.browse(self.cr, self.uid, fy).date_stop
        #print "end_fy_________________-----", end_fy
        
        cr.execute("SELECT id FROM account_period WHERE to_char(date_stop,'yyyy-mm') <= %s AND fiscalyear_id = %s ",(str(end_fy),str(fy),))
        period_ids = map(lambda x: x[0], cr.fetchall())
        minimum = min(period_ids)
        date_start = db_pool.get('account.period').browse(cr, uid, minimum).date_start
        
        res = {}
        total_view = 0.0
        analytic = False
        result = 0.0
        res[budget_item_id] = 0.0
        ########################ARYA############################
        if type == 'view':
#            print ">>>>>>>>>>Masuk<<<<<<<<<"
            budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
            budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
            total_view = 0.0
            for budget in budgets:
#                print "ANAK VIEW ==>", budget.id
                if dept:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                else:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id)])
                if line_ids:
                    for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                        result += line.amount
                    total_view += result
            print total_view
            return abs(total_view)
        else:
            if dept:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
            else:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget_item_id)])
            
            for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                result += line.amount
            #result = 0.0
        return abs(result)
    
    def get_period_actual_total(self, fy, as_of, budget_item_id, type, dept=False,  context=None):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        peri_pool = db_pool.get('account.period')
        
        cr.execute("SELECT id FROM account_period WHERE to_char(date_stop,'yyyy-mm') <= %s AND fiscalyear_id = %s ",(str(as_of),str(fy),))
        period_ids = map(lambda x: x[0], cr.fetchall())
        minimum = min(period_ids)
        date_start = db_pool.get('account.period').browse(cr, uid, minimum).date_start
        
        res = {}
        total_view = 0.0
        analytic = False
        result = 0.0
        res[budget_item_id] = 0.0
        ########################ARYA############################
        if type == 'view':
#            print ">>>>>>>>>>Masuk<<<<<<<<<"
            budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
            budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
            total_view = 0.0
            #res[budget_item_id] = 0.0
            #periode_id = peri_pool.search(cr,uid,[('date_start','<=',as_of),('date_stop','>=',as_of)])[0]
            #periode_obj= peri_pool.browse(cr,uid,periode_id)
            for budget in budgets:
#                print "ANAK VIEW ==>", budget.id
                if dept:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                else:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id)])
                if line_ids:
                    for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                        analytic = line.analytic_account_id.id
                    if analytic:
                        cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                                    "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic, date_start, as_of,))
                        result = cr.fetchone()[0]
                        if result is None:
                            result = 0.0
                        total_view += result
            
            return abs(total_view)
        else:
            if dept:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
            else:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget_item_id)])
            
            for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                analytic = line.analytic_account_id.id
            if analytic:
                cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                            "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic, date_start, as_of,))
                result = cr.fetchone()[0]
                if result is None:
                    result = 0.0
        
        return abs(result)

    def get_transaction_period_total(self, fy, as_of, budget_item_id, type, item, dept=False,  context=None):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        peri_pool = db_pool.get('account.period')
        
        cr.execute("SELECT id FROM account_period WHERE to_char(date_stop,'yyyy-mm') <= %s AND fiscalyear_id = %s ",(str(as_of),str(fy),))
        period_ids = map(lambda x: x[0], cr.fetchall())
        minimum = min(period_ids)
        date_start = db_pool.get('account.period').browse(cr, uid, minimum).date_start
        
        res = {}
        total_view = 0.0
        analytic = False
        result = 0.0
        res[budget_item_id] = 0.0
        ########################ARYA############################
        if type == 'view':
            budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
            budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
            total_view = 0.0
            for budget in budgets:
                if dept:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                else:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id)])
                if line_ids:
                    for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                        analytic = line.analytic_account_id.id
                    if analytic:
                        cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                                    "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic, date_start, as_of,))
                        result = cr.fetchone()[0]
                        if result is None:
                            result = 0.0
                        total_view += result
            
            return abs(total_view)
        else:
            if dept:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
            else:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ids),('budget_item_id','=',budget_item_id)])
            
            for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                analytic = line.analytic_account_id.id
            if analytic:
                cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                            "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic, date_start, as_of,))
                result = cr.fetchone()[0]
                if result is None:
                    result = 0.0
        
        return abs(result)


    def get_period_actual(self, as_of, period, budget_item_id, date_start, date_end, type, item, dept=False, context=None):
#        print "+++++++++++???????????????????????????????????????//+get_period_actual",period, budget_item_id, date_start, date_end, type, item, dept
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        peri_pool = db_pool.get('account.period')
        periode_id = peri_pool.search(cr,uid,[('date_start','<=',as_of),('date_stop','>=',as_of)])[0]
        periode_obj= peri_pool.browse(cr,uid,periode_id)
        selected_period = peri_pool.browse(cr,uid,period)
        res = {}
        res[budget_item_id] = 0.0
        
        period_ytd = peri_pool.search(cr,uid,[('date_start','>=',periode_obj.fiscalyear_id.date_start),('date_stop','<=',periode_obj.date_stop)])
        ########################ARYA############################
        if period in period_ytd:
            if type == 'view':
                
                budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
                budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
                total_view = 0.0
                for budget in budgets:
                    if dept:
                        line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                    else:
                        line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id)])
                    if line_ids:
                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                            
                            if line.amount <> 0.00 or line.amount == 0.00:
                                amount = float(line.balance_real)
                                if periode_id == period:
                                    analytic_account_id = line.analytic_account_id.id
                                    date_from   = periode_obj.date_start
                                    date_to     = as_of
                                    cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                                           "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
                                    result = cr.dictfetchone()
                                    if result['balance_real'] is None:
                                        amount = result['balance_real'] = 0.0
                                    else:
                                        amount = abs(result['balance_real'])
                                res[budget_item_id] = res[budget_item_id] + amount
                return res[budget_item_id]
            ####################################################
    
            
            if dept:
    #            print "******************************************************", dept
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
            else:
    #            print "000000000000000000000000000000000000000000000000000000000", dept
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id)])
            #line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id)])
    #        print "line_ids", line_ids
            #line_id = self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids)
            total = 0.0
            for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                #print "++", line.id, "==", line.amount, "IOW", line.balance_real
    #            print "#######################################################################"
                budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
                budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
                
                for budget in budgets:
    #                print "*********************************************8", budget
                
                    if line.amount <> 0.00 or line.amount == 0.00:
                        amount = float(line.balance_real)
                        
                        if periode_id == period:
                            analytic_account_id = line.analytic_account_id.id
                            date_from   = periode_obj.date_start
                            date_to     = as_of
                            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                                   "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
                            result = cr.dictfetchone()
#                            print "amount**********************%%%", result
                            if result['balance_real'] is None:
                                amount = result['balance_real'] = 0.0
                            else:
                                amount = abs(result['balance_real'])
                        
                        res[budget_item_id] = res[budget_item_id] + amount
    #                if line.amount <> 0.00:
    #                    res[budget_item_id] = float(line.amount - line.balance_real)
    #                    print "res[budget_item_id]^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", res[budget_item_id]
                        total = total + res[budget_item_id]
                        #print "total"
                        #return total
                    else:
    #                    print "----------------------->>>+++ MASUK****", line.amount
                        res[budget_item_id] = 0.00
                        #return 0.0
        else:
            total=0.0
        return total
    
    def get_desc_budget_line(self, as_of, period, budget_item_id, date_start, date_end, type, item, dept=False, context=None):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        peri_pool = db_pool.get('account.period')
        periode_id = peri_pool.search(cr,uid,[('date_start','<=',as_of),('date_stop','>=',as_of)])[0]
        periode_obj= peri_pool.browse(cr,uid,periode_id)
        selected_period = peri_pool.browse(cr,uid,period)
        res = {}
        res[budget_item_id] = 0.0
        
        ########################ARYA############################
        desc = ''

        if dept:
            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
        else:
            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id)])
        #total = 0.0
        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
            desc = line.name or ''
        return desc
    
    
    def get_period_unutilized(self, as_of, period, budget_item_id, date_start, date_end, type, item, dept=False, context=None):
#        print "+++++++++++???????????????????????????????????????//+get_period_actual",period, budget_item_id, date_start, date_end, type, item, dept
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        peri_pool = db_pool.get('account.period')
        periode_id = peri_pool.search(cr,uid,[('date_start','<=',as_of),('date_stop','>=',as_of)])[0]
        periode_obj= peri_pool.browse(cr,uid,periode_id)
        selected_period = peri_pool.browse(cr,uid,period)
        res = {}
        res[budget_item_id] = 0.0
        
        period_ytd = peri_pool.search(cr,uid,[('date_start','>=',periode_obj.fiscalyear_id.date_start),('date_stop','<=',periode_obj.date_stop)])
        ########################ARYA############################
        if not period in period_ytd:
            if type == 'view':
                budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
                budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
                total_view = 0.0
                for budget in budgets:
                    if dept:
                        line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                    else:
                        line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id)])
                    if line_ids:
                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                            if line.amount <> 0.00 or line.amount == 0.00:
                                amount = float(line.amount)

                                res[budget_item_id] = res[budget_item_id] + amount
                return res[budget_item_id]
            ####################################################
    
            
            if dept:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
            else:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id)])
            total = 0.0
            for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
                budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
                
                for budget in budgets:
#                    if line.amount <> 0.00:
                    amount = float(line.amount)
                    total = total + amount
            return total
#                        res[budget_item_id] = res[budget_item_id] + amount
#                        result = res[budget_item_id]
#                    else:
#                        res[budget_item_id] = 0.00
        else:
            total = 0.0
        
        return total
    
    def get_period_under(self, as_of, period, budget_item_id, date_start, date_end, type, item, dept=False, context=None):
        #print "+++++++++++???????????????????????????????????????//+get_period_under",period, budget_item_id, date_start, date_end, type, item, dept
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        peri_pool = db_pool.get('account.period')
        periode_id = peri_pool.search(cr,uid,[('date_start','<=',as_of),('date_stop','>=',as_of)])[0]
        periode_obj= peri_pool.browse(cr,uid,periode_id)
        selected_period = peri_pool.browse(cr,uid,period)
        res = {}
        res[budget_item_id] = 0.0
        ########################ARYA############################
        period_ytd = peri_pool.search(cr,uid,[('date_start','>=',periode_obj.fiscalyear_id.date_start),('date_stop','<=',periode_obj.date_stop)])
        
        if period in period_ytd:
            if type == 'view':
    #            print ">>>>>>>>>>Masuk<<<<<<<<<"
                budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
                budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
                total_view = 0.0
                #res[budget_item_id] = 0.0
                for budget in budgets:
    #                print "ANAK VIEW ==>", budget.id
                    if dept:
                        #print "******************************************************", dept
                        line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                    else:
                        #print "000000000000000000000000000000000000000000000000000000000", dept
                        line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id)])
                    if line_ids:
                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
    #                        print "View SELECT----------------------->>", budget.id
                            if line.amount <> 0.00 or line.amount == 0.00:
                                balance_real = line.balance_real
                                if periode_id == period:
                                    analytic_account_id = line.analytic_account_id.id
                                    date_from   = periode_obj.date_start
                                    date_to     = as_of
                                    cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                                           "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
                                    result = cr.dictfetchone()
    #                            print "amount**********************%%%", result
                                    if result['balance_real'] is None:
                                        balance_real = result['balance_real'] = 0.0
                                    else:
                                        balance_real = abs(result['balance_real'])
                                
                                amount = float(line.amount-balance_real)
                                
                                res[budget_item_id] = res[budget_item_id] + amount
    #                        print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww", res[budget_item_id]
                return res[budget_item_id]
            ####################################################
    
            
            if dept:
    #            print "******************************************************", dept
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
            else:
    #            print "000000000000000000000000000000000000000000000000000000000", dept
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id)])
            total = 0.0
            for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
                budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
                
                for budget in budgets:
                    if line.amount <> 0.00 or line.amount == 0.00:
                        balance_real = line.balance_real
                        if periode_id == period:
                            analytic_account_id = line.analytic_account_id.id
                            date_from   = periode_obj.date_start
                            date_to     = as_of
                            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                                   "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
                            result = cr.dictfetchone()
                            if result['balance_real'] is None:
                                balance_real = result['balance_real'] = 0.0
                            else:
                                balance_real = abs(result['balance_real'])
                        amount = float(line.amount-balance_real)
                        res[budget_item_id] = res[budget_item_id] + amount
                        total = total + res[budget_item_id]
                    else:
                        res[budget_item_id] = 0.00
        else:
            if type == 'view':
                budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
                budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
                total_view = 0.0
                for budget in budgets:
                    if dept:
                        line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                    else:
                        line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id)])
                    if line_ids:
                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                            if line.amount <> 0.00 or line.amount == 0.00:
                                
                                amount = float(line.amount)
                                
                                res[budget_item_id] = res[budget_item_id] + amount
                return res[budget_item_id]
            ####################################################
    
            
            if dept:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
            else:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id)])
            total = 0.0
            for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
                budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
                
                for budget in budgets:
                    if line.amount <> 0.00 or line.amount == 0.00:
                        
                        amount = float(line.amount)
                        res[budget_item_id] = res[budget_item_id] + amount
                        total = total + res[budget_item_id]
        return total
                    
    def get_transaction(self, as_of, budget_item, dept=False):
#        print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx...", budget_item, dept
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        analytic_line = db_pool.get('account.analytic.line')
        budget_line = db_pool.get('ad_budget.line')
        if dept == False:
            analytic_search = budget_line.search(cr, uid, [('budget_item_id','=',budget_item)])
        else:
            analytic_search = budget_line.search(cr, uid, [('budget_item_id','=',budget_item), ('analytic_account_id.department_id','=',dept)])
        analytic_browse = budget_line.browse(cr, uid, analytic_search)
        
        if len(analytic_browse)>0:
            for analytic in analytic_browse:
                analytic_id = analytic.analytic_account_id.id
#                print "ttttttttttttttttttttt", analytic_id
                trans_search = analytic_line.search(cr, uid, [('account_id','=',analytic_id),('date','<=',as_of)])
                trans_browse = analytic_line.browse(cr, uid, trans_search)
        else:
            trans_browse=[]
        return trans_browse
    
    def get_transaction_period(self, as_of, budget_item, date_start, date_end, analytic_line_id, dept=False):
#        print "ggggggggggggggggggggggggggggggggggggggggggggg...", budget_item, date_start, date_end, analytic_line_id, dept
        #print "as_of", as_of
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        analytic_line = db_pool.get('account.analytic.line')
        budget_line = db_pool.get('ad_budget.line')
        if dept == False:
            analytic_search = budget_line.search(cr, uid, [('budget_item_id','=',budget_item)])
        else:
            analytic_search = budget_line.search(cr, uid, [('budget_item_id','=',budget_item), ('analytic_account_id.department_id','=',dept)])
        analytic_browse = budget_line.browse(cr, uid, analytic_search)
        amount = 0.0
        if analytic_browse:
            for analytic in analytic_browse:
                analytic_id = analytic.analytic_account_id.id
#                print "ttttttttttttttttttttt", analytic_id
                if date_end <= as_of:
                    trans_search = analytic_line.search(cr, uid, [('account_id','=',analytic_id),('date','>=',date_start), ('date','<=',date_end), ('id','=',analytic_line_id)])
                else:
                    trans_search = analytic_line.search(cr, uid, [('account_id','=',analytic_id),('date','>=',date_start), ('date','<=',as_of), ('id','=',analytic_line_id)])
                trans_browse = analytic_line.browse(cr, uid, trans_search)
            #trans_search = analytic_line.search(cr, uid, [('account_id','=',analytic_id),('date','>=',date_start), ('date','<=',date_end)])
                if trans_browse:
                    for i in trans_browse:
                        amount = i.amount
        
        return abs(amount)
    
    def get_data(self, data):
        done = None
        if not done:
            done = {}
        level = 0
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)

        budget_pool = db_pool.get('ad_budget.item')
        budget_lines_obj = db_pool.get('ad_budget.line')
        currency_pool = db_pool.get('res.currency')
        period_pool = db_pool.get('account.period')
        period_ids = period_pool.search(cr, uid, [('fiscalyear_id','=',data['form']['fiscalyear_id'])])
        periods = period_pool.browse(cr, uid, period_ids)
        dept = data['form']['department_select']
#        print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", dept
        
        ctx = self.context.copy()
        ##################Perbaikan Net Loss Menjadi hanya yg Posted######################
#        ctx['state'] = "posted"
        #########################################
        accounts = {}
        cal_list = {}
        budgets_levels = {}
        #budget_id = data['form'].get('budget_item_id', False)
        budget_id = data['form'].get('budget_item_select', False)
#        budget_lines_obj.search(cr, uid, [('budget_item_id','=',budget_id),('dept_relation','=',dept)])
#        if 
        #print "contteeexxxxxxxxxxxxx",ctx
#        print "budget_id----------->>", budget_id
#        budget_ids = budget_pool._get_children_and_consol(cr, uid, budget_id, context=ctx)
#        
#        if data['form']['with_detail'] == True:
#            budgets = budget_pool.browse(cr, uid, budget_ids, context=ctx)
#        else:
#            budgets = budget_pool.browse(cr, uid, budget_id, context=ctx)
        child_ids = budget_pool._get_children_and_consol(cr, uid, budget_id, context=ctx)
        if child_ids:
            budget_ids = child_ids
        budgets = budget_pool.read(self.cr, self.uid, budget_ids, ['type','code','name','balance_budget','parent_id','level','type_budget'], context=ctx)
        budgets.sort(lambda x,y: cmp(x['code'], y['code']))
        res = []

        for budget in budgets:
            budget_id = budget['id']

            if budget_id in done:
                continue

            done[budget_id] = 1

            #
            # Calculate the account level
            #
            parent_id = budget['parent_id']
            if parent_id:
                if isinstance(parent_id, tuple):
                    parent_id = parent_id[0]
                budget_level = budgets_levels.get(parent_id, 0) + 1
            else:
                budget_level = level
            budgets_levels[budget_id] = budget_level
            #print "sssss",budgets_levels[budget_id],budget_id,parent_id
            if not data['form']['display_account_level'] or budget_level <= data['form']['display_account_level']:
                values = {
                    'name': budget['name'],
                    'id': budget['id'],
                    'balance': budget['balance_budget'],
                    'type': budget['type'],
                    'code' : budget['code'],
                    'level' : budget['level'],
                    'parent_id': budget['parent_id'],
                    'item' : data['form']['budget_item_select'],
                    'as_of' : data['form']['as_of_date'],
                }
                res.append(values)

        return res
        

    def get_lines_another(self, data):
#        print "get_lines_another",data
        return self.result.get(data['1']['id'], [])

report_sxw.report_sxw('report.budget.detail.pdf', 'ad_budget.item', 'addons/ad_budget_detail/report/budget_detail.mako', parser = budget_detail)
#report_sxw.report_sxw('report.sale.item.sold.report', 'sale.order', 'addons/ad_report_sales/report/report_item_sold_webkit.mako', parser = ReportStatus)
        