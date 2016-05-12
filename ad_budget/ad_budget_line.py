# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) Camptocamp SA - http://www.camptocamp.com
# Author: Arnaud WÃŒst
#
#    This file is part of the ad_budget module
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from osv import fields, osv
from c2c_reporting_tools.c2c_helper import *   
from datetime import datetime 
from time import mktime
import time
import decimal_precision as dp
from dateutil.relativedelta import relativedelta
from tools.translate import _
import os


class ad_budget_line(osv.osv):
    """ camptocamp budget line. 
    A budget version line NOT linked to an analytic account """
    
    def repair_capex(self, cr, uid, ids, context=None):
        print "xxxxx"
        budget_item_obj = self.pool.get('ad_budget.item')
        line_all = self.search(cr, uid, [('analytic_account_id.code','like',' 1-2-'),('dept_relation','=',27)])
        number = 0
        for line in self.browse(cr, uid, line_all):
            #print "iiiii"
            analytic_code = line.analytic_account_id.code
            #print "analytic_code", analytic_code
            analytic_code = analytic_code [-12:]
            #print "analytic_code2", analytic_code
            budget_item_search = budget_item_obj.search(cr, uid, [('code','=',analytic_code)])
            budget_item_browse = budget_item_obj.browse(cr, uid, budget_item_search)
            
            if budget_item_browse:
                for i in budget_item_browse:
                    #print "ID :::", i.id
                    print number
                    self.write(cr, uid, line.id, {'budget_item_id':i.id})
                    number += 1
                    print "Number",number
            else:
                raise osv.except_osv(_('Warning!'), _('Wrong model or unable to find active ids'))
    
    def repair_all(self, cr, uid, ids, context=None):
        print "xxxxx"
        budget_item_obj = self.pool.get('ad_budget.item')
        line_all = self.search(cr, uid, [])
        number = 0
        for line in self.browse(cr, uid, line_all):
            #print "iiiii"
            analytic_code = line.analytic_account_id.code
            #print "analytic_code", analytic_code
            analytic_code = analytic_code [-12:]
            #print "analytic_code2", analytic_code
            budget_item_search = budget_item_obj.search(cr, uid, [('code','=',analytic_code)])
            budget_item_browse = budget_item_obj.browse(cr, uid, budget_item_search)
            
            if budget_item_browse:
                for i in budget_item_browse:
                    #print "ID :::", i.id
                    print number
                    self.write(cr, uid, line.id, {'budget_item_id':i.id})
                    number += 1
                    print "Number",number
            else:
                raise osv.except_osv(_('Warning!'), _('Wrong model or unable to find active ids'))
    
    def filter_by_period(self, cr, uid, lines, periods_ids, context={}):
        """ return a list of lines amoungs those given in parameter that 
        are linked to one of the given periods """
        result = []
        import sys
        #print >> sys.stderr, 'periods_ids' ,periods_ids 
        #print >> sys.stderr, 'lines',lines
	 
        if len(periods_ids) == 0:
            return []
        for l in lines:
	    #print >> sys.stderr, 'l= ',l
            if l.period_id.id in periods_ids: 
                result.append(l) 
                   
	    #print >> sys.stderr, 'result ',result
        return result

    
    
    def filter_by_date(self, cr, uid, lines, date_start=None,\
        date_end=None, context={}):
        """return a list of lines among those given in parameter
            \that stand between date_start and date_end """
        result = []
        
        for l in lines:
            if (date_start == None or l.period_id.date_start >= date_start)\
             and (date_end == None or l.period_id.date_stop <= date_end):
                result.append(l) 
                   
        return result
    
    
    
    def filter_by_missing_analytic_account(self, cr, uid, lines, context={}):
        """return a list of lines among those given in parameter that are ot 
        linked to a analytic account """
        result = []
        
        for l in lines:
            if not l.analytic_account_id:
                result.append(l) 
                
        return result
    
    
        
    def filter_by_items(self, cr, uid, lines, items_ids, context={}):
        """return a list of lines among those given in parameter 
        that are linked to one of the given items """
        result = []
        
        budget_items_obj = self.pool.get('ad_budget.item')        
        all_items = budget_items_obj.get_sub_items(cr, items_ids)

        for l in lines:
            if l.budget_item_id.id in all_items:
                result.append(l)
                
        return result
    
    
    
    def filter_by_analytic_account(self, cr, uid, lines,\
        analytic_accounts_ids, context={}):
        """return a list of lines among those given in parameter 
        that is linked to analytic_accounts.
        param analytic_accounts_ids should be a list of accounts'ids. """
        result = []
        
        aa_obj = self.pool.get('account.analytic.account')
        all_accounts = aa_obj.get_children_flat_list(
                                                        cr, 
                                                        uid, 
                                                        analytic_accounts_ids
                                                    )
        
        for l in lines:
            if l.analytic_account_id.id in all_accounts:
                result.append(l) 
                
        return result



    def get_analytic_accounts(self, cr, uid, lines,\
            company_id, context={}):
        """ from a bunch of lines, return all analytic accounts 
        ids linked by those lines. Use it when you need analytic 
        accounts in a financial approach. For a project approach, 
        use get_project() above this is a facility to allow this 
        module to be overridden to use projects instead of analytic
        accounts
        """
        return self.get_projects(cr, uid, lines, context)
        
        
        
    def get_projects(self, cr, uid, lines, context={}):
        """ from a bunch of lines, return all analytic accounts ids linked by
         those lines this is an alias of get_analytic_accounts() called when 
         AA are used in a project approach (contrary to a financial approach)
        this is a facility to allow this module to be overridden to use projects 
        instead of analytic accounts
        """
        result = []
        
        for l in lines:
            if l.analytic_account_id and l.analytic_account_id.id not in result:
                result.append(l.analytic_account_id.id) 
                
        return result
    
    
    def get_versions(self, cr, uid, lines, context={}):
        """  from a bunch of lines, return all budgets' 
        versions those lines belong to """
        version = []
        version_ids = []
        
        for l in lines:
            if l.budget_version_id and l.budget_version_id.id \
                not in version_ids:
                version.append(l.budget_version_id) 
                version_ids.append(l.budget_version_id.id)
                
        return version
    
    
    
    
    def get_periods (self, cr, uid, ids, context={}):
        """return periods informations used by this budget lines.  
        (the periods are selected in the budget lines)"""
        
        periods = []
        periods_ids = []
        
        lines = self.browse(cr, uid, ids, context)
        for l in lines:
            if l.period_id.id not in periods_ids:
                periods.append(l.period_id)
                periods_ids.append(l.period_id.id)
        
        
        #sort periods by dates
        def byDateStart(first, second):
            if first.date_start > second.date_start:
                return 1
            elif first.date_start < second.date_start: 
                return -1
            return 0
        periods.sort(byDateStart)                

        
        return periods
    
    
    
    def _get_budget_currency_amount(self, cr, uid, ids, name, arg, context={}):
        """ return the line's amount xchanged in the budget's currency """ 
        res = {}
        
        #We get all values from DB
        objs =self.browse(cr, uid, ids)
        for obj in objs:
            budget_currency_id = obj.budget_version_id.currency_id.id

            
            #get the budget creation date in the right format
            t=datetime.now()
            budget_ref_date = t.timetuple()
            
            if obj.budget_version_id.ref_date:
                budget_ref_date = time.strptime(
                                                obj.budget_version_id.ref_date, 
                                                "%Y-%m-%d"
                                                )
            res[obj.id] = c2c_helper.exchange_currency(
                                                        cr, 
                                                        obj.amount, 
                                                        obj.currency_id.id, 
                                                        budget_currency_id
                                                    )
        return res
    
    
    
    def _get_budget_version_currency(self, cr, uid, context):
        """ return the default currency for this line of account. 
        The default currency is the currency set for the budget 
        version if it exists """
        
        # if the budget currency is already set
        if 'currency_id' in context and context['currency_id'] != False:
            return context['currency_id']
            
        return False
 
    def _get_children_and_consol(self, cr, uid, ids, context=None):
        
        #print "_get_children_and_consol"
        #print "ids=", ids
        #this function search for all the children and all consolidated children (recursively) of the given account ids
        ids2 = self.pool.get('ad_budget.item').search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        #ids2 = budget_item_obj.search(self.cr, self.uid, [('parent_id', 'child_of', i.id)], context=self.context)
        ids3 = []
#        for rec in self.browse(cr, uid, ids2, context=context):
#            for child in rec.child_consol_ids:
#                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
        return ids2 + ids3
    
    def __compute_real_sum(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        #print 'ids',ids
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            #print "Id ::", line.amount
            analytic_account_id = line.analytic_account_id.id
            #date_from = str(line.period_id.date_start)
            #date_to = str(line.period_id.date_stop)
            date_from = line.period_id.date_start
            date_to = line.period_id.date_stop
            
            #acc_ids = line.budget_item_id.
            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line WHERE account_id=%s AND (date "
                   "between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))", (analytic_account_id, date_from, date_to,))
            result = cr.dictfetchone()
            #print "line.id",line.id
            if result['balance_real'] is None:
                result.update({'balance_real': 0.0})
            result.update({'balance_real':abs(result['balance_real'])})
            res.update({line.id:result})
        return res
    
    def virtual_budget_usage(self, cr, uid, ids, analytic_account_id, date, context=None):
        res = {}
        
        period_obj      = self.pool.get('account.period')    
        period_ids      = period_obj.search(cr, uid,[('date_start', '<=', date), ('date_stop', '>=', date)])
        periods_tmp     = period_obj.browse(cr, uid, period_ids, context=context)
        if len(periods_tmp) > 0:
            period_id = periods_tmp[0]
          
        date_from = period_id.date_start
        date_to = period_id.date_stop
        
        cr.execute("select SUM((x.product_qty * x.price_unit)-(x.product_qty * x.price_unit)*x.discount/100) as balance_virtual FROM purchase_order_line x, purchase_order y "
                    " where y.state in ('approved') and x.order_id = y.id "
                    "  and x.account_analytic_id = %s and (x.date_planned between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) ", (analytic_account_id, date_from, date_to,))
        po_result = cr.dictfetchone()
        
        cr.execute("SELECT SUM(a.product_qty*a.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y, stock_move a "
                 " WHERE x.order_id = y.id and a.purchase_line_id = x.id and a.state in ('cancel','done') and "
                 " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
                   "  where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('approved') and b.state not in ('draft')) and a.id=y.id) and "
               " x.account_analytic_id=%s AND (x.date_planned between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) ", (analytic_account_id, date_from, date_to,))
        po_tobe_inv = cr.dictfetchone()
        
        cr.execute("select SUM(cal.amount) as balance_virtual "
                    "from cash_advance ca "
                    "left join cash_advance_line cal on (cal.voucher_id=ca.id)" 
                    "left join cash_settlement cs on (ca.id =  cs.cash_advance_id)"
                    "where ca.state='posted' and cs.state!='posted' and cal.account_analytic_id = %s" 
                    "AND (ca.date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))",(analytic_account_id, date_from, date_to,))
        cash_advance = cr.dictfetchone()
        
        if po_result['balance_virtual'] is None:
            po_result.update({'balance_virtual': 0.0})
        if po_tobe_inv['balance_virtual'] is None:
            po_tobe_inv.update({'balance_virtual': 0.0})
        if cash_advance['balance_virtual'] is None:
            cash_advance.update({'balance_virtual': 0.0})
        
        total_virtual = (abs(po_result['balance_virtual']) - abs(po_tobe_inv['balance_virtual'])) + abs(cash_advance['balance_virtual']) 
        
        return total_virtual
    
    def __compute_virtual_sum(self, cr, uid, ids, field_names, arg=None, context=None, query='', query_params=()):
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            analytic_account_id = line.analytic_account_id.id
            date_from = line.period_id.date_start
            date_to = line.period_id.date_stop
            
            total_virtual = self.virtual_budget_usage(cr, uid, ids, analytic_account_id, date_from)
            result = {'balance_virtual': total_virtual}
            
            res.update({line.id:result})
        return res
    
    def __compute_virtual_sum_old(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        #print 'ids',ids
        res={}
        for line in self.browse(cr, uid, ids, context=None):
            #print "Id ::", line.amount
            analytic_account_id = line.analytic_account_id.id
            #date_from = str(line.period_id.date_start)
            #date_to = str(line.period_id.date_stop)
            date_from = line.period_id.date_start
            date_to = line.period_id.date_stop
            
            cr.execute("select SUM(x.product_qty*x.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y "
                        " where y.state in ('approved') and x.order_id = y.id "
                        "  and x.account_analytic_id = %s and (x.date_planned between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) ", (analytic_account_id, date_from, date_to,))
            result2 = cr.dictfetchone()
            #acc_ids = line.budget_item_id.
            cr.execute("SELECT SUM(a.product_qty*a.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y, stock_move a "
                     " WHERE x.order_id = y.id and a.purchase_line_id = x.id and a.state in ('cancel','done') and "
                     " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
                       "  where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('approved') and b.state in ('open','paid','cancel')) and a.id=y.id) and "
                   " x.account_analytic_id=%s AND (x.date_planned between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) ", (analytic_account_id, date_from, date_to,))
            result = cr.dictfetchone()
            #print "line.id",line.id
            if result2['balance_virtual'] is None:
                result2.update({'balance_virtual': 0.0})
            if result['balance_virtual'] is None:
                result.update({'balance_virtual': 0.0})
            result2.update({'balance_virtual':abs(result2['balance_virtual'])-abs(result['balance_virtual'])})
            res.update({line.id:result2})
        return res
    
    def __compute_real_sum2(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        """ compute the balance for the provided
        budget_item_ids
        Arguments:
        `ids`: account ids
        `field_names`: the fields to compute (a list of any of
                       'balance', 'debit' and 'credit')
        `arg`: unused fields.function stuff
        `query`: additional query filter (as a string)
        `query_params`: parameters for the provided query string
                        (__compute will handle their escaping) as a
                        tuple
        """
        import datetime
        mapping = {
            'balance_real': "(sum(credit) - sum(debit)) * -1 as balance_real" ,
        }

        #get all the necessary accounts
        children_and_consolidated = self._get_children_and_consol(cr, uid, ids, context=context)
        #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'Children: %s'%children_and_consolidated)

        #compute for each account the balance/debit/credit from the move lines
        accounts = {}
        if children_and_consolidated:
            # FIXME allow only fy and period filters
            # remove others filters from context or raise error
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'Context: %s'%context)
            #aml_query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)

            #wheres = [""]
            #if query.strip():
            #    wheres.append(query.strip())
            #if aml_query.strip():
            #    wheres.append(aml_query.strip())
            #filters = " AND ".join(wheres)
            # self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'Filters: %s'%filters)
            #filters = ' AND period_id in ( select id from account_period where fiscalyear_id = %s ) ' % context.get('fiscalyear', False) 
            if context.get('periods', False):
                periods = context.get('periods', False)
            else:
               # default if startet without form
               date = time.strftime('%Y-%m-%d')
               date2a = datetime.datetime.today() + relativedelta(months=+1)
               date2 = date2a.strftime('%Y-%m-%d')
               fiscalyear_pool = self.pool.get('account.fiscalyear')
               fy_id = fiscalyear_pool.search(cr, uid, [('date_start','<=',date), ('date_stop','>=',date)])
               period_pool = self.pool.get('account.period')
               periods = period_pool.search(cr, uid, [('fiscalyear_id','=',fy_id), ('date_stop','<=',date2)])

            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'Periods: %s'%periods)
            # FIXME - tuple must not return ',' if only one period is available - period_id in ( p,) should be period_id in ( p )
            filters = ' AND period_id in %s ' % (tuple(periods),)
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'Filters: %s'%filters)
            # IN might not work ideally in case there are too many
            # children_and_consolidated, in that case join on a
            # values() e.g.:
            # SELECT l.account_id as id FROM account_move_line l
            # INNER JOIN (VALUES (id1), (id2), (id3), ...) AS tmp (id)
            # ON l.account_id = tmp.id
            # or make _get_children_and_consol return a query and join on that
            request = ("SELECT i.id as id, " +\
                       ', '.join(map(mapping.__getitem__, field_names)) +
                       " FROM account_account_period_sum l," \
                       "      ad_budget_item i," \
                       "      ad_budget_item_account_rel r " \
                       " WHERE l.account_id = r.account_id " \
                       "   AND i.id = r.budget_item_id " \
                       "   AND i.id IN %s " \
                            + filters +
                       " GROUP BY i.id")
            params = (tuple(children_and_consolidated),) + query_params
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'Request: %s'%request)
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'Params: %s'%params)
            cr.execute(request, params)
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
            #                          'Status: %s'%cr.statusmessage)

            for res in cr.dictfetchall():
                accounts[res['id']] = res
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'Accounts: %s'%accounts)

            # consolidate accounts with direct children
            children_and_consolidated.reverse()
            brs = list(self.pool.get('ad_budget.item').browse(cr, uid, children_and_consolidated, context=context))
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'brs: %s'%brs)

            sums = {}
            currency_obj = self.pool.get('res.currency')
            while brs:
                current = brs[0]
#                can_compute = True
#                for child in current.children_ids:
#                    if child.id not in sums:
#                        can_compute = False
#                        try:
#                            brs.insert(0, brs.pop(brs.index(child)))
#                        except ValueError:
#                            brs.insert(0, child)
#                if can_compute:
                brs.pop(0)
                for fn in field_names:
                    sums.setdefault(current.id, {})[fn] = accounts.get(current.id, {}).get(fn, 0.0)
                    #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'sums: %s'%sums)
                    for child in current.children_ids:
                        if child.company_id.currency_id.id == current.company_id.currency_id.id:
                            #FIXME Data error ?
                            try:
                               sums[current.id][fn] += sums[child.id][fn]
                            except:
                               print ' sums[current.id][fn] += sums[child.id][fn]'
                        else:
                            sums[current.id][fn] += currency_obj.compute(cr, uid, child.company_id.currency_id.id, current.company_id.currency_id.id, sums[child.id][fn], context=context)
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'sums: %s'%sums)
            res = {}
            null_result = dict((fn, 0.0) for fn in field_names)
            for id in ids:
                res[id] = sums.get(id, null_result)
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'Accounts res: %s'%res)
            print "Res ::", res
            return res
    
    def _balance(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            #print "++", line.id, "==", line.amount, "IOW", line.balance_real
            if line.amount <> 0.00:
                res[line.id] = float(line.amount - line.balance_real)
            elif line.amount == 0.00:
                res[line.id] = float(line.amount - line.balance_real)
            else:
                res[line.id] = 0.00
        return res
    
    def _balance_v(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            #print "++", line.id, "==", line.amount, "IOW", line.balance_real
            if line.amount <> 0.00:
                res[line.id] = float(line.amount - line.balance_real - line.balance_virtual)
            elif line.amount == 0.00:
                res[line.id] = float(line.amount - line.balance_real - line.balance_virtual)
            else:
                res[line.id] = 0.00
        return res
        
    def _percentage(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            #print "++", line.id, "==", line.amount, "IOW", line.balance_real
            if line.amount <> 0.00:
                res[line.id] = float((line.amount - line.balance_real) / line.amount ) * 100
            elif line.amount == 0.00:
                res[line.id] = 0.00
            else:
                res[line.id] = 0.00
        return res
   
    _name = "ad_budget.line"
    _description = "Budget Lines"
    _columns = {
        'period_id' : fields.many2one('account.period', 'Period', required=True),
        'analytic_account_id' : fields.many2one(
                                                'account.analytic.account', 
                                                'Analytic Account',required=True,
                                            ), 
        #'analytic_code' : fields.related ('analytic_account_id','code',type='char', string='Analytic Code', readonly=True),
        'budget_item_id' : fields.many2one(
                                            'ad_budget.item',
                                            'Budget Item', 
                                            required=True
                                        ),
        #'budget_item_code' : fields.related ('budget_item_id','code',type='char', string='Item Code', readonly=True),
        'name' : fields.char('Description', size=200),
        'amount' : fields.float('Amount', required=True),
        'currency_id' : fields.many2one(
                                            'res.currency', 
                                            'Currency', 
                                            required=True
                                        ),
        'amount_in_budget_currency' : fields.function(
                                            _get_budget_currency_amount, 
                                            method=True, 
                                            type='float', 
                                            string='In Budget\'s Currency'
                                        ),

        'budget_version_id' : fields.many2one(
                                                'ad_budget.version', 
                                                'Budget Version', 
                                                required=True
                                            ),     
        'percentage': fields.function(_percentage, method=True, string='Balance (%)', type='float'),
        'balance_real': fields.function(__compute_real_sum, digits_compute=dp.get_precision('Account'), method=True, string='Usage Real', multi='balance_sum'),
        'balance_virtual': fields.function(__compute_virtual_sum, digits_compute=dp.get_precision('Account'), method=True, string='Usage Virtual', multi='balance_virtual_sum'),
        'balance_v': fields.function(_balance_v, digits_compute=dp.get_precision('Account'), method=True, string='Balance Virtual', type='float'),
        'balance': fields.function(_balance, digits_compute=dp.get_precision('Account'), method=True, string='Balance Real', type='float'),
        'dept_relation': fields.related('analytic_account_id', 'department_id', relation='hr.department',type='many2one', string='Department',store=True, readonly=True),
        'div_relation': fields.related('analytic_account_id', 'division_id', relation='hr.division',type='many2one', string='Division',store=True, readonly=True),
        
        #'dept_relation': fields.related('voucher_id','company_id', relation='res.company', type='many2one', string='Company', store=True, readonly=True),
    
        }

    _defaults = {
        'currency_id' : lambda self, cr, uid, context :\
            self._get_budget_version_currency(cr, uid, context)
        }

    _order = 'budget_item_id'
    
    
    def _check_item_in_budget_tree (self, cr, uid, ids):
        """ check if the line's budget item is in the budget's structure """
        
        lines = self.browse(cr, uid, ids)
        for l in lines:
                    
            #get list of budget items for this budget
            budget_item_object = self.pool.get('ad_budget.item')
            flat_items_ids = budget_item_object.get_sub_items(cr, 
                    [l.budget_version_id.budget_id.budget_item_id.id]
                )
            
            #print "l.budget_item_id.id=",l.budget_item_id.id
            #print "flat_items_ids=",flat_items_ids
            
            if l.budget_item_id.id not in flat_items_ids:
                return False
        return True
        
        
    
    def _check_period(self, cr, uid, ids):
        """ check if the line's period overlay the budget's period """
        
        lines = self.browse(cr, uid, ids)
        for l in lines:
            
            # if a line's period is entierly before \
            #the budget's period or entierly after it, \
            #the line's period does not overlay the budget's period
            if    (l.period_id.date_start < l.budget_version_id.budget_id.start_date \
            and l.period_id.date_stop < l.budget_version_id.budget_id.start_date) \
            or (l.period_id.date_start > l.budget_version_id.budget_id.end_date \
            and l.period_id.date_stop > l.budget_version_id.budget_id.end_date):
                return False
            
        return True


    def search(self, cr, user, args, offset=0, limit=None, \
        order=None, context={}, count=False):
        """search through lines that belongs to accessible versions """
        
        lines_ids =  super(ad_budget_line, self).search(
                                                            cr, 
                                                            user, 
                                                            args, 
                                                            offset, 
                                                            limit, 
                                                            order, 
                                                            context, 
                                                            count
                                                        )    

        #get versions the user can see, from versions, get periods then filter lines by those periods
        if lines_ids:
            version_obj = self.pool.get('ad_budget.version')
            versions_ids = version_obj.search(cr, user, [], context=context)
            versions = version_obj.browse(cr, user, versions_ids, context=context)
            
            periods = []
            for v in versions:
                periods = periods + version_obj.get_periods (cr, user, v, context=context)
            lines = self.browse(cr, user, lines_ids, context=context)
            #lines = self.filter_by_period(cr, user, lines, [p.id for p in periods], context)
            line_ids = []
            # FIXME - may be a data error in blau6
            if lines:
               try:
                  lines_ids = [l.id for l in lines]
               except:
                  import sys
                  print >> sys.stderr,' lines',lines
        return lines_ids
                                                                      
    
    
    
    _constraints = [
            (
                _check_period, 
                "The line's period must overlap the budget's start or end dates",
                 ['period_id']
            ),
            (
                _check_item_in_budget_tree, 
                "The line's bugdet item must belong to the budget structure\
                 defined in the budget", 
                 ['budget_item_id']
            )
            
        ]
    
    
ad_budget_line()
