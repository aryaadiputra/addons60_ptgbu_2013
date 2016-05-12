import time
import pooler
from report import report_sxw
#from common_report_header import common_report_header
from tools.translate import _
    
class budget_rolling(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(budget_rolling, self).__init__(cr, uid, name, context=context)
        self.result_sum_dr = 0.0
        self.result_sum_cr = 0.0
        self.result = {}
        self.result_temp = []
        self.localcontext.update( {
            'get_total': self.get_total,
            'get_total_BudgetD': self.get_total_BudgetD,
            'get_lines_another': self.get_lines_another,
            'get_data': self.get_data,
            'get_period': self.get_period,
            'get_transaction': self.get_transaction,
            'get_department' : self.get_department,
            'get_total_row_cogs': self.get_total_row_cogs,
            'get_total_row_expense': self.get_total_row_expense,
            'get_total_row_Total': self.get_total_row_Total,
            'get_total_row_Budget': self.get_total_row_Budget,
            'get_dept_text': self.get_dept_text,
        })
        self.context = context
            
    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'budget_item_id' in data['form'] and [data['form']['budget_item_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
            lang_dict = self.pool.get('res.users').read(self.cr,self.uid,self.uid,['context_lang'])
            data['lang'] = lang_dict.get('context_lang') or False
        return super(budget_rolling, self).set_context(objects, data, new_ids, report_type=report_type)    
    
    def get_dept_text(self, data):
        """ Returns the text with the periods/dates used on the report. """
        dept_obj = self.pool.get('hr.department')
        depts_str = None
        dept_id = data['form']['dept_relation2'] or dept_obj.find(self.cr, self.uid)
        depts_ids = dept_obj.search(self.cr, self.uid, [('id','in',dept_id)])
        depts_str = ', '.join([dept.name for dept in dept_obj.browse(self.cr, self.uid, depts_ids)])
        if depts_str:
            return '%s' % depts_str
        else:
            return ''    
    
    def get_total(self, as_of, fy, budget_item_id, type, dept=False, context=None):
        #print as_of, fy, budget_item_id
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        #===========
        cr.execute("SELECT id FROM account_period WHERE to_char(date_stop,'yyyy-mm') <= %s AND fiscalyear_id = %s ",(str(as_of),str(fy),))
        period_ids = map(lambda x: x[0], cr.fetchall())
        minimum = min(period_ids)
        #-----------
        cr.execute("SELECT id FROM account_period WHERE fiscalyear_id = %s AND id not in %s ",(str(fy),tuple(period_ids),))
        period_budget_ids = map(lambda x: x[0], cr.fetchall())
        #+++++++++++
        date_start = db_pool.get('account.period').browse(cr, uid, minimum).date_start
        analytic = False
        total_view = balance = 0.0
        result = 0.0
        if type == 'view':
            budget_ids = budget_pool._get_children_and_consol(cr, uid, budget_item_id, context)
            budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
            for budget in budgets:
                if dept:
                    line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                    line_budget_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_budget_ids),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                else:
                    line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id)])
                    line_budget_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_budget_ids),('budget_item_id','=',budget.id)])
                if line_ids or line_budget_ids:
                    for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                        analytic = line.analytic_account_id.id
                    for line_budget in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_budget_ids,):
                        balance += line_budget.balance
                    if analytic:
                        cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                                   "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic, date_start, as_of,))
                        result = cr.fetchone()[0]
                        if result is None:
                            result = 0.0
                        total_view += result
            #print "balanceview",balance
            return abs(total_view)+balance
        else:
            if dept:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_ids),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
                line_budget_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_budget_ids),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
            else:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_ids),('budget_item_id','=',budget_item_id)])
                line_budget_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_budget_ids),('budget_item_id','=',budget_item_id)])
            for line in db_pool.get('ad_budget.line').browse(cr, uid, line_ids, context=context):
                analytic = line.analytic_account_id.id
            for line_budget in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_budget_ids,):
                balance += line_budget.balance
            if analytic:
                cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                       "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic, date_start, as_of,))
                result = cr.fetchone()[0]
                if result is None:
                    result = 0.0
            #print "balancenormal",balance
        return abs(result)+balance
    
    def get_total_BudgetD(self, as_of, fy, budget_item_id, type, dept=False, context=None):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        cr.execute("SELECT id FROM account_period WHERE fiscalyear_id = %s ",(str(fy),))
        period_ids = map(lambda x: x[0], cr.fetchall())
        #print "ssss",period_ids
        minimum = min(period_ids)
        date_start = db_pool.get('account.period').browse(cr, uid, minimum).date_start
        analytic = False
        total_view = 0.0
        result = 0.0
        budget_ids = budget_pool._get_children_and_consol(cr, uid, budget_item_id, context)
        budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
        for budget in budgets:
            if dept:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
            else:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id)])
            if line_ids:
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                    total_view += line.amount
        return abs(total_view)
    
    def get_total_row_Total(self, as_of, fy, budget_item_id, type, dept=False, context=None):
        #print "+++++",as_of, fy, budget_item_id, type, dept
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        #actual
        cr.execute("SELECT id FROM account_period WHERE to_char(date_stop,'yyyy-mm') <= %s AND fiscalyear_id = %s ",(str(as_of),str(fy),))
        period_ids = map(lambda x: x[0], cr.fetchall())
        minimum = min(period_ids)
        date_start = db_pool.get('account.period').browse(cr, uid, minimum).date_start
        #budget
        cr.execute("SELECT id FROM account_period WHERE fiscalyear_id = %s AND id not in %s ",(str(fy),tuple(period_ids),))
        period_budget_ids = map(lambda x: x[0], cr.fetchall())
        #print "=====",period_budget_ids
        #minimum = min(period_ids)
        
        analytic = False
        total_budget = total_view = 0.0
        result = 0.0
        budget_ids = budget_pool._get_children_and_consol(cr, uid, budget_item_id, context)
        budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
        for budget in budgets:
            if dept:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                line_budget_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_budget_ids),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
            else:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id)])
                line_budget_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_budget_ids),('budget_item_id','=',budget.id)])
            #print "ssss",line_budget_ids
            if line_ids or line_budget_ids:
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                    analytic = line.analytic_account_id.id
                    #analytic_budget = line.analytic_account_id.id
                #print analytic,analytic_budget
                for line_budget in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_budget_ids,):
                    total_budget += line_budget.balance
                if analytic:
                    cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                               "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic, date_start, as_of,))
                    result = cr.fetchone()[0]
                    if result is None:
                        result = 0.0
                    total_view += result
        return abs(total_view)+total_budget

    def get_total_row_Budget(self, as_of, fy, budget_item_id, type, dept=False, context=None):
        #print "+++++",as_of, fy, budget_item_id, type, dept
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        cr.execute("SELECT id FROM account_period WHERE fiscalyear_id = %s ",(str(fy),))
        period_ids = map(lambda x: x[0], cr.fetchall())
        #print "ssss",period_ids
        minimum = min(period_ids)
        date_start = db_pool.get('account.period').browse(cr, uid, minimum).date_start
        analytic = False
        total_view = 0.0
        result = 0.0
        budget_ids = budget_pool._get_children_and_consol(cr, uid, budget_item_id, context)
        budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
        for budget in budgets:
            if dept:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
            else:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','in',period_ids),('budget_item_id','=',budget.id)])
            if line_ids:
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                    total_view += line.amount
        return abs(total_view)
    
    def get_total_row_expense(self, period, as_of, fy, budget_item_id, type, dept=False, context=None):
        #print "get_total_row_expense",period, as_of, fy, budget_item_id, type, dept
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        cr.execute("SELECT id FROM account_period WHERE to_char(date_stop,'yyyy-mm') <= %s AND fiscalyear_id = %s ",(str(as_of),str(fy),))
        period_ids = map(lambda x: x[0], cr.fetchall())
        minimum = min(period_ids)
        date_start = db_pool.get('account.period').browse(cr, uid, minimum).date_start
        analytic = False
        total_view = 0.0
        result = 0.0
        a = 0.0
#       print period_ids,minimum,date_start
        budget_ids = budget_pool._get_children_and_consol(cr, uid, budget_item_id, context)
        budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
        for budget in budgets:
            if dept:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','=',period),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
            else:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','=',period),('budget_item_id','=',budget.id)])
            #line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','=',period),('budget_item_id','=',budget.id)])
            if line_ids:
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids):
                    analytic = line.analytic_account_id.id
                    date_from = line.period_id.date_start
                    date_to = line.period_id.date_stop
                    if analytic:
                        cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                                   "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))  AND date <= %s ", (analytic, date_from, date_to, as_of,))
                        result = cr.fetchone()[0]
                        #print analytic,date_from,date_to,result
                        if result is None:
                            if line.period_id.id in period_ids:
                                total_view += 0.0
                            else:
                                total_view += line.amount 
                        else:
                            total_view += result 
        return abs(total_view)
    
    def get_total_row_cogs(self, period, as_of, fy, budget_item_id, type, dept=False, context=None):
        #print "get_total_row_cogs",period, as_of, fy, budget_item_id, type, dept
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        cr.execute("SELECT id FROM account_period WHERE to_char(date_stop,'yyyy-mm') <= %s AND fiscalyear_id = %s ",(str(as_of),str(fy),))
        period_ids = map(lambda x: x[0], cr.fetchall())
        minimum = min(period_ids)
        date_start = db_pool.get('account.period').browse(cr, uid, minimum).date_start
        analytic = False
        total_view = 0.0
        result = 0.0
        a = 0.0
#       print period_ids,minimum,date_start
        budget_ids = budget_pool._get_children_and_consol(cr, uid, budget_item_id, context)
        budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
        for budget in budgets:
            if dept:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','=',period),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
            else:
                line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','=',period),('budget_item_id','=',budget.id)])
            #line_ids = db_pool.get('ad_budget.line').search(cr, uid, [('period_id','=',period),('budget_item_id','=',budget.id)])
            if line_ids:
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids):
                    analytic = line.analytic_account_id.id
                    date_from = line.period_id.date_start
                    date_to = line.period_id.date_stop
                    if analytic:
                        cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                                   "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))  AND date <= %s ", (analytic, date_from, date_to, as_of,))
                        result = cr.fetchone()[0]
                        #print analytic,date_from,date_to,result
                        if result is None:
                            if line.period_id.id in period_ids:
                                total_view += 0.0
                            else:
                                total_view += line.amount 
                        else:
                            total_view += result 
        return abs(total_view)

    
    def get_department(self, data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['form']['id']])
        dept = obj_data[0].department_select
        return dept
    
    def get_period(self, as_of, fy, period, budget_item_id, date_start, date_end, type, item, dept=False, context=None):
        #print "+++++++++++???????????????????????????????????????//+",period, budget_item_id, date_start, date_end, type, item, dept
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        period_pool = db_pool.get('account.period')
        res = {}
#        period_ids = period_pool.search(self.cr, self.uid, [('date_start','<=',as_of),('date_stop','>=',as_of)])[0]
#        period_idx = period_pool.browse(self.cr, self.uid, period_ids)
        
        cr.execute("SELECT id FROM account_period WHERE to_char(date_stop,'yyyy-mm') <= %s AND fiscalyear_id = %s ",(str(as_of),str(fy),))
        period_id = map(lambda x: x[0], cr.fetchall())
        #print "result2",move_ids
        res[budget_item_id] = 0.0
        ########################ARYA############################
        if type == 'view':
            #print ">>>>>>>>>>Masuk<<<<<<<<<"
            budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
            budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
            total_view = 0.0
            #res[budget_item_id] = 0.0
            for budget in budgets:
                #print "ANAK VIEW ==>", budget.id
                if dept:
                    #print "******************************************************", dept
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                else:
                    #print "000000000000000000000000000000000000000000000000000000000", dept
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id)])
                if line_ids:
                    for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                        analytic_account_id = line.analytic_account_id.id
                        #date_from = str(line.period_id.date_start)
                        #date_to = str(line.period_id.date_stop)
                        date_from = line.period_id.date_start
                        date_to = line.period_id.date_stop
                        #print date_from,date_to,line.period_id
                        cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                               "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) AND date <= %s ", (analytic_account_id, date_from, date_to, as_of,))
                        result = cr.dictfetchone()
#                        if result['balance_real'] is None:
#                            result.update({'balance_real': 0.0})
#                        result.update({'balance_real':abs(result['balance_real'])})
#                        res.update({line.id:result})
                        if line.amount <> 0.00:
                            if result['balance_real']:
                                amount = float(result['balance_real'])
                            #amount = float(line.amount - line.balance_real)
                            else:
                                if period not in period_id:
                                    amount = float(line.amount)
                                else:
                                    amount = 0.00
                            #res[budget_item_id] = float(line.amount - line.balance_real)
                            res[budget_item_id] = res[budget_item_id] + amount
                        #print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww", res[budget_item_id]
            return abs(res[budget_item_id])
        ####################################################

        if dept:
            #print "******************************************************", dept
            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
        else:
            #print "000000000000000000000000000000000000000000000000000000000", periode.append(period)
            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id)])
        #line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id)])
        #print "line_ids", line_ids
        #line_id = self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids)
        total = 0.0
        #print periode
        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
            analytic_account_id = line.analytic_account_id.id
            #date_from = str(line.period_id.date_start)
            #date_to = str(line.period_id.date_stop)
            date_from = line.period_id.date_start
            date_to = line.period_id.date_stop
            #print date_from,date_to,line.period_id
            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                   "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) AND date <= %s ", (analytic_account_id, date_from, date_to, as_of,))
            result = cr.dictfetchone()
            #print "View SELECT----------------------->>", result
#            cr.execute("SELECT id FROM account_period WHERE date_stop <= '2012-08-31'")
#            result2 = cr.dictfetchall()
            #print "++", line.id, "==", line.amount, "IOW", line.balance_real
            #print "#######################################################################"
            budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
            budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
            
            for budget in budgets:
                #print "*********************************************8",result2
                if result['balance_real'] is None:
                    result.update({'balance_real': 0.0})
                result.update({'balance_real':abs(result['balance_real'])})
                #print "result",result['balance_real']
                if line.amount <> 0.00:
                    #print "period",period
                    if result['balance_real']:
                        amount = float(result['balance_real'])
                    #amount = float(line.amount - line.balance_real)
                    else:
                        if period not in period_id:
                            amount = float(line.amount)
                        else:
                            amount = 0.00
                    res[budget_item_id] = res[budget_item_id] + amount
#                if line.amount <> 0.00:
#                    res[budget_item_id] = float(line.amount - line.balance_real)
                    #print "res[budget_item_id]^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", res[budget_item_id]
                    total = total + res[budget_item_id]
                    #print "total"
                    #return total
                else:
                    #print "----------------------->>>+++ MASUK****", line.amount
                    res[budget_item_id] = 0.00
                    #return 0.0
        return total
                
    def get_transaction(self, budget_item, dept):
        #print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx...", budget_item, dept
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        analytic_line = db_pool.get('account.analytic.line')
        budget_line = db_pool.get('ad_budget.line')
        
        analytic_search = budget_line.search(cr, uid, [('budget_item_id','=',budget_item),('analytic_account_id.department_id','=',dept)])
        analytic_browse = budget_line.browse(cr, uid, analytic_search)
        if len(analytic_browse) > 0:
            for analytic in analytic_browse:
                analytic_id = analytic.analytic_account_id.id
                #print "ttttttttttttttttttttt", analytic_id
                trans_search = analytic_line.search(cr, uid, [('account_id','=',analytic_id)])
                trans_browse = analytic_line.browse(cr, uid, trans_search)
        else:
            trans_browse = []
        return trans_browse
    
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
        #print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", dept
        #field_names = [field_names]
        #print field_names
        #types = ['expense','income']
        
        ctx = self.context.copy()
#        ctx['fiscalyear'] = data['form'].get('fiscalyear_id', False)
        #print "eeeeeeeeeeee",data['form']['filter']
#        if data['form']['filter'] == 'filter_period':
#            ctx['period_from'] =  data['form'].get('period_from', False)
#            ctx['period_to'] =  data['form'].get('period_to', False)
#            #print "dddddddddd",data['form']['filter'],ctx['period_from'],ctx['period_to']
#        elif data['form']['filter'] == 'filter_date':
#            ctx['date_from'] = data['form'].get('date_from', False)
#            ctx['date_to'] =  data['form'].get('date_to', False)
            #print "dddddddddd",data['form']['filter'],ctx['date_from'],ctx['date_to']
        #print "xxxxxxx",ctx['periods']
        
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
        #print "budget_id----------->>",budget_id,data['form']['display_account_level']
        
        child_ids = budget_pool._get_children_and_consol(cr, uid, budget_id, context=ctx)
        if child_ids:
            budget_ids = child_ids
        
#        if data['form']['with_detail'] == True:
#            budgets = budget_pool.browse(cr, uid, budget_ids, context=ctx)
#        else:
#            budgets = budget_pool.browse(cr, uid, budget_id, context=ctx)
        #print "==========",budgets
        budgets = budget_pool.read(self.cr, self.uid, budget_ids, ['type','code','name','balance_budget','parent_id','level','type_budget'], context=ctx)
        budgets.sort(lambda x,y: cmp(x['code'], y['code']))
        #budgets = budget_pool.browse(cr, uid, budget_ids, context=ctx)
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
            if not data['form']['display_account_level'] or budget_level <= data['form']['display_account_level']:
                values = {
                    'name': budget['name'],
                    'id': budget['id'],
                    'balance': budget['balance_budget'],
                    'type': budget['type'], 
                    'code' : budget['code'],
                    'level' : budget['level'],
                    'type_budget': budget['type_budget'],
                    'item' : data['form']['budget_item_select'],
                    #'dept' : data['form']['department_select'],
                }
                res.append(values)
        return res


    def get_lines_another(self, data):
        return self.result.get(data['1']['id'], [])

report_sxw.report_sxw('report.budget.rolling.pdf', 'ad_budget.item', 'addons/ad_budget_rolling/report/budget_rolling.mako', parser = budget_rolling)
#report_sxw.report_sxw('report.sale.item.sold.report', 'sale.order', 'addons/ad_report_sales/report/report_item_sold_webkit.mako', parser = ReportStatus)
        