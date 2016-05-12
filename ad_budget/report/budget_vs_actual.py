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

from c2c_reporting_tools.reports.standard_report import *
from c2c_reporting_tools.flowables.simple_row_table import *
from c2c_reporting_tools.c2c_helper import *
from c2c_reporting_tools.translation import _
from reportlab.platypus import *
from ad_budget.report.helper import *

import time
import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter

import netsvc
import pooler
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _

from copy import copy
from c2c_reporting_tools.c2c_helper import *             
import decimal_precision as dp


class budget_vs_reality(StandardReport):  
    """this report compare a budget's version with its pending real values"""
    
    def get_template_title(self, cr, context):
        """ return the title of the report """
        return _("Budget Vs. Actual")
    

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

    #def _compute_budget_sum(self, cr, uid, ids, field_names, context=None):

    def _compute_budget_sum(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        
        #print "ids=",ids
        #print "context=",context
        
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
        mapping = {
            'balance_budget': "sum(amount) as balance_budget" ,
        }

        #get all the necessary accounts
        children_and_consolidated = self._get_children_and_consol(cr, uid, ids, context=context)
        #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'Children: %s'%children_and_consolidated)

        #print "-------- children_and_consolidated",children_and_consolidated
        
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
               #date2 = (datetime.today() + relativedelta(months=+1)).strftime('%Y-%m-%d')
               #date2 = (datetime.today() + relativedelta(years=-1)).strftime('%Y-%m-%d')
               fiscalyear_pool = self.pool.get('account.fiscalyear')
               fy_id = fiscalyear_pool.search(cr, uid, [('date_start','<=',date), ('date_stop','>=',date)])
               period_pool = self.pool.get('account.period')
               periods = period_pool.search(cr, uid, [('fiscalyear_id','=',fy_id),('date_stop','<=',date2)])

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
            request = ("SELECT l.budget_item_id as id, " +\
                       ', '.join(map(mapping.__getitem__, field_names)) +
                       " FROM ad_budget_line l" \
                       " WHERE l.budget_item_id IN %s " \
                            + filters +
                       " GROUP BY l.budget_item_id")
            #print "===========",request
            
            params = (tuple(children_and_consolidated),) + query_params

            query = ("SELECT l.budget_item_id as id, " +\
                       ', '.join(map(mapping.__getitem__, field_names)) +
                       " FROM ad_budget_line l" \
                       " WHERE l.budget_item_id IN %s " \
                            + filters +
                       " GROUP BY l.budget_item_id") % params

            
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
                               import sys
                               print >> sys.stderr,'sums[current.id][fn] += sums[child.id][fn]', current.id, child.id
                        else:
                            sums[current.id][fn] += currency_obj.compute(cr, uid, child.company_id.currency_id.id, current.company_id.currency_id.id, sums[child.id][fn], context=context)
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'sums: %s'%sums)
            res = {}
            null_result = dict((fn, 0.0) for fn in field_names)
            for id in ids:
                res[id] = sums.get(id, null_result)
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,'Accounts res: %s'%res)
            return res

    def _compute_real_sum(self, cr, uid, ids, field_names, arg=None, context=None,
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

        mapping = {
            'balance_real': "sum(credit) - sum(debit) as balance_real" ,
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
            return res
    
    def get_story(self):
        """ return the report story """

        story = []

        line_obj = self.pool.get('ad_budget.line')
        version_obj = self.pool.get('ad_budget.version')
        budget_item_obj = self.pool.get('ad_budget.item')
        project_obj = self.pool.get('ad_budget.report_abstraction').get_project_group_object(self.cr, self.uid, self.context)
  
        #do we split the tables by aa?
        aa_groups = []
        if (self.datas['form']['split_by_aa']):
            #group by selected AA 
            if len(self.datas['form']['analytic_accounts'][0][2]) > 0:
                aa_groups += project_obj.browse(self.cr, self.uid, self.datas['form']['analytic_accounts'][0][2], context=self.context)
            #group by each AA linked by one line
            else: 
                aa_groups += project_obj.browse(self.cr, self.uid, line_obj.get_projects(self.cr, self.uid, self.objects, self.context), context=self.context)
        else:
            aa_groups = [True] #true means no split by aa
            
        versions = version_obj.browse(self.cr, self.uid, self.datas['form']['version_ids'])
        
        for v in versions: 
            #lines = self.objects
            for aa in aa_groups:

                title = ""
                #no split by AA
                if type(aa) == bool and aa:
                    title = v.budget_id.name+": "+v.name+" ["+v.currency_id.name+"]"
                    lines = self.objects
                #group by a AA
                else:
                    title = v.budget_id.name+": "+v.name+": "+aa.name+" ["+v.currency_id.name+"]"
                    lines = line_obj.filter_by_analytic_account(self.cr, self.uid, self.objects, [aa.id], context=self.context)
            
                table = SimpleRowsTableBuilder(title)
                   
                #first column for structure
                table.add_text_column(self._('Code'), 25*mm)
                table.add_text_column(self._('Structure'), 80*mm)
                table.add_num_column(self._('Budget Amount'),'auto',2)
                table.add_num_column(self._('Budget Real'),'auto',2)
                table.add_num_column(self._('Balance'),'auto',2)
            
                items = budget_item_obj.get_sorted_list(self.cr, self.uid, v.budget_id.budget_item_id.id)
                
                for i in items:
                    #do not add invisible items
                    if i.style != 'invisible' :
                        
                        budget_sum = self._compute_budget_sum(self.cr, self.uid, [i.id], [('balance_budget')], context=self.context)
                        real_sum = self._compute_real_sum(self.cr, self.uid, [i.id], [('balance_real')], context=self.context)

                        item_cell = ItemCell(i)
                    
                        cell = BudgetNumCell(i.code, 0)
                        cell.copy_style(item_cell)
                        table.add_custom_cell(cell)
        
                        table.add_custom_cell(item_cell)

                        cell = BudgetNumCell(budget_sum[i.id]['balance_budget'], 0)
                        cell.copy_style(item_cell)
                        table.add_custom_cell(cell)
        
                        cell = BudgetNumCell(real_sum[i.id]['balance_real'], 0)
                        cell.copy_style(item_cell)
                        table.add_custom_cell(cell)

                        cell = BudgetNumCell(budget_sum[i.id]['balance_budget']-real_sum[i.id]['balance_real'], 0)
                        cell.copy_style(item_cell)
                        table.add_custom_cell(cell)

                story.append(table.get_table())         
                story.append(PageBreak())

        return story
           
budget_vs_reality('report.budget_vs_actual', "Budget Vs. Actual", 'ad_budget.line', StandardReport.A4_PORTRAIT)        
