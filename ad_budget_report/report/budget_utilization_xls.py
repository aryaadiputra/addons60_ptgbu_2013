# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (c) 2009 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import xlwt
from report_engine_xls import report_xls
from ad_budget_report.report.report_budget_utilization import report_budgets
import cStringIO
from tools.translate import _
import pooler

class budget_utilization_xls(report_xls):
    
    def _get_start_date(self, data):
        # ok
        if data.get('form', False) and data['form'].get('date_from', False):
            return data['form']['date_from']
        return ''
    
    def _get_end_date(self, data):
        # ok
        if data.get('form', False) and data['form'].get('date_to', False):
            return data['form']['date_to']
        return ''

    def get_start_period(self, data):
        if data.get('form', False) and data['form'].get('period_from', False):
            return pooler.get_pool(self.cr.dbname).get('account.period').browse(self.cr,self.uid,data['form']['period_from']).name
        return ''

    def get_end_period(self, data):
        if data.get('form', False) and data['form'].get('period_to', False):
            return pooler.get_pool(self.cr.dbname).get('account.period').browse(self.cr, self.uid, data['form']['period_to']).name
        return ''
    
    def _get_target_move(self, data):
        if data.get('form', False) and data['form'].get('target_move', False):
            if data['form']['target_move'] == 'all':
                return _('All Entries')
            return _('All Posted Entries')
        return ''
    
    def _get_filter(self, data):
        if data.get('form', False) and data['form'].get('filter', False):
            if data['form']['filter'] == 'filter_date':
                return _('Date')
            elif data['form']['filter'] == 'filter_period':
                return _('Periods')
        return _('No Filter')
    
    def _display_filter(self, parser, data):
        filter_mode = self._get_filter(data)
        filter_string = filter_mode
        if filter_mode == 'Date':
            filter_string = '%s -> %s' % (parser.formatLang(self._get_start_date(data), date=True),
                                          parser.formatLang(self._get_end_date(data), date=True))
        elif filter_mode == 'Periods':
            filter_string = '%s -> %s' % (self.get_start_period(data),
                                 self.get_end_period(data))

        moves_string = self._get_target_move(data)
        display_acct_string = ''
        if data['form']['display_account'] == 'bal_all':
            display_acct_string = 'All'
        elif data['form']['display_account'] == 'bal_movement':
            display_acct_string = 'With movements'
        else:
            display_acct_string = 'With balance is not equal to 0'
        
        fiscal_year_str = parser.get_fiscalyear_text(data['form'])
        period_date_str = parser.get_periods_and_date_text(data['form'])

        return 'Fiscal Year: %s, Period & Date By: %s' % (fiscal_year_str, period_date_str)

    def _display_fiscalyear(self, parser, data):
        """k = parser.get_fiscalyear_text(data)
        if k:
            k = 'Fiscal Year: %s' % (k)"""
        k = "asdfasdfasdfasdf"
        return k
    
    ## Modules Begin
    def _size_col(sheet, col):
        return sheet.col_width(col)
     
    def _size_row(sheet, row):
        return sheet.row_height(row)
        ## Modules End    
    
    def _department_list(self, data):
#        if data.get('form', False) and data['form'].get('dept_relation2', False):
#            return pooler.get_pool(self.cr.dbname).get('hr.department').browse(self.cr,self.uid,data['form']['dept_relation2']).name
#        return ''
        if data.get('form', False) and data['form'].get('dept_relation2', False):
            return data['form']['dept_relation2']
        return ''

    """def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))"""
    
    def generate_xls_report(self, parser, data, obj, wb):
        
        c = parser.localcontext['company']
        ws = wb.add_sheet(('Utilization'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        ws.col(0).width = len("ABCD")*1024
        ws.col(1).width = len("ABCD")*2048
        ws.col(2).width = len("ABC")*256
        ws.col(3).width = len("ABCDEF")*1024
        ws.col(4).width = len("AB")*256
        ws.col(6).width = len("AB")*256
        ws.col(8).width = len("AB")*256
        ws.col(10).width = len("AB")*256
        ws.col(12).width = len("AB")*256
        ws.col(15).width = len("AB")*256
        ws.col(18).width = len("AB")*256
        ws.col(20).width = len("AB")*256
#        ws.col(24).width = len("AB")*256
#        ws.col(26).width = len("AB")*256
        #ws.col(3).width = len("ABC")*256
        #ws.col(4).width = len("A bunch of longer text not wrapped")*256
        ws.row(7).height = len("AB")*256
        company = "%s" % (c.name)
        #act_ytd_view = parser.compute_view_xls(data, False, i['id'], data['form']['period_id'], data['form']['cut_date'])['act_ytd']
        styles = dict(
            bold = 'font: bold 1',
            italic = 'font: italic 1',
            # Wrap text in the cell
            wrap_bold = 'font: bold 1; align: wrap 1;',
            # White text on a blue background
            reversed = 'pattern: pattern solid, fore_color blue; font: color black;',
            # Light orange checkered background
            light_orange_bg = 'pattern: pattern fine_dots, fore_color white, back_color orange;',
            # Heavy borders
            bordered = 'border: top thick, right thick, bottom thick, left thick;',
            # 16 pt red text
            big_red = 'font: height 320, color red;',
        )
        #print styles['light_orange_bg']
        cols_specs = [
                # Headers data
                ('Kosong', 1, 0, 'text',
                    lambda x, d, p: ""),
                ('Note',  1, 0, 'text',
                    lambda x, d, p: 'Note:'),
                ('Note1', 6, 0, 'text',
                    lambda x, d, p: "1. This rolling report should include P&L, cashflow & balance sheet"),
                ('Note2', 6, 0, 'text',
                    lambda x, d, p: "2. ERP should produce both detail & summary (high level, major accounts)"),
                ('Note3', 6, 0, 'text',
                    lambda x, d, p: "3. Need to add Revenue"),
                ('Space', 22, 0, 'text',
                    lambda x, d, p: ""),
                ('Company', 22, 0, 'text',
                    lambda x, d, p: company.upper()),
                ('Judul', 22, 0, 'text',
                    lambda x, d, p: "Budget Reporting"),
                ('Dept', 22, 0, 'text',
                    lambda x, d, p: parser.get_dept_text(data)),
                ('Department', 22, 0, 'text',
                    lambda x, d, p: x.name),
                ('Div', 22, 0, 'text',
                    lambda x, d, p: 'Division'),
#                ('inIDR', 23, 0, 'text',
#                    lambda x, d, p: 'in IDR'),
                ('YearEnded', 22, 0, 'text',
                    lambda x, d, p: 'for year ended %s' % (parser.formatLang(data['form']['cut_date'], date=True))),
                ('inIDR', 22, 0, 'text',
                    lambda x, d, p: "in IDR"),
                ('HeaderCOA', 2, 0, 'text',
                    lambda x, d, p: "COA"),
                ('HeaderDesc', 1, 0, 'text',
                    lambda x, d, p: ""),
                ('HAPY', 1, 0, 'text',
                    lambda x, d, p: "Actual Previous Year"),
                ('HACY', 3, 0, 'text',
                    lambda x, d, p: "Actual Current Year"),
                ('HBCY', 3, 0, 'text',
                    lambda x, d, p: "Budget Current Year"),
                ('VRC', 5, 0, 'text',
                    lambda x, d, p: "(Over)/Under"),
                ('RB', 5, 0, 'text',
                    lambda x, d, p: "Remaining Budget"),
                ('UTB', 3, 0, 'text',
                    lambda x, d, p: "vs Total Budget Dept."),#compute_view(data, dept,item,o.period_id,o.cut_date)
                ('Code', 1, 0, 'text',
                    lambda x, d, p: x['code']),
                ('Desc', 1, 0, 'text',
                    lambda x, d, p: '  '*x['level'] +x['name']),
                #LIST ALL EXPENSE
                ('AmtHAPY', 1, 0, 'number',
                    lambda x, d, p: parser._lastyear(i['id'], i['type'], data['form']['period_id'], data['form']['cut_date'], False)),                
                ('AmtActMonth', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtActMonth', False)),
                ('AmtActYear', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtActYear', False)),
                ('AmtBgtMonth', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtBgtMonth', False)),
                ('AmtBgtYear', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtBgtYear', False)),
                ('AmtVarMonth', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtVarMonth', False)),
                ('AmtVarYear', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtVarYear', False)),
                ('PreVarMonth', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'PreVarMonth', False)),
                ('PreVarYear', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'PreVarYear', False)),
                ('AmtTotBudget', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtTotBudget', False)),
                ('PreTotBudget', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'PreTotBudget', False)),
                #TOTAL ALL EXPENSE
                ('TotalDesc', 3, 0, 'text', lambda x, d, p: "TOTAL OPERATING EXPENSES"),
                ('AmtActMonthTot', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], exps, False, 'AmtActMonthTot', False)),
                ('AmtActYearTot', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], exps, False, 'AmtActYearTot', False)),
                ('AmtBgtMonthTot', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], exps, False, 'AmtBgtMonthTot', False)),
                ('AmtBgtYearTot', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], exps, False, 'AmtBgtYearTot', False)),
                ('AmtVarMonthTot', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], exps, False, 'AmtVarMonthTot', False)),
                ('PreVarMonthTot', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], exps, False, 'PreVarMonthTot', False)),
                ('AmtVarYearTot', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], exps, False, 'AmtVarYearTot', False)),
                ('PreVarYearTot', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], exps, False, 'PreVarYearTot', False)),
                ('AmtTotBudgetTot', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], exps, False, 'AmtTotBudgetTot', False)),
                ('PreTotBudgetTot', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], exps, False, 'PreTotBudgetTot', False)),
                #TOTAL ALL COGS
                ('TotalCOGSDesc', 3, 0, 'text', lambda x, d, p: "TOTAL PRODUCTION COST"),
                ('AmtActMonthTotCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogs, False, 'AmtActMonthTot', False)),
                ('AmtActYearTotCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogs, False, 'AmtActYearTot', False)),
                ('AmtBgtMonthTotCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogs, False, 'AmtBgtMonthTot', False)),
                ('AmtBgtYearTotCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogs, False, 'AmtBgtYearTot', False)),
                ('AmtVarMonthTotCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogs, False, 'AmtVarMonthTot', False)),
                ('PreVarMonthTotCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogs, False, 'PreVarMonthTot', False)),
                ('AmtVarYearTotCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogs, False, 'AmtVarYearTot', False)),
                ('PreVarYearTotCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogs, False, 'PreVarYearTot', False)),
                ('AmtTotBudgetTotCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogs, False, 'AmtTotBudgetTot', False)),
                ('PreTotBudgetTotCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogs, False, 'PreTotBudgetTot', False)),
                #LIST DEPT
                ('AmtHAPYDEP', 1, 0, 'number',
                    lambda x, d, p: parser._lastyear(i['id'], i['type'], data['form']['period_id'], data['form']['cut_date'], dep['id'])),                
                ('AmtActMonthDEP', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtActMonth', dep['id'])),
                ('AmtActYearDEP', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtActYear', dep['id'])),
                ('AmtBgtMonthDEP', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtBgtMonth', dep['id'])),
                ('AmtBgtYearDEP', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtBgtYear', dep['id'])),
                ('AmtVarMonthDEP', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtVarMonth', dep['id'])),
                ('AmtVarYearDEP', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtVarYear', dep['id'])),
                ('PreVarMonthDEP', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'PreVarMonth', dep['id'])),
                ('PreVarYearDEP', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'PreVarYear', dep['id'])),
                ('AmtTotBudgetDEP', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'AmtTotBudget', dep['id'])),
                ('PreTotBudgetDEP', 1, 0, 'number',
                    lambda x, d, p: parser.get_period_actual(data['form']['cut_date'], data['form']['period_id'], i['id'], i['type'], 'PreTotBudget', dep['id'])),
                #TOTAL DEPT EXPENSE
                ('TotalDepDesc', 3, 0, 'text', lambda x, d, p: "TOTAL OPERATING EXPENSES"),
                ('AmtActMonthTotDEP', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], expsD, False, 'AmtActMonthTot', dep['id'])),
                ('AmtActYearTotDEP', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], expsD, False, 'AmtActYearTot', dep['id'])),
                ('AmtBgtMonthTotDEP', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], expsD, False, 'AmtBgtMonthTot', dep['id'])),
                ('AmtBgtYearTotDEP', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], expsD, False, 'AmtBgtYearTot', dep['id'])),
                ('AmtVarMonthTotDEP', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], expsD, False, 'AmtVarMonthTot', dep['id'])),
                ('PreVarMonthTotDEP', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], expsD, False, 'PreVarMonthTot', dep['id'])),
                ('AmtVarYearTotDEP', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], expsD, False, 'AmtVarYearTot', dep['id'])),
                ('PreVarYearTotDEP', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], expsD, False, 'PreVarYearTot', dep['id'])),
                ('AmtTotBudgetTotDEP', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], expsD, False, 'AmtTotBudgetTot', dep['id'])),
                ('PreTotBudgetTotDEP', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], expsD, False, 'PreTotBudgetTot', dep['id'])),
                #TOTAL DEPT COGS
                ('TotalCOGSDepDesc', 3, 0, 'text', lambda x, d, p: "TOTAL PRODUCTION COST"),
                ('AmtActMonthTotDEPCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogsD, False, 'AmtActMonthTot', dep['id'])),
                ('AmtActYearTotDEPCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogsD, False, 'AmtActYearTot', dep['id'])),
                ('AmtBgtMonthTotDEPCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogsD, False, 'AmtBgtMonthTot', dep['id'])),
                ('AmtBgtYearTotDEPCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogsD, False, 'AmtBgtYearTot', dep['id'])),
                ('AmtVarMonthTotDEPCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogsD, False, 'AmtVarMonthTot', dep['id'])),
                ('PreVarMonthTotDEPCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogsD, False, 'PreVarMonthTot', dep['id'])),
                ('AmtVarYearTotDEPCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogsD, False, 'AmtVarYearTot', dep['id'])),
                ('PreVarYearTotDEPCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogsD, False, 'PreVarYearTot', dep['id'])),
                ('AmtTotBudgetTotDEPCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogsD, False, 'AmtTotBudgetTot', dep['id'])),
                ('PreTotBudgetTotDEPCOGS', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], cogsD, False, 'PreTotBudgetTot', dep['id'])),
                
                #Total DEPT CAPEX
                ('TotalCAPEXDepDesc', 3, 0, 'text', lambda x, d, p: "TOTAL CAPITAL EXPENSES"),
                ('AmtActMonthTotDEPCAPEX', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], capexD, False, 'AmtActMonthTot', dep['id'])),
                ('AmtActYearTotDEPCAPEX', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], capexD, False, 'AmtActYearTot', dep['id'])),
                ('AmtBgtMonthTotDEPCAPEX', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], capexD, False, 'AmtBgtMonthTot', dep['id'])),
                ('AmtBgtYearTotDEPCAPEX', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], capexD, False, 'AmtBgtYearTot', dep['id'])),
                ('AmtVarMonthTotDEPCAPEX', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], capexD, False, 'AmtVarMonthTot', dep['id'])),
                ('PreVarMonthTotDEPCAPEX', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], capexD, False, 'PreVarMonthTot', dep['id'])),
                ('AmtVarYearTotDEPCAPEX', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], capexD, False, 'AmtVarYearTot', dep['id'])),
                ('PreVarYearTotDEPCAPEX', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], capexD, False, 'PreVarYearTot', dep['id'])),
                ('AmtTotBudgetTotDEPCAPEX', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], capexD, False, 'AmtTotBudgetTot', dep['id'])),
                ('PreTotBudgetTotDEPCAPEX', 1, 0, 'number',
                    lambda x, d, p: '%s' % parser.get_period_total(data['form']['cut_date'], data['form']['period_id'], capexD, False, 'PreTotBudgetTot', dep['id'])),
        
                
        ]

        row_hdr0 = self.xls_row_template(cols_specs, ['Kosong','Note','Note1'])
        row_hdr1 = self.xls_row_template(cols_specs, ['Kosong','Kosong','Note2'])
        row_hdr2 = self.xls_row_template(cols_specs, ['Kosong','Kosong','Note3'])
        row_hdr3 = self.xls_row_template(cols_specs, ['Space'])
        row_hdr4 = self.xls_row_template(cols_specs, ['Company'])
        row_hdr5a = self.xls_row_template(cols_specs, ['Judul'])
        row_hdr5b = self.xls_row_template(cols_specs, ['YearEnded'])
        row_hdr5c = self.xls_row_template(cols_specs, ['Div'])
        row_hdr5d = self.xls_row_template(cols_specs, ['Dept'])
        row_hdr5e = self.xls_row_template(cols_specs, ['inIDR'])
        #row_hdr6 = self.xls_row_template(cols_specs, ['Kosong','AsOff'])
        row_hdr7 = self.xls_row_template(cols_specs, ['Space'])
        row_hdr8 = self.xls_row_template(cols_specs, ['Kosong','HeaderDesc','Kosong','HAPY','Kosong','HACY','Kosong','HBCY','Kosong','VRC','Kosong','UTB'])
#        row_hdr9 = self.xls_row_template(cols_specs, ['Kosong','StateCOA','StateDesc','StateM1','StateM2','StateM3','StateM4','StateM5','StateM6','StateM7','StateM8','StateM9','StateM10','StateM11','StateM12','Kosong','Kosong','Kosong'])
        #row_hdr9 = self.xls_row_template(cols_specs, ['Kosong','Space'])
        row_hdr10 = self.xls_row_template(cols_specs, ['Space'])
        row_hdr11 = self.xls_row_template(cols_specs, ['Department'])
#        row_loopDep = self.xls_row_template(cols_specs, ['Kosong','Code','Name','MD1','MD2','MD3','MD4','MD5','MD6','MD7','MD8','MD9','MD10','MD11','MD12','TotalD','BudgetD','VarianceD'])#row_loop_test[17][2]['PreVarYear'],row_loop_test[21][2]['PreTotBudget']
#        row_loop = self.xls_row_template(cols_specs, ['Code','Desc','Kosong','AmtHAPY','Kosong','AmtActMonth','Kosong','AmtActYear','Kosong','AmtBgtMonth','Kosong','AmtBgtYear','Kosong','AmtVarMonth','PreVarMonth','Kosong','AmtVarYear','PreVarYear','Kosong','AmtTotBudget','Kosong','PreTotBudget'])
        row_loop_test = self.xls_row_template(cols_specs, ['Code','Desc','Kosong','AmtHAPY','Kosong','AmtActMonth','Kosong','AmtActYear','Kosong','AmtBgtMonth','Kosong','AmtBgtYear','Kosong','AmtVarMonth','PreVarMonth','Kosong','AmtVarYear','PreVarYear','Kosong','AmtTotBudget','Kosong','PreTotBudget'])
        row_loop_dep = self.xls_row_template(cols_specs, ['Code','Desc','Kosong','AmtHAPYDEP','Kosong','AmtActMonthDEP','Kosong','AmtActYearDEP','Kosong','AmtBgtMonthDEP','Kosong','AmtBgtYearDEP','Kosong','AmtVarMonthDEP','PreVarMonthDEP','Kosong','AmtVarYearDEP','PreVarYearDEP','Kosong','AmtTotBudgetDEP','Kosong','PreTotBudgetDEP'])
#        row_total_cogs = self.xls_row_template(cols_specs, ['Kosong','TotalCOGSDesc','MtotCOGS1','MtotCOGS2','MtotCOGS3','MtotCOGS4','MtotCOGS5','MtotCOGS6','MtotCOGS7','MtotCOGS8','MtotCOGS9','MtotCOGS10','MtotCOGS11','MtotCOGS12','TotalCOGS','BudgetCOGS','VarianceCOGS'])
        row_total_expense = self.xls_row_template(cols_specs, ['TotalDesc','Kosong','Kosong','AmtActMonthTot','Kosong','AmtActYearTot','Kosong','AmtBgtMonthTot','Kosong','AmtBgtYearTot','Kosong','AmtVarMonthTot','PreVarMonthTot','Kosong','AmtVarYearTot','PreVarYearTot','Kosong','AmtTotBudgetTot','Kosong','PreTotBudgetTot'])
        row_total_expense_dep = self.xls_row_template(cols_specs, ['TotalDepDesc','Kosong','Kosong','AmtActMonthTotDEP','Kosong','AmtActYearTotDEP','Kosong','AmtBgtMonthTotDEP','Kosong','AmtBgtYearTotDEP','Kosong','AmtVarMonthTotDEP','PreVarMonthTotDEP','Kosong','AmtVarYearTotDEP','PreVarYearTotDEP','Kosong','AmtTotBudgetTotDEP','Kosong','PreTotBudgetTotDEP'])
#
        row_total_cogs = self.xls_row_template(cols_specs, ['TotalCOGSDesc','Kosong','Kosong','AmtActMonthTotCOGS','Kosong','AmtActYearTotCOGS','Kosong','AmtBgtMonthTotCOGS','Kosong','AmtBgtYearTotCOGS','Kosong','AmtVarMonthTotCOGS','PreVarMonthTotCOGS','Kosong','AmtVarYearTotCOGS','PreVarYearTotCOGS','Kosong','AmtTotBudgetTotCOGS','Kosong','PreTotBudgetTotCOGS'])
        row_total_cogs_dep = self.xls_row_template(cols_specs, ['TotalCOGSDepDesc','Kosong','Kosong','AmtActMonthTotDEPCOGS','Kosong','AmtActYearTotDEPCOGS','Kosong','AmtBgtMonthTotDEPCOGS','Kosong','AmtBgtYearTotDEPCOGS','Kosong','AmtVarMonthTotDEPCOGS','PreVarMonthTotDEPCOGS','Kosong','AmtVarYearTotDEPCOGS','PreVarYearTotDEPCOGS','Kosong','AmtTotBudgetTotDEPCOGS','Kosong','PreTotBudgetTotDEPCOGS'])

        row_total_capex = self.xls_row_template(cols_specs, ['TotalCAPEXDesc','Kosong','Kosong','AmtActMonthTotCAPEX','Kosong','AmtActYearTotCAPEX','Kosong','AmtBgtMonthTotCAPEX','Kosong','AmtBgtYearTotCAPEX','Kosong','AmtVarMonthTotCAPEX','PreVarMonthTotCAPEX','Kosong','AmtVarYearTotCAPEX','PreVarYearTotCAPEX','Kosong','AmtTotBudgetTotCAPEX','Kosong','PreTotBudgetTotCAPEX'])
        row_total_capex_dep = self.xls_row_template(cols_specs, ['TotalCAPEXDepDesc','Kosong','Kosong','AmtActMonthTotDEPCAPEX','Kosong','AmtActYearTotDEPCAPEX','Kosong','AmtBgtMonthTotDEPCAPEX','Kosong','AmtBgtYearTotDEPCAPEX','Kosong','AmtVarMonthTotDEPCAPEX','PreVarMonthTotDEPCAPEX','Kosong','AmtVarYearTotDEPCAPEX','PreVarYearTotDEPCAPEX','Kosong','AmtTotBudgetTotDEPCAPEX','Kosong','PreTotBudgetTotDEPCAPEX'])
#

##
#        row_total_cogsDep = self.xls_row_template(cols_specs, ['Kosong','TotalCOGSDepDesc','MtotCOGSDep1','MtotCOGSDep2','MtotCOGSDep3','MtotCOGSDep4','MtotCOGSDep5','MtotCOGSDep6','MtotCOGSDep7','MtotCOGSDep8','MtotCOGSDep9','MtotCOGSDep10','MtotCOGSDep11','MtotCOGSDep12','TotalCOGSDep','BudgetCOGSDep','VarianceCOGSDep'])
#        row_total_expenseDep = self.xls_row_template(cols_specs, ['Kosong','TotalExpenseDep','MtotEXPDep1','MtotEXPDep2','MtotEXPDep3','MtotEXPDep4','MtotEXPDep5','MtotEXPDep6','MtotEXPDep7','MtotEXPDep8','MtotEXPDep9','MtotEXPDep10','MtotEXPDep11','MtotEXPDep12','TotalEXPDep','BudgetEXPDep','VarianceEXPDep'])

        ## Style variable Begin borders: top thick, bottom solid, left double, right double;
        hdr_style = xlwt.easyxf('pattern: pattern solid, fore_color gray25;')
        row_normal_style=  xlwt.easyxf('font: height 170, colour_index black;pattern: pattern solid, fore_color white;',num_format_str='#,##0.00;(#,##0.00)')
        row_bold_style = xlwt.easyxf('font: height 180, colour_index black, bold on;pattern: pattern solid, fore_color white;',num_format_str='#,##0.00;(#,##0.00)')
        row_normal_style_pre = xlwt.easyxf('font: height 180, colour_index black;pattern: pattern solid, fore_color white;',num_format_str='#,##0.00;(#,##0.00)')
        row_bold_style_pre = xlwt.easyxf('font: height 180, colour_index black, bold on;pattern: pattern solid, fore_color white;',num_format_str='#,##0.00;(#,##0.00)')
        row_bold_style_total = xlwt.easyxf('font: height 180, colour_index black, bold on;pattern: pattern solid, fore_color white;borders: top thin, bottom medium;',num_format_str='#,##0.00;(#,##0.00)')
        style = xlwt.easyxf(styles['reversed'])
        tittle_style = xlwt.easyxf('font: height 180,name Arial, colour_index white, bold on; pattern: pattern solid, fore_color brown;')
        tittle_style2 = xlwt.easyxf('font: height 180,name Arial, colour_index white, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        tittle_bold_left_style = xlwt.easyxf('font: height 240, name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        tittle_bold_left_style2 = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;borders: bottom double;')
        tittle_left_italic_style = xlwt.easyxf('font: height 190, name Arial, colour_index black, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        tittle_bold_center_style = xlwt.easyxf('font: height 210, name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz centre; pattern: pattern solid, fore_color gray50;')
        tittle_bold_center_style3 = xlwt.easyxf('font: height 210, name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz centre; pattern: pattern solid, fore_color gray50;borders: top thin;')
        tittle_bold_center_style2 = xlwt.easyxf('font: height 200, name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz centre; pattern: pattern solid, fore_color gray50;borders: top thin;')
        tittle_bold_left = xlwt.easyxf('font: height 210, name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray50;borders: top thin;')
        tittle_bold_right = xlwt.easyxf('font: height 210, name Times New Roman, colour_index black, bold on; align: wrap on, vert centre, horiz right; pattern: pattern solid, fore_color gray50;borders: top thin;')
        #row_normal_style = xlwt.easyxf('font: height 170, name Arial, colour_index black; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        #row_bold_style = xlwt.easyxf('font: height 180, name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        subtittle_right_style = xlwt.easyxf('font: height 170, name Arial, colour_index black, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        subtittle_top_and_bottom_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        blank_style = xlwt.easyxf('font: height 650, name Arial, colour_index brown, bold off; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        normal_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off; align: wrap on, vert centre, horiz left;')
        total_style = xlwt.easyxf('font: height 240, name Arial, colour_index brown, bold on, italic on; align: wrap on, vert centre;', num_format_str='#,##0.00;(#,##0.00)')
        ## Style variable End

        # Write headers
#        ws.write(0, 0, '', tittle_style2)
#        ws.write(0, 1, '', tittle_style2)
#        ws.write(0, 2, 'Note: ', tittle_style)
#        ws.write(0, 3, '1.', tittle_style)
#        ws.write(0, 4, 'This rolling report should include P&L, cashflow & balance sheet', tittle_style)
#        for x in [5,6,7,8,9]:
#            ws.write(0, x, '', tittle_style)
#        for x in [10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
#            ws.write(0, x, '', tittle_style2)
#                
#        ws.write(1, 0, '', tittle_style2)
#        ws.write(1, 1, '', tittle_style2)
#        ws.write(1, 2, '', tittle_style)
#        ws.write(1, 3, '2.', tittle_style)
#        ws.write(1, 4, 'ERP should produce both detail & summary (high level, major accounts)', tittle_style)
#        for x in [5,6,7,8,9]:
#            ws.write(1, x, '', tittle_style)
#        for x in [10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
#            ws.write(1, x, '', tittle_style2)
#                
#        ws.write(2, 0, '', tittle_style2)
#        ws.write(2, 1, '', tittle_style2)
#        ws.write(2, 2, '', tittle_style)
#        ws.write(2, 3, '3.', tittle_style)
#        ws.write(2, 4, 'Need to add Revenue', tittle_style)
#        for x in [5,6,7,8,9]:
#            ws.write(2, x, '', tittle_style)
#        for x in [10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
#            ws.write(2, x, '', tittle_style2)
        #====================================================================    
#        self.xls_write_row(ws, None, data, parser, 3, row_hdr0, tittle_style)
#        self.xls_write_row(ws, None, data, parser, 4, row_hdr1, tittle_style)
#        self.xls_write_row(ws, None, data, parser, 5, row_hdr2, tittle_style)
#        self.xls_write_row(ws, None, data, parser, 3, row_hdr3, tittle_style2)#Space
        self.xls_write_row(ws, None, data, parser, 0, row_hdr4, tittle_bold_left_style)#Company
        self.xls_write_row(ws, None, data, parser, 1, row_hdr5a, tittle_bold_left_style)#Budget Rolling
        self.xls_write_row(ws, None, data, parser, 2, row_hdr5b, tittle_bold_left_style)#Budget Rolling
        self.xls_write_row(ws, None, data, parser, 3, row_hdr5c, tittle_bold_left_style)#Budget Rolling
        self.xls_write_row(ws, None, data, parser, 4, row_hdr5d, tittle_bold_left_style)#Budget Rolling
        self.xls_write_row(ws, None, data, parser, 5, row_hdr5e, tittle_bold_left_style)#Budget Rolling
        #self.xls_write_row(ws, None, data, parser, 6, row_hdr6, tittle_left_italic_style)#As of
        self.xls_write_row(ws, None, data, parser, 6, row_hdr7, tittle_style2)#Space
        self.xls_write_row(ws, None, data, parser, 7, row_hdr8, tittle_bold_center_style)
        ws.write(8, 0, 'ACCOUNT', tittle_bold_center_style)
        ws.write(8, 1, 'DESCRIPTION', tittle_bold_center_style)
        #ws.write(8, 2, '', tittle_bold_center_style)
        #ws.write(8, 3, '', tittle_bold_center_style)
        #ws.write(8, 4, '', tittle_bold_center_style)
        ws.write(8, 5, 'Month', tittle_bold_center_style3)
        #ws.write(8, 6, '', tittle_bold_center_style3)
        ws.write(8, 7, 'Ytd', tittle_bold_center_style3)
        #ws.write(8, 8, '', tittle_bold_center_style)
        ws.write(8, 9, 'Month', tittle_bold_center_style3)
        #ws.write(8, 10, '', tittle_bold_center_style3)
        ws.write(8, 11, 'Ytd', tittle_bold_center_style3)
        #ws.write(8, 12, '', tittle_bold_center_style)
        ws.write(8, 13, 'Monthly', tittle_bold_right)
        #ws.write(8, 14, '', tittle_bold_center_style3)
        #ws.write(8, 15, '', tittle_bold_center_style3)
        #ws.write(8, 16, '', tittle_bold_center_style3)
        ws.write(8, 17, 'Ytd', tittle_bold_left)
        #ws.write(8, 18, '', tittle_bold_center_style)
        #ws.write(8, 19, 'Monthly', tittle_bold_right)
        #ws.write(8, 20, '', tittle_bold_center_style3)
        #ws.write(8, 21, '', tittle_bold_center_style3)
        #ws.write(8, 22, '', tittle_bold_center_style3)
        #ws.write(8, 23, 'Ytd', tittle_bold_left)
        #ws.write(8, 24, '', tittle_bold_center_style)
#        ws.write(8, 19, '', tittle_bold_center_style)
        #ws.write(8, 26, '', tittle_bold_center_style3)
#        ws.write(8, 21, '', tittle_bold_center_style)
        for x in [2,3,4,8,12,18,19,20,21]:
            ws.write(8, x, '', tittle_bold_center_style)
        for x in [6,10,14,15,16]:
            ws.write(8, x, '', tittle_bold_center_style3)
        # 9
        #ws.write(9, 0, '', tittle_bold_center_style)
        #ws.write(9, 1, '', tittle_bold_center_style)
        #ws.write(9, 2, '', tittle_bold_center_style)
        ws.write(9, 3, 'Amt', tittle_bold_center_style2)
        #ws.write(9, 4, '', tittle_bold_center_style)
        ws.write(9, 5, 'Amt', tittle_bold_center_style2)
        #ws.write(9, 6, '', tittle_bold_center_style)
        ws.write(9, 7, 'Amt', tittle_bold_center_style2)
        #ws.write(9, 8, '', tittle_bold_center_style)
        ws.write(9, 9, 'Amt', tittle_bold_center_style2)
        #ws.write(9, 10, '', tittle_bold_center_style)
        ws.write(9, 11, 'Amt', tittle_bold_center_style2)
        #ws.write(9, 12, '', tittle_bold_center_style)
        ws.write(9, 13, 'Amt', tittle_bold_center_style2)
        ws.write(9, 14, '%', tittle_bold_center_style2)
        #ws.write(9, 15, '', tittle_bold_center_style)
        ws.write(9, 16, 'Amt', tittle_bold_center_style2)
        ws.write(9, 17, '%', tittle_bold_center_style2)
        #ws.write(9, 18, '', tittle_bold_center_style)
        #ws.write(9, 19, 'Amt', tittle_bold_center_style2)
        #ws.write(9, 20, '%', tittle_bold_center_style2)
        #ws.write(9, 21, '', tittle_bold_center_style)
        #ws.write(9, 22, 'Amt', tittle_bold_center_style2)
        #ws.write(9, 23, '%', tittle_bold_center_style2)
        #ws.write(9, 24, '', tittle_bold_center_style)
        ws.write(9, 19, 'Amt', tittle_bold_center_style2)
        #ws.write(9, 26, '', tittle_bold_center_style)
        ws.write(9, 21, '% Remain', tittle_bold_center_style2)
        for x in [0,1,2,4,6,8,10,12,15,18,20]:
            ws.write(9, x, '', tittle_bold_center_style)
#        for x in [3,9,11,13,14,16,17,19,20,22,23,25,27]:
#            ws.write(9, x, '', tittle_bold_center_style2)
        #self.xls_write_row(ws, None, data, parser, 6, row_hdr9, tittle_bold_center_style)
    
        row_count = 10
        ws.horz_split_pos = row_count
        if len(parser.get_dept(data)) > 0:
            for dep in parser.get_dept(data):
                self.xls_write_row(ws, dep, data, parser, row_count, row_hdr11, tittle_bold_left_style2)
                row_count += 1
                
                ##################CAPEX######################
                capexD = []
                for i in parser.get_data(data):
                    if i['type_budget'] == 'capex':
                        capexD.append(i['id'])
                        if i['type'] == 'view':
                            style = row_bold_style
                        else:
                            style = row_normal_style
                        if data['form']['without_zero']:
                            if i['balance']:
#                                if i['type'] == 'view':
#                                    if row_loop_dep[14][2][0] == 'PreVarMonthDEP' or row_loop_dep[17][2][0] == 'PreVarYearDEP' or row_loop_dep[21][2][0] == 'PreTotBudgetDEP':
#                                        self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_bold_style_pre)
#                                    else:
#                                        self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_normal_style_pre)
#                                else:
                                self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, style)
                                row_count += 1
                        else:
#                            if row_loop_test[14][2][0] == 'PreVarMonthDEP' or row_loop_test[17][2][0] == 'PreVarYearDEP' or row_loop_test[21][2][0] == 'PreTotBudgetDEP':
#                                if i['type'] == 'view':
#                                    self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_bold_style_pre)
#                                else:
#                                    self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_normal_style_pre)
#                            else:
                            self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, style)
                            row_count += 1
                if capexD:
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
#                    if row_total_expense_dep[12][2][0] == 'PreVarMonthTotDEP' or row_total_expense_dep[15][2][0] == 'PreVarYearTotDEP' or row_total_expense_dep[19][2][0] == 'PreTotBudgetTotDEP':
#                        self.xls_write_row(ws, expsD, data, parser, row_count, row_total_expense_dep, row_bold_style_pre)
#                    else:
                    self.xls_write_row(ws, capexD, data, parser, row_count, row_total_capex_dep, row_bold_style_total)
                    #self.xls_write_row(ws, expsD, data, parser, row_count, row_total_expense_dep, row_bold_style_total)
                    row_count += 1
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
                
                
                cogsD = []
                for i in parser.get_data(data):
                    if i['type_budget'] == 'cogs':
                        cogsD.append(i['id'])
                        if i['type'] == 'view':
                            style = row_bold_style
                        else:
                            style = row_normal_style
                        if data['form']['without_zero']:
                            if i['balance']:
#                                if i['type'] == 'view':
#                                    if row_loop_dep[14][2][0] == 'PreVarMonthDEP' or row_loop_dep[17][2][0] == 'PreVarYearDEP' or row_loop_dep[21][2][0] == 'PreTotBudgetDEP':
#                                        self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_bold_style_pre)
#                                    else:
#                                        self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_normal_style_pre)
#                                else:
                                self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, style)
                                row_count += 1
                        else:
#                            if i['type'] == 'view':
#                                if row_loop_dep[14][2][0] == 'PreVarMonthDEP' or row_loop_dep[17][2][0] == 'PreVarYearDEP' or row_loop_dep[21][2][0] == 'PreTotBudgetDEP':
#                                    self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_bold_style_pre)
#                                else:
#                                    self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_normal_style_pre)
#                            else:
                            self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, style)
                            row_count += 1
                if cogsD:
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
#                    if row_total_cogs_dep[12][2][0] == 'PreVarMonthTotDEPCOGS' or row_total_cogs_dep[15][2][0] == 'PreVarYearTotDEPCOGS' or row_total_cogs_dep[19][2][0] == 'PreTotBudgetTotDEPCOGS':
#                        self.xls_write_row(ws, cogsD, data, parser, row_count, row_total_cogs_dep, row_bold_style_pre)
#                    else:
                    self.xls_write_row(ws, cogsD, data, parser, row_count, row_total_cogs_dep, row_bold_style_total)
                    #self.xls_write_row(ws, cogsD, data, parser, row_count, row_total_cogs_dep, row_bold_style_total)
                    row_count += 1
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
                    
                expsD = []
                for i in parser.get_data(data):
                    if i['type_budget'] == 'expense':
                        expsD.append(i['id'])
                        if i['type'] == 'view':
                            style = row_bold_style
                        else:
                            style = row_normal_style
                        if data['form']['without_zero']:
                            if i['balance']:
#                                if i['type'] == 'view':
#                                    if row_loop_dep[14][2][0] == 'PreVarMonthDEP' or row_loop_dep[17][2][0] == 'PreVarYearDEP' or row_loop_dep[21][2][0] == 'PreTotBudgetDEP':
#                                        self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_bold_style_pre)
#                                    else:
#                                        self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_normal_style_pre)
#                                else:
                                self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, style)
                                row_count += 1
                        else:
#                            if row_loop_test[14][2][0] == 'PreVarMonthDEP' or row_loop_test[17][2][0] == 'PreVarYearDEP' or row_loop_test[21][2][0] == 'PreTotBudgetDEP':
#                                if i['type'] == 'view':
#                                    self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_bold_style_pre)
#                                else:
#                                    self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, row_normal_style_pre)
#                            else:
                            self.xls_write_row(ws, i, data, parser, row_count, row_loop_dep, style)
                            row_count += 1
                if expsD:
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
#                    if row_total_expense_dep[12][2][0] == 'PreVarMonthTotDEP' or row_total_expense_dep[15][2][0] == 'PreVarYearTotDEP' or row_total_expense_dep[19][2][0] == 'PreTotBudgetTotDEP':
#                        self.xls_write_row(ws, expsD, data, parser, row_count, row_total_expense_dep, row_bold_style_pre)
#                    else:
                    self.xls_write_row(ws, expsD, data, parser, row_count, row_total_expense_dep, row_bold_style_total)
                    #self.xls_write_row(ws, expsD, data, parser, row_count, row_total_expense_dep, row_bold_style_total)
                    row_count += 1
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
            
        else:
            cogs = []
            for i in parser.get_data(data):
                if i['type_budget'] == 'cogs':
                    cogs.append(i['id'])
                    if i['type'] == 'view':
                        style = row_bold_style
                    else:
                        style = row_normal_style
                    if data['form']['without_zero']:
                        if i['balance']:
#                            if row_loop_test[14][2][0] == 'PreVarMonth' or row_loop_test[17][2][0] == 'PreVarYear' or row_loop_test[21][2][0] == 'PreTotBudget':
#                                if i['type'] == 'view':
#                                    self.xls_write_row(ws, i, data, parser, row_count, row_loop_test, row_bold_style_pre)
#                                else:
#                                    self.xls_write_row(ws, i, data, parser, row_count, row_loop_test, row_normal_style_pre)
#                            else:
                            self.xls_write_row(ws, i, data, parser, row_count, row_loop_test, style)
                            row_count += 1
                    else:
                        self.xls_write_row(ws, i, data, parser, row_count, row_loop_test, style)
                        row_count += 1
            if cogs:
                self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                row_count += 1
#                if row_total_cogs[12][2][0] == 'PreVarMonthTotCOGS' or row_total_cogs[15][2][0] == 'PreVarYearTotCOGS' or row_total_cogs[19][2][0] == 'PreTotBudgetTotCOGS':
#                    self.xls_write_row(ws, cogs, data, parser, row_count, row_total_cogs, row_bold_style_pre)
#                else:
                self.xls_write_row(ws, cogs, data, parser, row_count, row_total_cogs, row_bold_style_total)
                row_count += 1
                self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                row_count += 1
                
            exps = []
            for i in parser.get_data(data):
                if i['type_budget'] == 'expense':
                    exps.append(i['id'])
                    if i['type'] == 'view':
                        style = row_bold_style
                    else:
                        style = row_normal_style
                    if data['form']['without_zero']:
                        if i['balance']:
#                            if row_loop_test[14][2][0] == 'PreVarMonth' or row_loop_test[17][2][0] == 'PreVarYear' or row_loop_test[21][2][0] == 'PreTotBudget':
#                                if i['type'] == 'view':
#                                    self.xls_write_row(ws, i, data, parser, row_count, row_loop_test, row_bold_style_pre)
#                                else:
#                                    self.xls_write_row(ws, i, data, parser, row_count, row_loop_test, row_normal_style_pre)
#                            else:    
                            self.xls_write_row(ws, i, data, parser, row_count, row_loop_test, style)
                            row_count += 1
                    else:#row_loop_test[17][2]['PreVarYear'],row_loop_test[21][2]['PreTotBudget']
#                        if row_loop_test[14][2][0] == 'PreVarMonth' or row_loop_test[17][2][0] == 'PreVarYear' or row_loop_test[21][2][0] == 'PreTotBudget':
#                            if i['type'] == 'view':
#                                self.xls_write_row(ws, i, data, parser, row_count, row_loop_test, row_bold_style_pre)
#                            else:
#                                self.xls_write_row(ws, i, data, parser, row_count, row_loop_test, row_normal_style_pre)
#                        else:    
                        self.xls_write_row(ws, i, data, parser, row_count, row_loop_test, style)
                        row_count += 1
                    
            if exps:
                self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                row_count += 1
#                print "xxxxxxxxxxxxxxx12",row_total_expense[12][2]
#                print "xxxxxxxxxxxxxxx13",row_total_expense[13][2]
#                print "xxxxxxxxxxxxxxx14",row_total_expense[14][2]
#                print "xxxxxxxxxxxxxxx15",row_total_expense[15][2]
#                print "xxxxxxxxxxxxxxx16",row_total_expense[16][2]
#                print "xxxxxxxxxxxxxxx17",row_total_expense[17][2]
#                print "xxxxxxxxxxxxxxx18",row_total_expense[18][2]
#                print "xxxxxxxxxxxxxxx19",row_total_expense[19][2]
#                print "xxxxxxxxxxxxxxx20",row_total_expense[20][2]
#                print "xxxxxxxxxxxxxxx21",row_total_expense[21][2]
#                if row_total_expense[12][2][0] == 'PreVarMonthTot':# or row_total_expense[15][2][0] == 'PreVarYearTot' or row_total_expense[19][2][0] == 'PreTotBudgetTot':
#                    self.xls_write_row(ws, exps, data, parser, row_count, row_total_expense, row_bold_style_pre)
#                else:
                self.xls_write_row(ws, exps, data, parser, row_count, row_total_expense, row_bold_style_total)
                row_count += 1
                self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                row_count += 1

budget_utilization_xls(
        'report.budgets.report.xls',
        'ad_budget.item',
        'addons/ad_budget_report/report/print_budgets_report.mako',
        parser=report_budgets,
        header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: