from osv import osv,fields
from report import report_sxw
from tools.translate import _
import tools
import pooler
import time

class report_budgets(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_budgets, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
              'get_object'                  : self._get_object,
              'get_period_name'             : self._get_period_name,
              'get_department'              : self._get_department,
              'get_line'                    : self._get_line,
              'compute_real_sum'            : self._compute_real_sum,
              'compute_ytd_real_sum'        : self._compute_ytd_real_sum,
              'compute_lastyear_real_sum'   : self._compute_lastyear_real_sum,
              'get_budget'                  : self._get_budget,
              'compute_view'                : self._compute_view,
              'compute_view_xls'                : self._compute_view_xls,
              'get_data': self.get_data,
              'get_dept': self.get_dept,
              'get_dept_text': self.get_dept_text,
              'lastyear': self._lastyear,
              'actual_current_month': self._actual_current_month,
              'get_period_actual' : self.get_period_actual,
              'get_period_total' : self.get_period_total,
        })
        self.context = context
        
    def _get_object(self, data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['form']['id']])
        return obj_data
    
    def _get_period_name(self,selected):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(cr.dbname)
        item_pool = db_pool.get('ad_budget.item')
        item = item_pool.browse(cr,uid,selected)
        return item
    
    def _get_department(self, dept):
        return dept
    
    def _get_line(self, data, dept,selected):
        done = None
        if not done:
            done = {}
        level = 0
        cr, uid = self.cr, self.uid

        db_pool = pooler.get_pool(cr.dbname)
        item_pool = db_pool.get('ad_budget.item')
        line_pool = db_pool.get('ad_budget.line')
        item_temp=[]
        if dept:
            obj=self.pool.get(data['model']).browse(cr,uid,[data['form']['id']])
            for o in obj:
                #===================================================================
                # Awal comment
                #===================================================================
                args=[]
                if dept:
                    args.append(('dept_relation','=',dept.id))
                if o.period_id and o.period_id.id:
                    args.append(('period_id','=',o.period_id.id))
                line_ids = line_pool.search(cr,uid,args)
                line_obj = line_pool.browse(cr,uid,line_ids)
                for line in line_obj:
                    item_temp.append(line.budget_item_id.id)
                    
                for item in item_pool.browse(cr,uid,item_temp):
                    while item.level<>0:
                        item_temp.append(item.parent_id.id)
                        item=item.parent_id
                #===================================================================
                # Akhir comment
                #===================================================================
                budget_id   = data['form'].get('budget_item2', False)
                budget_ids  = item_pool._get_children_and_consol(cr, uid, selected)
                budgets     = item_pool.browse(cr, uid, budget_ids)
                
                for item in budgets:
                    if not item.parent_id:
                        budget_ids.remove(item.id)
                    if item.id not in item_temp and item.type=='normal':
                        budget_ids.remove(item.id)
                item2 = item_pool.browse(cr,uid,budget_ids)
                for item in reversed(item2):
                    if item.type=='view':
                        l=len(item.children_ids)
                        i=0
                        for child in item.children_ids:
                            i+=1
                            if child.id in item_temp:
                                break
                            else:
                                if i==l:
                                    budget_ids.remove(item.id)
                item3 = item_pool.browse(cr,uid,budget_ids)
        else:
            budget_ids  = item_pool._get_children_and_consol(cr, uid, selected)
            item3       = item_pool.browse(cr,uid,budget_ids)
        return item3
    
    def get_dept(self, data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['form']['id']])
        dept = obj_data[0].dept_relation2
        return dept
    
    def get_dept_text(self, data):
        """ Returns the text with the periods/dates used on the report. """
        if not data['form']['dept_relation2']:
            return ''
        dept_obj = self.pool.get('hr.department')
        depts_str = None
        dept_id = data['form']['dept_relation2'] or dept_obj.find(self.cr, self.uid)
        depts_ids = dept_obj.search(self.cr, self.uid, [('id','in',dept_id)])
        
        depts_str = ', '.join([dept.name for dept in dept_obj.browse(self.cr, self.uid, depts_ids)])
        if depts_str:
            return 'Department : %s ' % depts_str
        else:
            return ''
    
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
        period_ids = period_pool.search(cr, uid, [('id','=',data['form']['period_id'])])
        periods = period_pool.browse(cr, uid, period_ids)
        dept = data['form']['dept_relation2']
        
        ctx = self.context.copy()
        
        accounts = {}
        cal_list = {}
        budgets_levels = {}
        #budget_id = data['form'].get('budget_item_id', False)
        budget_id = data['form'].get('budget_item2', False)
        #print "-----",budget_id
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
            if not data['form']['display_account_level'] or budget_level <= data['form']['display_account_level']:
                budget_browse = budget_pool.browse(cr, uid, budget['id'], context=ctx)
                #print budget_browse
                values = {
                    'name': budget['name'],
                    'id': budget['id'],
                    'balance': budget['balance_budget'],
                    'type': budget['type'], 
                    'code' : budget['code'],
                    'level' : budget['level'],
                    'type_budget': budget['type_budget'],
                    'item' : data['form']['budget_item2'],
                    'budget_id': budget_browse,
                    #'dept' : data['form']['department_select'],
                }
                res.append(values)
        return res
    
    def _compute_view(self, data, dept, item, period_obj, date):
        #print "xxxxx",data, dept, item, period_obj, date
        result={}
        item_pool = self._get_line(data, dept, item.id)
        balance_last_year,act_monthly,act_ytd,rem_monthly,rem_ytd,bgt_monthly,bgt_yearly,bgt_year=0,0,0,0,0,0,0,0
        for item_obj in item_pool:
            
            balance_real=0
            if len(self._compute_lastyear_real_sum(item_obj, period_obj, dept))>0:
                balance_real=self._compute_lastyear_real_sum(item_obj, period_obj, dept)['balance_real']
            balance_last_year += balance_real
            
            act_current_month,act_current_ytd=0,0
            rem_current_month,rem_current_ytd=0,0
            if len(self._compute_real_sum(item_obj, period_obj, date, dept))>0:
                act_current_month=self._compute_real_sum(item_obj, period_obj, date, dept)['balance_real']
                rem_current_month=self._compute_real_sum(item_obj, period_obj, date, dept)['balance']
            act_monthly += act_current_month
            rem_monthly += rem_current_month
            if len(self._compute_ytd_real_sum(item_obj, period_obj, date, dept))>0:
                act_current_ytd=self._compute_ytd_real_sum(item_obj, period_obj, date, dept)['balance_real']
                rem_current_ytd=self._compute_ytd_real_sum(item_obj, period_obj, date, dept)['balance']
            act_ytd     += act_current_ytd
            rem_ytd     += rem_current_ytd
            
            monthly,yearly,year = 0,0,0
            get_bgt             = self._get_budget(item_obj, period_obj, dept)
            if len(get_bgt)>0:
                monthly = self._get_budget(item_obj, period_obj, dept)['monthly']
                yearly  = self._get_budget(item_obj, period_obj, dept)['yearly']
                year    = self._get_budget(item_obj, period_obj, dept)['year']
            bgt_monthly += monthly
            bgt_yearly  += yearly
            bgt_year    += year
            
        print "act_monthly===========================", act_monthly
        
        result['balance_last_year'] = balance_last_year
        result['act_monthly']       = act_monthly
        result['act_ytd']           = act_ytd
        result['rem_monthly']       = rem_monthly
        result['rem_ytd']           = rem_ytd
        result['bgt_monthly']       = bgt_monthly
        result['bgt_yearly']        = bgt_yearly
        result['bgt_year']          = bgt_year
        return result 

    def _compute_view_xls(self, data, dept, item, period_obj, date):
        print "xxxxx",data, dept, item, period_obj, date
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(cr.dbname)
        result={}
        item_pool = self._get_line(data, dept, item)
        #item_obj = db_pool.get('ad_budget.item')
        #print "item_pool",item_pool
        #budget_ids = self.get_data(data)#[0]['item']
        #items      = item_obj.browse(cr, uid, budget_ids)
        #print "===================",budget_ids
        period_obj = db_pool.get('account.period').browse(cr, uid, period_obj)
        balance_last_year,act_monthly,act_ytd,rem_monthly,rem_ytd,bgt_monthly,bgt_yearly,bgt_year=0,0,0,0,0,0,0,0
        for item_obj in item_pool:
            #print item_obj
            balance_real=0
            if len(self._compute_lastyear_real_sum(item_obj, period_obj, dept))>0:
                balance_real=self._compute_lastyear_real_sum(item_obj, period_obj, dept)['balance_real']
            balance_last_year += balance_real
            
            act_current_month,act_current_ytd=0,0
            rem_current_month,rem_current_ytd=0,0
            if len(self._compute_real_sum(item_obj, period_obj, date, dept))>0:
                act_current_month=self._compute_real_sum(item_obj, period_obj, date, dept)['balance_real']
                rem_current_month=self._compute_real_sum(item_obj, period_obj, date, dept)['balance']
            act_monthly += act_current_month
            rem_monthly += rem_current_month
            if len(self._compute_ytd_real_sum_xls(item_obj, period_obj, date, dept))>0:
                act_current_ytd=self._compute_ytd_real_sum_xls(item_obj, period_obj, date, dept)['balance_real']
                rem_current_ytd=self._compute_ytd_real_sum_xls(item_obj, period_obj, date, dept)['balance']
            act_ytd     += act_current_ytd
            rem_ytd     += rem_current_ytd
            
            monthly,yearly,year = 0,0,0
            get_bgt             = self._get_budget(item_obj, period_obj, dept)
            if len(get_bgt)>0:
                monthly = self._get_budget(item_obj, period_obj, dept)['monthly']
                yearly  = self._get_budget(item_obj, period_obj, dept)['yearly']
                year    = self._get_budget(item_obj, period_obj, dept)['year']
            bgt_monthly += monthly
            bgt_yearly  += yearly
            bgt_year    += year
            
        result['pre_var_month'] = result['pre_var_year'] = result['bgt_year_pre'] = 0.0
        result['balance_last_year'] = balance_last_year
        result['act_monthly']       = act_monthly
        result['act_ytd']           = act_ytd
        
        result['rem_monthly']       = rem_monthly
        result['rem_ytd']           = rem_ytd
        
        result['bgt_monthly']       = bgt_monthly
        result['bgt_yearly']        = bgt_yearly
        result['bgt_year']          = bgt_year
        
        if rem_monthly and bgt_monthly:
            result['pre_var_month']           = (rem_monthly/bgt_monthly)*100.0
        if rem_ytd and bgt_yearly:
            result['pre_var_year']           = (rem_ytd/bgt_yearly)*100.0
        if bgt_yearly and act_ytd:
            result['bgt_year_pre'] = 100*((bgt_yearly-act_ytd)/bgt_yearly)
        return result 
    
    def _lastyear(self, budget_item_id, type, period, asof, dept=False, context=None):
        #print "============",budget_item_id, type, period, int(asof[0:4])-1, dept
        last = int(asof[0:4])-1
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        period_pool = db_pool.get('account.period')
        res = {}
        cr.execute("SELECT DISTINCT fiscalyear_id FROM account_period WHERE to_char(date_start,'yyyy') = %s ",(str(last),))
        fiscal_last_id = map(lambda x: x[0], cr.fetchall())
        #dprint "======",fiscal_last_id[0]
        cr.execute("SELECT id FROM account_period WHERE fiscalyear_id = %s ",(str(fiscal_last_id[0]),))
        period_id = map(lambda x: x[0], cr.fetchall())
        #print "xxxxx",period_id
        res[budget_item_id] = 0.0
        analytic = []
        result  = {}
        if type == 'view':
            budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
            budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
            total_view = 0.0
            for budget in budgets:
                if dept:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_id),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                else:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_id),('budget_item_id','=',budget.id)])
                if line_ids:
                    for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids):
                        analytic_account_id = line.analytic_account_id.id
                        date_from = line.period_id.date_start
                        date_to = line.period_id.date_stop
                        analytic.append(analytic_account_id)
            if analytic:
                cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id in %s AND "
                       "to_char(date,'yyyy') = %s ", (tuple(analytic), str(last)))
                result = cr.dictfetchone()
                if result['balance_real'] is None:
                    result.update({'balance_real': 0.0})
                result.update({'balance_real':abs(result['balance_real'])})
                return result['balance_real']
            else:
                return 0.0
        if dept:
            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_id),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
        else:
            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_id),('budget_item_id','=',budget_item_id)])
        total = 0.0
        #print "periode",line_ids
        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
            analytic_account_id = line.analytic_account_id.id
            date_from = line.period_id.date_start
            date_to = line.period_id.date_stop
            analytic.append(analytic_account_id)
            #print date_from,date_to,line.period_id
        if analytic:
            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id in %s AND "
                   "to_char(date,'yyyy') = %s ", (tuple(analytic), str(last)))
            result = cr.dictfetchone()
            if result['balance_real'] is None:
                result.update({'balance_real': 0.0})
            result.update({'balance_real':abs(result['balance_real'])})
            total = result['balance_real']
            #total = result['balance_real']
        return total
    
    ####################ARYA###########################
    def get_period_actual(self, as_of, period, budget_item_id, type, col, dept=False, context=None):
        #print "aaaaaaaaaaa"
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        peri_pool = db_pool.get('account.period')
        periode_id = peri_pool.search(cr,uid,[('date_start','<=',as_of),('date_stop','>=',as_of)])[0]
        selected_period = peri_pool.browse(cr,uid,period)
        res = {}
        res[budget_item_id] = 0.0
        periode_obj= peri_pool.browse(cr,uid,periode_id)
        
        period_ytd = peri_pool.search(cr,uid,[('date_start','>=',periode_obj.fiscalyear_id.date_start),('date_stop','<=',periode_obj.date_stop)])
        period_fiscal = peri_pool.search(cr, uid, [('fiscalyear_id','=',periode_obj.fiscalyear_id.id)])
        #print "period_ytd",period_fiscal
        ########################ARYA############################
        if period in period_ytd:
            if type == 'view':
                print "^^^^^^^^^^^^^^^^^^^^^^^^^^^"
                budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
                budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
                #print "budgets",budgets
                total_view = 0.0
                AmtBgtMonth = 0
                line_ids_curr = []
                line_ids = []
                Amt = 0
                for budget in budgets:
                    if dept:
                        if col in ['AmtActMonth','AmtBgtMonth', 'AmtVarMonth', 'PreVarMonth']:
                            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                        elif col in ['AmtActYear','AmtBgtYear','AmtVarYear','PreVarYear']:
                            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                        elif col in ['AmtTotBudget', 'PreTotBudget']:
                            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_fiscal),('budget_item_id','=',budget.id),('analytic_account_id.department_id','=',dept)])
                    else:
                        if col in ['AmtActMonth','AmtBgtMonth', 'AmtVarMonth', 'PreVarMonth']:
                            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget.id)])
                        elif col in ['AmtActYear','AmtBgtYear','AmtVarYear','PreVarYear']:
                            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','=',budget.id)])
                            print "actyear",col,period_ytd,budget.id
                        elif col in ['AmtTotBudget', 'PreTotBudget']:
                            line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_fiscal),('budget_item_id','=',budget.id)])
                    #print "qqqqqqqqq",col,line_ids
                    if line_ids:
                        #print "BBB"
                        if period in period_ytd and col in ['AmtActYear','AmtBgtYear','AmtVarYear','AmtTotBudget','PreVarYear', 'PreTotBudget']:
                            #print "AAA"
                            line = self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context)[0]
                            #print "xxxxxxxxx",line_ids,period,period_ytd,line,col
                            if col == 'AmtActYear':
                                amount = float(line.balance_real)
                                #print "amount",amount
                                periode_obj= peri_pool.browse(cr,uid,min(period_ytd))
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
                                #res[budget_item_id] = abs(res[budget_item_id]) 
                                #print ".........",res[budget_item_id]
                            elif col == 'AmtBgtYear':
                                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                                    res[budget_item_id] += line.amount
                            elif col == 'AmtVarYear':
                                amount = float(line.balance_real)
                                periode_obj= peri_pool.browse(cr,uid,min(period_ytd))
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
                                AmtActYear = res[budget_item_id] + amount
                                AmtBgtYear = 0
                                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                                    AmtBgtYear += line.amount
                                res[budget_item_id] = (AmtActYear - AmtBgtYear) or 0.0
                                
                            elif col == 'AmtTotBudget':
                                amount = float(line.balance_real)
                                periode_obj_start= peri_pool.browse(cr,uid,min(period_fiscal))
                                periode_obj_end= peri_pool.browse(cr,uid,max(period_fiscal))
                                analytic_account_id = line.analytic_account_id.id
                                date_from   = periode_obj_start.date_start
                                date_to     = as_of
                                ###########Diganti BUdget Total 1 Tahun###############
                                #date_to     = periode_obj_end.date_stop
                                
                                #print "date_from", date_from, "date_to", date_to
                                
                                cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                                       "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
                                result = cr.dictfetchone()
                                if result['balance_real'] is None:
                                    amount = result['balance_real'] = 0.0
                                else:
                                    amount = abs(result['balance_real'])
                                #AmtActYear = res[budget_item_id] + amount
                                ###############Diganti FUll BUdget Total################
                                AmtActYear = res[budget_item_id]
                                AmtBgtYear = 0
                                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                                    print "line.amount>>>>>>>>>>>>>>>>>>>>>>>>>>", line.amount
                                    AmtBgtYear += line.amount
                                #print "xxxxxxxxxxxxxx",AmtActYear,AmtBgtYear
                                res[budget_item_id] = (AmtActYear - AmtBgtYear) or 0.0
                            elif col == 'PreVarYear':
                                for l in line_ids:
                                    line_ids_curr.append(l)
                                Amt = 0
                                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids_curr, context=context):
                                    Amt += line.amount
                                amount = float(line.balance_real)
                                periode_obj= peri_pool.browse(cr,uid,min(period_ytd))
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
                            elif col == 'PreTotBudget':
                                for l in line_ids:
                                    line_ids_curr.append(l)
                                Amt = 0
                                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids_curr, context=context):
                                    Amt += line.amount
                                amount = float(line.balance_real)
                                periode_obj_start= peri_pool.browse(cr,uid,min(period_fiscal))
                                periode_obj_end= peri_pool.browse(cr,uid,max(period_fiscal))
                                analytic_account_id = line.analytic_account_id.id
                                date_from   = periode_obj_start.date_start
                                #date_to     = periode_obj_end.date_stop
                                date_to     = as_of
                                cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                                       "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
                                result = cr.dictfetchone()
                                if result['balance_real'] is None:
                                    amount = result['balance_real'] = 0.0
                                else:
                                    amount = abs(result['balance_real'])
                                AmtActYear = res[budget_item_id] + amount
                                AmtBgtYear = 0
                                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                                    AmtBgtYear += line.amount
                                res[budget_item_id] = (AmtActYear - AmtBgtYear) or 0.0
                                #print "res[budget_item_id]",res[budget_item_id],AmtActYear,AmtBgtYear
                                
                        elif col in ['AmtActMonth','AmtBgtMonth', 'AmtVarMonth', 'PreVarMonth']:
                            for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids):   
                                ######################Ubah########################
                                #if line.amount <> 0.00 and col == 'AmtActMonth': 
                                ###################################################         
                                #if line.amount <> 0.00 or line.amount==0.0 and col == 'AmtActMonth': 
                                if (line.amount <> 0.00 or line.amount == 0.00) and col == 'AmtActMonth':
                                    amount = float(line.balance)               
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
                                    #return abs(res[budget_item_id])
                                    #print "aaaaaaaaaaaaaaaaaaaaaaaaaaaa",amount,res[budget_item_id]
                                elif col == 'AmtBgtMonth':
                                    res[budget_item_id] += line.amount
                                elif col == 'AmtVarMonth':
                                    amount = float(line.balance)               
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
                                    AmtBgtMonth += line.amount
                                elif col == 'PreVarMonth':
                                    amount = float(line.balance)               
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
                                    AmtBgtMonth += line.amount
                                    
                if col == 'PreVarMonth':
                    if AmtBgtMonth != 0:
                        return (abs(AmtBgtMonth-res[budget_item_id])/AmtBgtMonth)*100.0
                elif col == 'PreVarYear':
                    if Amt != 0:
                        return abs((Amt-res[budget_item_id])/Amt)*100.0
                elif col == 'PreTotBudget':
                    #print "PreTotBudget 1"
                    if Amt != 0:
                        return abs(res[budget_item_id]/Amt)*100.0
                elif col in ['AmtActYear','AmtActMonth','AmtBgtMonth','AmtBgtYear']:
                    return abs(AmtBgtMonth-res[budget_item_id])
                else:
                    #print "col",col,res[budget_item_id]
                    #return abs(AmtBgtMonth-res[budget_item_id])
                    #########################Buang Absolute untuk memunculkan kurung#########################
                    return AmtBgtMonth-res[budget_item_id]
            #################Type Normal###################
            if dept:
                if col in ['AmtActMonth','AmtBgtMonth', 'AmtVarMonth','PreVarMonth']:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
                elif col in ['AmtActYear','AmtBgtYear','AmtVarYear','PreVarYear']:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
                elif col in ['AmtTotBudget', 'PreTotBudget']:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_fiscal),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',dept)])
            else:
                if col in ['AmtActMonth','AmtBgtMonth', 'AmtVarMonth','PreVarMonth']:
                    print "period",period
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','=',budget_item_id)])
                    print "line_ids",line_ids
                elif col in ['AmtActYear','AmtBgtYear','AmtVarYear','PreVarYear']:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','=',budget_item_id)])
                elif col in ['AmtTotBudget', 'PreTotBudget']:
                    line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_fiscal),('budget_item_id','=',budget_item_id)])
            total = 0.0
            #print dept,line_ids
            if line_ids:
                #print "OOOOOOOOOOOOO"
                if period in period_ytd and col in ['AmtActYear','AmtBgtYear','AmtVarYear','AmtTotBudget','PreVarYear', 'PreTotBudget']:
                    if col == 'AmtActYear':
                        periode_obj= peri_pool.browse(cr,uid,min(period_ytd))
                        analytic = []
                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids,):
                            analytic.append(line.analytic_account_id.id)
                        date_from   = periode_obj.date_start
                        date_to     = as_of
                        cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id in %s AND (date "
                               "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (tuple(analytic), date_from, date_to,))
                        result = cr.dictfetchone()
                        #print analytic,result
                        if result['balance_real'] is None:
                            total = result['balance_real'] = 0.0
                        else:
                            total = abs(result['balance_real'])
                    elif col == 'AmtBgtYear':
                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                            total += line.amount
                    elif col in ['AmtVarYear','PreVarYear']:
                        periode_obj= peri_pool.browse(cr,uid,min(period_ytd))
                        analytic = []
                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                            analytic.append(line.analytic_account_id.id)
                        date_from   = periode_obj.date_start
                        date_to     = as_of
                        cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id in %s AND (date "
                               "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (tuple(analytic), date_from, date_to,))
                        result = cr.dictfetchone()
                        if result['balance_real'] is None:
                            AmtActYear = result['balance_real'] = 0.0
                        else:
                            AmtActYear = abs(result['balance_real'])
                        AmtBgtYear = 0    
                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                            AmtBgtYear += line.amount
                        if col == 'AmtVarYear':
                            total = (AmtBgtYear - AmtActYear) or 0.0
                        else:
                            if AmtBgtYear != 0:
                                total = ((AmtBgtYear - AmtActYear)/AmtBgtYear)*100.0
                        #print "AmtBgtYear - AmtActYear",AmtBgtYear,AmtActYear
                    elif col in ['AmtTotBudget','PreTotBudget']:
                        analytic = []
                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                            analytic.append(line.analytic_account_id.id)
                        periode_obj_start= peri_pool.browse(cr,uid,min(period_fiscal))
                        periode_obj_end= peri_pool.browse(cr,uid,max(period_fiscal))
                        date_from   = periode_obj_start.date_start
                        date_to     = as_of
                        print ".............",date_from,date_to
                        cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id in %s AND (date "
                               "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (tuple(analytic), date_from, date_to,))
                        result = cr.dictfetchone()
                        
                        if result['balance_real'] is None:
                            AmtActYear = result['balance_real'] = 0.0
                        else:
                            AmtActYear = abs(result['balance_real'])
                        AmtBgtYear = 0    
                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                            AmtBgtYear += line.amount
                        #print "mmmmmmmmmmmm",AmtActYear,AmtBgtYear
                        if col == 'AmtTotBudget':
                            ##################Remain Budget#######################
                            #total = (AmtBgtYear - AmtActYear) or 0.0
                            ##################Total Budget#######################
                            total = AmtBgtYear or 0.0
                        else:
                            if AmtBgtYear != 0:
                                total = ((AmtBgtYear - AmtActYear)/AmtBgtYear)*100.0
#                    elif col == 'PreVarYear':
#                        budget = 0
#                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
#                            budget += line.amount
#                        line = self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context)[0]
#                        periode_obj_start= peri_pool.browse(cr,uid,min(period_fiscal))
#                        periode_obj_end= peri_pool.browse(cr,uid,max(period_fiscal))
#                        analytic_account_id = line.analytic_account_id.id
#                        date_from   = periode_obj_start.date_start
#                        date_to     = periode_obj_end.date_stop
#                        #print ".............",date_from,date_to,analytic_account_id
#                        cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
#                               "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
#                        result = cr.dictfetchone()
#                        if result['balance_real'] is None:
#                            AmtActYear = result['balance_real'] = 0.0
#                        else:
#                            AmtActYear = abs(result['balance_real'])
#                        AmtBgtYear = 0    
#                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
#                            AmtBgtYear += line.amount
#                        var = (AmtBgtYear - AmtActYear) or 0.0
#                        total = (var/budget)*100.0
#                    elif col == 'PreTotBudget':
#                        line = self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context)[0]
#                        periode_obj_start= peri_pool.browse(cr,uid,min(period_fiscal))
#                        periode_obj_end= peri_pool.browse(cr,uid,max(period_fiscal))
#                        analytic_account_id = line.analytic_account_id.id
#                        date_from   = periode_obj_start.date_start
#                        date_to     = periode_obj_end.date_stop
#                        #print ".............",date_from,date_to,analytic_account_id
#                        cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
#                               "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
#                        result = cr.dictfetchone()
#                        if result['balance_real'] is None:
#                            AmtActYear = result['balance_real'] = 0.0
#                        else:
#                            AmtActYear = abs(result['balance_real'])
#                        AmtBgtYear = 0    
#                        for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
#                            AmtBgtYear += line.amount
#                        total = (abs(AmtBgtYear - AmtActYear)/AmtBgtYear)*100.0 or 0.0
                        
                elif period in period_ytd and col in ['AmtActMonth','AmtBgtMonth', 'AmtVarMonth','PreVarMonth']:
                    #print "xxxxxxxxxxxxx",period,period_ytd,line_ids
                    AmtBgtMonth = 0
                    for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
#                        budget_ids = budget_pool._get_children_and_consol(self.cr, self.uid, budget_item_id, context)
#                        budgets = budget_pool.browse(cr, uid, budget_ids, context=context)
#                        for budget in budgets:
                        if col == 'AmtActMonth':
                            ###################diubah########################
                            if line.amount <> 0.00 or line.amount == 0.0:
                            ################################################
                                amount = float(line.balance_real)
                                #print "sssssssssssss",period_ytd,line.period_id.id, period
                                if line.period_id.id == period:
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
                                total = res[budget_item_id]
                            else:
                                total = 0.00
                            #print ">>>>>>>>>>>>",total,res[budget_item_id],amount
                        elif col == 'AmtBgtMonth':
                            total += line.amount
                        elif col == 'AmtVarMonth':
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
                                AmtActMonth = total + res[budget_item_id]
                            else:
                                AmtActMonth = 0.00
                            AmtBgtMonth += line.amount
                            #total = AmtActMonth#(AmtBgtMonth - AmtActMonth) or 0.0
                        elif col == 'PreVarMonth':
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
                                AmtActMonth = total + res[budget_item_id]
                            else:
                                AmtActMonth = 0.00
                            AmtBgtMonth += line.amount
                            #AmtVarMonth = (AmtBgtMonth - AmtActMonth) or 0.0
                            #print "AmtVarMonth/AmtBgtMonth",AmtVarMonth,AmtBgtMonth
                            #total = (AmtVarMonth/AmtBgtMonth)*100.0
                    if col == 'AmtVarMonth':
                        total = (AmtBgtMonth - AmtActMonth) or 0.0
                        print "total#######", total
                    elif col == 'PreVarMonth':
                        if AmtBgtMonth != 0.0:
                            total = ((AmtBgtMonth - AmtActMonth)/AmtBgtMonth)*100.0
                            print "total$$$$$", total
                else:
                    total=0.0
        #print "total123", total
        return total
    ###############################################
    
    def get_period_total(self, as_of, period, budget_ids, type, col, dept=False, context=None):
        #print "budget_item_id",budget_ids
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        peri_pool = db_pool.get('account.period')
        periode_id = peri_pool.search(cr,uid,[('date_start','<=',as_of),('date_stop','>=',as_of)])[0]
        selected_period = peri_pool.browse(cr,uid,period)
        res = {}
        
        periode_obj= peri_pool.browse(cr, uid, periode_id)
        
        period_ytd = peri_pool.search(cr,uid,[('date_start','>=',periode_obj.fiscalyear_id.date_start),('date_stop','<=',periode_obj.date_stop)])
        period_fiscal = peri_pool.search(cr, uid, [('fiscalyear_id','=',periode_obj.fiscalyear_id.id)])
        
        if dept:
            if col in ['AmtActMonthTot','AmtBgtMonthTot','AmtVarMonthTot','PreVarMonthTot']:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','in',budget_ids),('analytic_account_id.department_id','=',dept)])
            elif col in ['AmtBgtYearTot','AmtVarYearTot','AmtActYearTot']:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','in',budget_ids),('analytic_account_id.department_id','=',dept)])
        else:
            if col in ['AmtActMonthTot','AmtBgtMonthTot','AmtVarMonthTot','PreVarMonthTot']:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','in',budget_ids)])
            elif col in ['AmtBgtYearTot','AmtVarYearTot','AmtActYearTot']:
                line_ids = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','in',budget_ids)])
        total = 0.0
        
        if period in period_ytd:
            if col == 'AmtActMonthTot':
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                    periode_obj= peri_pool.browse(cr,uid,period)
                    analytic_account_id = line.analytic_account_id.id
                    date_from   = periode_obj.date_start
                    date_to     = as_of
                    cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                           "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
                    result = cr.dictfetchone()
                    
                    if result['balance_real'] is None:
                        total += 0.0
                    else:
                        total += abs(result['balance_real'])
            elif col == 'AmtActYearTot':
                #print "limeeeeeeeeeee",line_ids
                analytic = []
                periode_obj= peri_pool.browse(cr,uid,min(period_ytd))
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                    analytic.append(line.analytic_account_id.id)
                date_from   = periode_obj.date_start
                date_to     = as_of
                if analytic:
                    cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id in %s AND (date "
                           "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (tuple(analytic), date_from, date_to,))
                    result = cr.dictfetchone()
                    #print result,analytic, date_from, date_to
                    if result['balance_real'] is None:
                        total += 0.0
                    else:
                        total += abs(result['balance_real'])
                    #print "total",result
            elif col == 'AmtBgtMonthTot':
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                    total += line.amount
            elif col == 'AmtBgtYearTot':
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                    total += line.amount
            elif col in ['AmtVarMonthTot','PreVarMonthTot']:
                bm = am = 0
                periode_obj= peri_pool.browse(cr,uid,period)
                analytic = []
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                    analytic.append(line.analytic_account_id.id)
                date_from   = periode_obj.date_start
                date_to     = as_of
                if analytic:
                    cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id in %s AND (date "
                           "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (tuple(analytic), date_from, date_to,))
                    result = cr.dictfetchone()
                    if result['balance_real'] is None:
                        am += 0.0
                    else:
                        am += abs(result['balance_real'])
                    for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
                        bm += line.amount
                    if col == 'PreVarMonthTot':
                        if bm != 0:
                            total = ((bm-am)/bm)*100.0
                        else:
                            total = 0
                    else:
                        total = (bm - am)
                #print total
#            elif col == 'PreVarMonthTot':
#                bm = am = 0
#                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
#                    periode_obj= peri_pool.browse(cr,uid,period)
#                    analytic_account_id = line.analytic_account_id.id
#                    date_from   = periode_obj.date_start
#                    date_to     = as_of
#                    cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
#                           "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
#                    result = cr.dictfetchone()
#                    if result['balance_real'] is None:
#                        am += 0.0
#                    else:
#                        am += abs(result['balance_real'])
#                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids, context=context):
#                    bm += line.amount
#                if bm != 0:
#                    total = ((bm-am)/bm)*100.0
#                else:
#                    total = 0
#                
#            elif col == 'AmtVarYearTot':
#                yam = ybm = 0
#                if dept:
#                    line_ids_yam = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','in',budget_ids),('analytic_account_id.department_id','=',dept)])
#                    line_ids_ybm = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','in',budget_ids),('analytic_account_id.department_id','=',dept)])
#                else:
#                    line_ids_yam = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','in',budget_ids)])
#                    line_ids_ybm = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','in',budget_ids)])
#                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids_yam, context=context):
#                    ybm += line.amount
#                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids_ybm, context=context):
#                    periode_obj= peri_pool.browse(cr,uid,min(period_ytd))
#                    analytic_account_id = line.analytic_account_id.id
#                    date_from   = periode_obj.date_start
#                    date_to     = as_of
#                    cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
#                           "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
#                    result = cr.dictfetchone()
#                    if result['balance_real'] is None:
#                        yam += 0.0
#                    else:
#                        yam += abs(result['balance_real'])
#                total = (ybm - yam)
                
            elif col in ['AmtVarYearTot','PreVarYearTot']:
                yam = ybm = 0
                #print period
                if dept:
                    line_ids_yam = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','in',budget_ids),('analytic_account_id.department_id','=',dept)])
                    line_ids_ybm = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','in',budget_ids),('analytic_account_id.department_id','=',dept)])
                else:
                    line_ids_yam = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','in',budget_ids)])
                    line_ids_ybm = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','=',period),('budget_item_id','in',budget_ids)])
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids_yam, context=context):
                    ybm += line.amount
                analytic = []
                periode_obj= peri_pool.browse(cr,uid,min(period_ytd))
                #print "line_ids_ybm",line_ids_ybm
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids_yam, context=context):
                    analytic.append(line.analytic_account_id.id)
                date_from   = periode_obj.date_start
                date_to     = as_of
                if analytic:
                    cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id in %s AND (date "
                           "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (tuple(analytic), date_from, date_to,))
                    result = cr.dictfetchone()
                    if result['balance_real'] is None:
                        yam += 0.0
                    else:
                        yam += abs(result['balance_real'])
                    #print yam,ybm
                    if col == 'AmtVarYearTot':
                        total = (ybm - yam)
                    else:
                        if ybm != 0:
                            total = ((ybm - yam)/ybm)*100.0
                        else:
                            total = 0
            
            elif col in ['AmtTotBudgetTot']:
                yam = ybm = 0
                if dept:
                    line_ids_yam = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','in',budget_ids),('analytic_account_id.department_id','=',dept)])
                    line_ids_ybm = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_fiscal),('budget_item_id','in',budget_ids),('analytic_account_id.department_id','=',dept)])
                else:
                    line_ids_yam = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','in',budget_ids)])
                    line_ids_ybm = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_fiscal),('budget_item_id','in',budget_ids)])
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids_ybm, context=context):
                    ybm += line.amount
                analytic = []
                periode_obj= peri_pool.browse(cr,uid,min(period_ytd))
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids_yam, context=context):
                    analytic.append(line.analytic_account_id.id)
                date_from   = periode_obj.date_start
                date_to     = as_of
                if analytic:
                    cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id in %s AND (date "
                           "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (tuple(analytic), date_from, date_to,))
                    result = cr.dictfetchone()
                    if result['balance_real'] is None:
                        yam += 0.0
                    else:
                        yam += abs(result['balance_real'])
                    if col == 'AmtTotBudgetTot':
                        total = (ybm - yam)
                        total = ybm
                    else:
                        if ybm != 0:
                            total = ((ybm - yam)/ybm)*100.0
                        else:
                            total = 0
                else:
                    total = 0
            
            elif col in ['PreTotBudgetTot']:
                yam = ybm = 0
                if dept:
                    line_ids_yam = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','in',budget_ids),('analytic_account_id.department_id','=',dept)])
                    line_ids_ybm = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_fiscal),('budget_item_id','in',budget_ids),('analytic_account_id.department_id','=',dept)])
                else:
                    line_ids_yam = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_ytd),('budget_item_id','in',budget_ids)])
                    line_ids_ybm = self.pool.get('ad_budget.line').search(self.cr, self.uid, [('period_id','in',period_fiscal),('budget_item_id','in',budget_ids)])
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids_ybm, context=context):
                    ybm += line.amount
                analytic = []
                periode_obj= peri_pool.browse(cr,uid,min(period_ytd))
                for line in self.pool.get('ad_budget.line').browse(self.cr, self.uid, line_ids_yam, context=context):
                    analytic.append(line.analytic_account_id.id)
                date_from   = periode_obj.date_start
                date_to     = as_of
                if analytic:
                    cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id in %s AND (date "
                           "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (tuple(analytic), date_from, date_to,))
                    result = cr.dictfetchone()
                    if result['balance_real'] is None:
                        yam += 0.0
                    else:
                        yam += abs(result['balance_real'])
                    if col == 'AmtTotBudgetTot':
                        total = (ybm - yam)
                    else:
                        if ybm != 0:
                            total = ((ybm - yam)/ybm)*100.0
                        else:
                            total = 0
                else:
                    total = 0
        print "total", total
        return total
    
    def _actual_current_month(self, budget_item_id, type, period, asof, dept=False, context=None):
        #print "============",budget_item_id, type, period, int(asof[0:4])-1, dept
        current = asof[0:4]
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(cr.dbname)
        budget_pool = db_pool.get('ad_budget.item')
        period_pool = db_pool.get('account.period')
        res = {}
        cr.execute("SELECT DISTINCT fiscalyear_id FROM account_period WHERE to_char(date_stop,'yyyy') = %s ",(str(current),))
        fiscal_last_id = map(lambda x: x[0], cr.fetchall())
        #print "======",fiscal_last_id
        cr.execute("SELECT id FROM account_period WHERE to_char(date_stop,'yyyy-mm') <= %s AND fiscalyear_id in %s ",(str(asof),tuple(fiscal_last_id),))
        period_id = map(lambda x: x[0], cr.fetchall())
        #print period_id
        return 
    
    def _compute_lastyear_real_sum(self, item_obj, period_obj, dept):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(cr.dbname)
        item_pool = db_pool.get('ad_budget.item')
        line_pool = db_pool.get('ad_budget.line')
        fisc_pool = db_pool.get('account.fiscalyear')
        if dept:
            line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('dept_relation','=',dept.id)])
        else:
            line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id)])
        line_obj = line_pool.browse(cr,uid,line_ids)
        result  = {}
        for line in line_obj:
            analytic_account_id = line.analytic_account_id.id
            nowyear     = period_obj.fiscalyear_id.date_start.split('-')[0]
            lastyear    = str(int(nowyear)-1)
            lastfisc_id = fisc_pool.search(cr,uid,[('code','=',lastyear)])
            lastfisc_obj= fisc_pool.browse(cr,uid,lastfisc_id)
            if len(lastfisc_obj)==0:
                result['balance_real']  ='N/A'
            else:
                date_from   = lastfisc_obj[0].date_start
                date_to     = lastfisc_obj[0].date_stop
                cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                       "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
                result = cr.dictfetchone()
                if result['balance_real'] is None:
                    result.update({'balance_real': 0.0})
                result.update({'balance_real':abs(result['balance_real'])})
        return result

    def _compute_real_sum(self, item_obj, period_obj,date,dept):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(cr.dbname)
        item_pool = db_pool.get('ad_budget.item')
        line_pool = db_pool.get('ad_budget.line')
        if dept:
            line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('dept_relation','=',dept.id)])
        else:
            line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id)])
        line_obj = line_pool.browse(cr,uid,line_ids)
        result={}
        for line in line_obj:
            analytic_account_id = line.analytic_account_id.id
            date_from   = period_obj.date_start
            if date:
                date_to = date
            else:
                date_to = period_obj.date_stop
#            print date_to, date
            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                   "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
            result = cr.dictfetchone()
            if result['balance_real'] is None:
                result.update({'balance_real': 0.0})
            result.update({'balance_real':abs(result['balance_real'])})
            if line.amount<>0:
                result['balance']=float(line.amount-result['balance_real'])
            elif line.amount == 0:
                result['balance']=float(line.amount-result['balance_real'])
            else:
                result['balance']=0.0
            if int(line.amount)==0:
                print "OAK1"
                result['percent']=0
            else:
                print "Masuk"
                per = float(result['balance'])/float(line.amount)*100
                result['percent'] = "%.2f" %per
                
        return result

    def _compute_ytd_real_sum_xls(self, item_obj, period_obj, date, dept):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(cr.dbname)
        item_pool = db_pool.get('ad_budget.item')
        line_pool = db_pool.get('ad_budget.line')
        peri_pool = db_pool.get('account.period')
        if dept:
            line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('dept_relation','=',dept.id)])
        else:
            line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id)])
        line_obj = line_pool.browse(cr,uid,line_ids)

        ids_pool=[]
        periode_ids = peri_pool.search(cr,uid,[('date_start','>=',period_obj.fiscalyear_id.date_start),('date_start','<=',period_obj.date_stop)])
        result={}
        for period in peri_pool.browse(cr,uid,periode_ids):
            if dept:
                line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('period_id','=',period.id),('dept_relation','=',dept.id)])
            else:
                line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('period_id','=',period.id)])
            if len(line_ids)>0:
                ids_pool.append(line_ids[0])
            line_obj = line_pool.browse(cr,uid,ids_pool)
            amount_ytd=0
            for line in line_obj:
                amount_ytd += line.amount

        for line in line_obj:
            analytic_account_id = line.analytic_account_id.id
            date_from   = period_obj.fiscalyear_id.date_start
            
            if date:
                date_to = date
            else:
                date_to = period_obj.date_stop

            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                   "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
            result = cr.dictfetchone()
            if result['balance_real'] is None:
                result.update({'balance_real': 0.0})
            result.update({'balance_real':abs(result['balance_real'])})
            if line.amount<>0:
                result['balance']=float(amount_ytd-result['balance_real'])
            else:
                result['balance']=0.0
            if int(line.amount)==0:
                print "OAK2"
                result['percent']=0
            else:
                print result['balance'], amount_ytd
                per = result['balance']/amount_ytd*100
                result['percent'] = "%.2f" %per
        return result
    
    def _compute_ytd_real_sum(self, item_obj, period_obj, date, dept):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(cr.dbname)
        item_pool = db_pool.get('ad_budget.item')
        line_pool = db_pool.get('ad_budget.line')
        peri_pool = db_pool.get('account.period')
        if dept:
            line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('dept_relation','=',dept.id)])
        else:
            line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id)])
        line_obj = line_pool.browse(cr,uid,line_ids)

        ids_pool=[]
        periode_ids = peri_pool.search(cr,uid,[('date_start','>=',period_obj.fiscalyear_id.date_start),('date_start','<=',period_obj.date_stop)])
        result={}
        for period in peri_pool.browse(cr,uid,periode_ids):
            if dept:
                line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('period_id','=',period.id),('dept_relation','=',dept.id)])
            else:
                line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('period_id','=',period.id)])
            if len(line_ids)>0:
                ids_pool.append(line_ids[0])
            line_obj = line_pool.browse(cr,uid,ids_pool)
            amount_ytd=0
            for line in line_obj:
                amount_ytd += line.amount

        for line in line_obj:
            analytic_account_id = line.analytic_account_id.id
            date_from   = period_obj.fiscalyear_id.date_start
            
            if date:
                date_to = date
            else:
                date_to = period_obj.date_stop

            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                   "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
            result = cr.dictfetchone()
            if result['balance_real'] is None:
                result.update({'balance_real': 0.0})
            result.update({'balance_real':abs(result['balance_real'])})
            if line.amount<>0:
                result['balance']=float(amount_ytd-result['balance_real'])
            else:
                result['balance']=0.0
            if int(line.amount)==0:
                print "OAK3"
                result['percent']=0
            else:
                print "33333"
                per = result['balance']/amount_ytd*100
                result['percent'] = "%.2f" %per
        return result
    
    def _get_budget(self, item_obj,period_obj,dept):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(cr.dbname)
        line_pool = db_pool.get('ad_budget.line')
        peri_pool = db_pool.get('account.period')
        result={}
        if dept:
            line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('period_id','=',period_obj.id),('dept_relation','=',dept.id)])
        else:
            line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('period_id','=',period_obj.id)])
        line_obj = line_pool.browse(cr,uid,line_ids)
        result['monthly']=0
        for line in line_obj:
            result['monthly']=line.amount
        
        ids_pool=[]
        periode_ids = peri_pool.search(cr,uid,[('date_start','>=',period_obj.fiscalyear_id.date_start),('date_start','<=',period_obj.date_stop)])
        result['yearly']=0
        for period in peri_pool.browse(cr,uid,periode_ids):
            if dept:
                line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('period_id','=',period.id),('dept_relation','=',dept.id)])
            else:
                line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('period_id','=',period.id)])
            if len(line_ids)>0:
                ids_pool.append(line_ids[0])
            line_obj = line_pool.browse(cr,uid,ids_pool)
            result['yearly']=0
            for line in line_obj:
                result['yearly'] += line.amount

        ids_pool=[]
        periode_ids = peri_pool.search(cr,uid,[('date_start','>=',period_obj.fiscalyear_id.date_start),('date_start','<=',period_obj.fiscalyear_id.date_stop)])
        result['year']=0
        for period in peri_pool.browse(cr,uid,periode_ids):
            if dept:
                line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('period_id','=',period.id),('dept_relation','=',dept.id)])
            else:
                line_ids = line_pool.search(cr,uid,[('budget_item_id','=',item_obj.id),('period_id','=',period.id)])
            if len(line_ids)>0:
                ids_pool.append(line_ids[0])
                line_obj = line_pool.browse(cr,uid,ids_pool)
                result['year']=0
                for line in line_obj:
                    result['year'] += line.amount
    
        return result
    
    def get_account_amount(self, data, i):
        
        result = []
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        department_id   = data['form']['dept_relation2'][0]
        budget_item_id  = i['id']
        type = i['type']
        budget_item_obj = db_pool.get('ad_budget.item')
        
        print department_id, budget_item_id, type
        
        budget_line_obj = db_pool.get('ad_budget.line')
        analytic_obj    = db_pool.get('account.analytic.account')
        ########Current Period#############
        cr.execute("""select id from account_period where date_start <= %s and date_stop >= %s 
                    """, (data['form']['cut_date'],data['form']['cut_date']))
        current_period = cr.fetchone()[0]
        
        ########Period In Year#############
        cr.execute("""
                    select id from account_period where fiscalyear_id =  

                                (select fiscalyear_id from account_period where id = %s)
                                
                                order by date_start
                    """, (data['form']['period_id'],))
        period_in_year = tuple(map(lambda x: x[0], cr.fetchall()))
        
        ###########Date Current Period#########
        cr.execute("""select date_start, date_stop from account_period where id = %s """, (data['form']['period_id'],))
        period_date = cr.fetchone()
        #print "*******************", period_date[0]
        first_date_current_month = period_date[0]
        end_date_current_month  = period_date[1]
        
        ###############Year To Date Period##########
        cr.execute("""
                select id from account_period where fiscalyear_id = 
                    (select fiscalyear_id from account_period where id = %s)
                    
                 and date_start <= %s
                order by date_start
            
            """, (
                  data['form']['period_id'],
                  data['form']['cut_date']
                  ))
            
        period_ytd_id = tuple(map(lambda x: x[0], cr.fetchall()))
        
        ##########Year Date##########
        cr.execute("""
                    select date_start, date_stop from account_fiscalyear where id =  

                                (select fiscalyear_id from account_period where id = %s)
                                
                                order by date_start
                    """, (data['form']['period_id'],))
        year_date = cr.fetchone()
        first_date_year = year_date[0]
        end_date_year   = year_date[1]
        
        
        #################Analytic#################
        if type == 'view':
            budgets_item_ids = []
            budget_item_search = budget_item_obj._get_children_and_consol(cr, uid, budget_item_id, context=None)
            budgets_item_browse = budget_item_obj.browse(cr, uid, budget_item_search, context=None)
            for budgets_item in budgets_item_browse:
                budgets_item.id
                print "Type", budgets_item.type, budgets_item.name
                budgets_item_ids.append(budgets_item.id)
            budgets_item_ids = tuple(budgets_item_ids)
            print "budgets_item_ids>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", budgets_item_ids
            
            analytic_search = budget_line_obj.search(cr, uid, [('period_id','=',current_period),('budget_item_id','in',budgets_item_ids),('analytic_account_id.department_id','=',department_id)])
            analytic_browse = budget_line_obj.browse(cr, uid, analytic_search)
            
            print "analytic_browse^^^^^^^^^^^^^^^^^^^^^^^", analytic_browse
            
        else:
            analytic_search = budget_line_obj.search(cr, uid, [('period_id','=',current_period),('budget_item_id','=',budget_item_id),('analytic_account_id.department_id','=',department_id)])
            analytic_browse = budget_line_obj.browse(cr, uid, analytic_search)
        
        if analytic_browse:
            if len(analytic_browse) > 1:
                analytic_account_id = []
                for budget_line in analytic_browse:
                    #print "Analytic********************************". budget_line.analytic_account_id
                    #analytic_account_id = budget_line.analytic_account_id.id
                    analytic_account_id.append(budget_line.analytic_account_id.id)
                analytic_account_id = tuple(analytic_account_id)
                #print "111111111111111111111111111111", type(analytic_account_id)
            else:
                analytic_account_id = []
                for budget_line in analytic_browse:
                    analytic_account_id = budget_line.analytic_account_id.id
                analytic_account_id = "(" +str(analytic_account_id)+ ")"
                print "2222222222222222222222222222", analytic_account_id
            
            print "OOOOOOOOOOOOOOOOOOOOOOOOOo", analytic_account_id
        
        
            analytic_account_id         = analytic_account_id
            first_date_year             = first_date_year
            end_date_year               = end_date_year
            first_date_current_month    = first_date_current_month
            end_date_current_month      = end_date_current_month
            current_period              = current_period
            period_ytd_id               = period_ytd_id
            period_in_year              = period_in_year
            as_of_date                  = data['form']['cut_date']
            
            print "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW", analytic_account_id, first_date_year
            query ="""
                SELECT 1 as no,abs(SUM(amount)) as balance_real FROM account_analytic_line 
                            WHERE account_id in """+str(analytic_account_id)+""" and date <= '"""+first_date_year+"""'
                UNION
                SELECT 2 as no,abs(SUM(amount)) as balance_real FROM account_analytic_line 
                                        WHERE account_id in """+str(analytic_account_id)+""" and date >= '"""+first_date_current_month+"""' and date <= '"""+end_date_current_month+"""'
                UNION
                SELECT 3 as no,abs(SUM(amount)) as balance_real FROM account_analytic_line 
                                        WHERE account_id in """+str(analytic_account_id)+""" and date >= '"""+first_date_year+"""' and date <= '"""+as_of_date+"""'
                UNION
                select 4 as no, abs(SUM(amount)) as balance_real from ad_budget_line where period_id = """+str(current_period)+"""
                                            and analytic_account_id in """+str(analytic_account_id)+"""
                UNION
                select 5 as no, abs(SUM(amount)) as balance_real from ad_budget_line where period_id in """+str(period_ytd_id)+"""
                                            and analytic_account_id in """+str(analytic_account_id)+""" 
                UNION
                select 6 as no, abs(SUM(amount)) as balance_real from ad_budget_line where period_id in """+str(period_in_year)+"""
                                            and analytic_account_id in """+str(analytic_account_id)+"""                                                        
    
                                order by no """
                
            #print "QUERY>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", query
            cr.execute(query)
            
            result = cr.fetchall()
            print "******************************", result
        
        return result

report_sxw.report_sxw('report.budgets.report', 'ad_budget.line', 'ad_budget_report/report/print_budgets_report.mako', parser=report_budgets, header = False)