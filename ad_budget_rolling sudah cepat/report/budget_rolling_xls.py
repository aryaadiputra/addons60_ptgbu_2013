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
from ad_budget_rolling.report.budget_rolling import budget_rolling
import cStringIO
from tools.translate import _

class budget_rolling_xls(report_xls):
    print "EEEEEEEEEEEEEEE"
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

    """def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))"""
    
    def generate_xls_report(self, parser, data, obj, wb):
        
        c = parser.localcontext['company']
        ws = wb.add_sheet(('Budget Rolling'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        ws.col(0).width = len("ABC")*256
        ws.col(1).width = len("ABCD")*512
        ws.col(2).width = len("ABCD")*512
        ws.col(3).width = len("ABC")*256
        ws.col(21).width = len("ABCD")*1024
        ws.col(22).width = len("ABCD")*1024
        ws.col(23).width = len("ABCD")*1024
        #ws.col(4).width = len("A bunch of longer text not wrapped")*256
        #ws.row(4).height = len("A bunch of longer text not wrapped")*256
        company = "%s" % (c.name)
        
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
                ('Space', 23, 0, 'text',
                    lambda x, d, p: ""),
                ('Company', 23, 0, 'text',
                    lambda x, d, p: company.upper()),
                ('Judul', 23, 0, 'text',
                    lambda x, d, p: "Budget Rolling Report (Detail)"),
                ('Dept', 23, 0, 'text',
                    lambda x, d, p: x.name),
                ('AsOff', 23, 0, 'text',
                    lambda x, d, p: "As of %s " % (parser.formatLang(data['form']['as_of'], date=True))),
                ('HeaderCOA', 2, 0, 'text',
                    lambda x, d, p: "COA"),
                ('HeaderDesc', 6, 0, 'text',
                    lambda x, d, p: "DESCRIPTION"),
                ('HeaderM1', 1, 0, 'text', lambda x, d, p: data['form']['1']['date']),
                ('HeaderM2', 1, 0, 'text', lambda x, d, p: data['form']['2']['date']),
                ('HeaderM3', 1, 0, 'text', lambda x, d, p: data['form']['3']['date']),
                ('HeaderM4', 1, 0, 'text', lambda x, d, p: data['form']['4']['date']),
                ('HeaderM5', 1, 0, 'text', lambda x, d, p: data['form']['5']['date']),
                ('HeaderM6', 1, 0, 'text', lambda x, d, p: data['form']['6']['date']),
                ('HeaderM7', 1, 0, 'text', lambda x, d, p: data['form']['7']['date']),
                ('HeaderM8', 1, 0, 'text', lambda x, d, p: data['form']['8']['date']),
                ('HeaderM9', 1, 0, 'text', lambda x, d, p: data['form']['9']['date']),
                ('HeaderM10', 1, 0, 'text', lambda x, d, p: data['form']['10']['date']),
                ('HeaderM11', 1, 0, 'text', lambda x, d, p: data['form']['11']['date']),
                ('HeaderM12', 1, 0, 'text', lambda x, d, p: data['form']['12']['date']),
                ('HeaderTotal', 1, 0, 'text', lambda x, d, p: "TOTAL"),
                ('HeaderBudget', 1, 0, 'text', lambda x, d, p: "BUDGET"),
                ('HeaderVariance', 1, 0, 'text', lambda x, d, p: "VARIANCE"),
                
                
                ('StateCOA', 2, 0, 'text', lambda x, d, p: ""),
                ('StateDesc', 6, 0, 'text', lambda x, d, p: ""),
                ('StateM1', 1, 0, 'text', lambda x, d, p: data['form']['1']['state']),
                ('StateM2', 1, 0, 'text', lambda x, d, p: data['form']['2']['state']),
                ('StateM3', 1, 0, 'text', lambda x, d, p: data['form']['3']['state']),
                ('StateM4', 1, 0, 'text', lambda x, d, p: data['form']['4']['state']),
                ('StateM5', 1, 0, 'text', lambda x, d, p: data['form']['5']['state']),
                ('StateM6', 1, 0, 'text', lambda x, d, p: data['form']['6']['state']),
                ('StateM7', 1, 0, 'text', lambda x, d, p: data['form']['7']['state']),
                ('StateM8', 1, 0, 'text', lambda x, d, p: data['form']['8']['state']),
                ('StateM9', 1, 0, 'text', lambda x, d, p: data['form']['9']['state']),
                ('StateM10', 1, 0, 'text', lambda x, d, p: data['form']['10']['state']),
                ('StateM11', 1, 0, 'text', lambda x, d, p: data['form']['11']['state']),
                ('StateM12', 1, 0, 'text', lambda x, d, p: data['form']['12']['state']),
#                ('Fiscal Year', 5, 0, 'text',
#                    lambda x, d, p: 'self._display_filter(p, d)'),
#                ('Create Date', 5, 0, 'text',
#                    lambda x, d, p: 'Create date: ' + p.formatLang(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),date_time = True)),
                #('Filter', 10, 0, 'text',
                #    lambda x, d, p: self._display_filter(p, d)),
                # Balance column
                
                ###############################################
#                ('Code',      2, 67,  'text',   lambda x, d, p: x['code']),
#                ('Name',      6, 270, 'text',   lambda x, d, p: '   '*x['level'] + x['name']),
#                ('MD1',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], dep['id'])),
#                ('MD2',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], dep['id'])),
#                ('MD3',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], dep['id'])),
#                ('MD4',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], dep['id'])),
#                ('MD5',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], dep['id'])),
#                ('MD6',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], dep['id'])),
#                ('MD7',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], dep['id'])),
#                ('MD8',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], dep['id'])),
#                ('MD9',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], dep['id'])),
#                ('MD10',      1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], dep['id'])),
#                ('MD11',      1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], dep['id'])),
#                ('MD12',      1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], dep['id'])),
#                ('TotalD',    1, 270, 'number', lambda x, d, p: parser.get_total(data['form']['as_of'], data['form']['fiscalyear_id'], i['id'], i['type'], dep['id']) or 0.0),
#                ('BudgetD',   1, 270, 'number', lambda x, d, p: parser.get_total_BudgetD(data['form']['as_of'], data['form']['fiscalyear_id'], i['id'], False, dep['id'])),
#                ('VarianceD', 1, 270, 'number', lambda x, d, p: (parser.get_total_BudgetD(data['form']['as_of'], data['form']['fiscalyear_id'], i['id'], False, dep['id']))-(parser.get_total(data['form']['as_of'], data['form']['fiscalyear_id'], i['id'], i['type'], dep['id'])) or 0.0),
#                
                ###############################################
                
#                #WITH DEPARTMENT
                ('Code',      2, 67,  'text',   lambda x, d, p: x['code']),
                ('Name',      6, 270, 'text',   lambda x, d, p: '   '*x['level'] + x['name']),
#                ('MD1',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], dep['id'])),
#                ('MD2',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], dep['id'])),
#                ('MD3',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], dep['id'])),
#                ('MD4',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], dep['id'])),
#                ('MD5',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], dep['id'])),
#                ('MD6',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], dep['id'])),
#                ('MD7',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], dep['id'])),
#                ('MD8',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], dep['id'])),
#                ('MD9',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], dep['id'])),
#                ('MD10',      1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], dep['id'])),
#                ('MD11',      1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], dep['id'])),
#                ('MD12',      1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], dep['id'])),
#                ('TotalD',    1, 270, 'number', lambda x, d, p: parser.get_total(data['form']['as_of'], data['form']['fiscalyear_id'], i['id'], i['type'], dep['id']) or 0.0),
#                ('BudgetD',   1, 270, 'number', lambda x, d, p: parser.get_total_BudgetD(data['form']['as_of'], data['form']['fiscalyear_id'], i['id'], False, dep['id'])),
#                ('VarianceD', 1, 270, 'number', lambda x, d, p: (parser.get_total_BudgetD(data['form']['as_of'], data['form']['fiscalyear_id'], i['id'], False, dep['id']))-(parser.get_total(data['form']['as_of'], data['form']['fiscalyear_id'], i['id'], i['type'], dep['id'])) or 0.0),
#                #NO DEPARTMENT
#                ('M1',        1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], False)),
#                ('M2',        1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], False)),
#                ('M3',        1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], False)),
#                ('M4',        1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], False)),
#                ('M5',        1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], False)),
#                ('M6',        1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], False)),
#                ('M7',        1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], False)),
#                ('M8',        1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], False)),
#                ('M9',        1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], False)),
#                ('M10',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], False)),
#                ('M11',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], False)),
#                ('M12',       1, 270, 'number', lambda x, d, p: parser.get_period(data['form']['as_of'], data['form']['fiscalyear_id'], data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], False)),
#                ('Total',     1, 270, 'number', lambda x, d, p: parser.get_total(data['form']['as_of'], data['form']['fiscalyear_id'], i['id'], i['type'], False) or 0.0),
#                ('Budget',    1, 270, 'number', lambda x, d, p: x['balance'] or 0.0),
#                ('Variance',  1, 270, 'number', lambda x, d, p: x['balance']-parser.get_total(data['form']['as_of'], data['form']['fiscalyear_id'], i['id'], i['type'], False) or 0.0),
        ]
        

        row_hdr0 = self.xls_row_template(cols_specs, ['Kosong','Note','Note1'])
        row_hdr1 = self.xls_row_template(cols_specs, ['Kosong','Kosong','Note2'])
        row_hdr2 = self.xls_row_template(cols_specs, ['Kosong','Kosong','Note3'])
        row_hdr3 = self.xls_row_template(cols_specs, ['Kosong','Space'])
        row_hdr4 = self.xls_row_template(cols_specs, ['Kosong','Company'])
        row_hdr5 = self.xls_row_template(cols_specs, ['Kosong','Judul'])
        row_hdr6 = self.xls_row_template(cols_specs, ['Kosong','AsOff'])
        row_hdr7 = self.xls_row_template(cols_specs, ['Kosong','Space'])
        row_hdr8 = self.xls_row_template(cols_specs, ['Kosong','HeaderCOA','HeaderDesc','HeaderM1','HeaderM2','HeaderM3','HeaderM4','HeaderM5','HeaderM6','HeaderM7','HeaderM8','HeaderM9','HeaderM10','HeaderM11','HeaderM12','HeaderTotal','HeaderBudget','HeaderVariance'])
        row_hdr9 = self.xls_row_template(cols_specs, ['Kosong','StateCOA','StateDesc','StateM1','StateM2','StateM3','StateM4','StateM5','StateM6','StateM7','StateM8','StateM9','StateM10','StateM11','StateM12','Kosong','Kosong','Kosong'])
        #row_hdr9 = self.xls_row_template(cols_specs, ['Kosong','Space'])
        row_hdr10 = self.xls_row_template(cols_specs, ['Kosong','Space'])
        row_hdr11 = self.xls_row_template(cols_specs, ['Kosong','Dept'])
        row_loopDep = self.xls_row_template(cols_specs, ['Kosong','Code','Name','MD1','MD2','MD3','MD4','MD5','MD6','MD7','MD8','MD9','MD10','MD11','MD12','TotalD','BudgetD','VarianceD'])#
        row_loop = self.xls_row_template(cols_specs, ['Kosong','Code','Name','M1','M2','M3','M4','M5','M6','M7','M8','M9','M10','M11','M12','Total','Budget','Variance'])
        row_total_cogs = self.xls_row_template(cols_specs, ['Kosong','TotalCOGSDesc','MtotCOGS1','MtotCOGS2','MtotCOGS3','MtotCOGS4','MtotCOGS5','MtotCOGS6','MtotCOGS7','MtotCOGS8','MtotCOGS9','MtotCOGS10','MtotCOGS11','MtotCOGS12','TotalCOGS','BudgetCOGS','VarianceCOGS'])
        row_total_expense = self.xls_row_template(cols_specs, ['Kosong','TotalExpense','MtotEXP1','MtotEXP2','MtotEXP3','MtotEXP4','MtotEXP5','MtotEXP6','MtotEXP7','MtotEXP8','MtotEXP9','MtotEXP10','MtotEXP11','MtotEXP12','TotalEXP','BudgetEXP','VarianceEXP'])
#
        ########################ARYA#######################
        row_total_capexDep = self.xls_row_template(cols_specs, ['Kosong','TotalCAPEXDepDesc','MtotCAPEXDep1','MtotCAPEXDep2','MtotCAPEXDep3','MtotCAPEXDep4','MtotCAPEXDep5','MtotCAPEXDep6','MtotCAPEXDep7','MtotCAPEXDep8','MtotCAPEXDep9','MtotCAPEXDep10','MtotCAPEXDep11','MtotCAPEXDep12','TotalCAPEXDep','BudgetCAPEXDep','VarianceCAPEXDep'])
        ###################################################
        row_total_cogsDep = self.xls_row_template(cols_specs, ['Kosong','TotalCOGSDepDesc','MtotCOGSDep1','MtotCOGSDep2','MtotCOGSDep3','MtotCOGSDep4','MtotCOGSDep5','MtotCOGSDep6','MtotCOGSDep7','MtotCOGSDep8','MtotCOGSDep9','MtotCOGSDep10','MtotCOGSDep11','MtotCOGSDep12','TotalCOGSDep','BudgetCOGSDep','VarianceCOGSDep'])
        row_total_expenseDep = self.xls_row_template(cols_specs, ['Kosong','TotalExpenseDep','MtotEXPDep1','MtotEXPDep2','MtotEXPDep3','MtotEXPDep4','MtotEXPDep5','MtotEXPDep6','MtotEXPDep7','MtotEXPDep8','MtotEXPDep9','MtotEXPDep10','MtotEXPDep11','MtotEXPDep12','TotalEXPDep','BudgetEXPDep','VarianceEXPDep'])

        ## Style variable Begin borders: top thick, bottom solid, left double, right double;
        hdr_style = xlwt.easyxf('pattern: pattern solid, fore_color gray25;')
        row_normal_style=  xlwt.easyxf('font: height 170, colour_index black;pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        row_bold_style = xlwt.easyxf('font: height 180, colour_index black, bold on;pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        row_bold_style_total = xlwt.easyxf('font: height 180, colour_index black, bold on;pattern: pattern solid, fore_color white;borders: top thin, bottom medium;',num_format_str='#,##0;(#,##0)')
        style = xlwt.easyxf(styles['reversed'])
        tittle_style = xlwt.easyxf('font: height 180,name Arial, colour_index white, bold on; pattern: pattern solid, fore_color brown;')
        tittle_style2 = xlwt.easyxf('font: height 180,name Arial, colour_index white, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        tittle_bold_left_style = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        tittle_bold_left_style2 = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;borders: bottom double;')
        tittle_left_italic_style = xlwt.easyxf('font: height 190, name Arial, colour_index black, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        tittle_bold_center_style = xlwt.easyxf('font: height 180, name Arial, colour_index white, bold on; align: wrap on, vert centre, horiz centre; pattern: pattern solid, fore_color gray50;')
        #row_normal_style = xlwt.easyxf('font: height 170, name Arial, colour_index black; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        #row_bold_style = xlwt.easyxf('font: height 180, name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        subtittle_right_style = xlwt.easyxf('font: height 170, name Arial, colour_index black, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        subtittle_top_and_bottom_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        blank_style = xlwt.easyxf('font: height 650, name Arial, colour_index brown, bold off; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        normal_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off; align: wrap on, vert centre, horiz left;')
        total_style = xlwt.easyxf('font: height 240, name Arial, colour_index brown, bold on, italic on; align: wrap on, vert centre;', num_format_str='#,##0.00;(#,##0.00)')
        ## Style variable End

        # Write headers
        ws.write(0, 0, '', tittle_style2)
        ws.write(0, 1, '', tittle_style2)
        ws.write(0, 2, 'Note: ', tittle_style)
        ws.write(0, 3, '1.', tittle_style)
        ws.write(0, 4, 'This rolling report should include P&L, cashflow & balance sheet', tittle_style)
        for x in [5,6,7,8,9]:
            ws.write(0, x, '', tittle_style)
        for x in [10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
            ws.write(0, x, '', tittle_style2)
                
        ws.write(1, 0, '', tittle_style2)
        ws.write(1, 1, '', tittle_style2)
        ws.write(1, 2, '', tittle_style)
        ws.write(1, 3, '2.', tittle_style)
        ws.write(1, 4, 'ERP should produce both detail & summary (high level, major accounts)', tittle_style)
        for x in [5,6,7,8,9]:
            ws.write(1, x, '', tittle_style)
        for x in [10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
            ws.write(1, x, '', tittle_style2)
                
        ws.write(2, 0, '', tittle_style2)
        ws.write(2, 1, '', tittle_style2)
        ws.write(2, 2, '', tittle_style)
        ws.write(2, 3, '3.', tittle_style)
        ws.write(2, 4, 'Need to add Revenue', tittle_style)
        for x in [5,6,7,8,9]:
            ws.write(2, x, '', tittle_style)
        for x in [10,11,12,13,14,15,16,17,18,19,20,21,22,23]:
            ws.write(2, x, '', tittle_style2)
        #====================================================================    
#        self.xls_write_row(ws, None, data, parser, 3, row_hdr0, tittle_style)
#        self.xls_write_row(ws, None, data, parser, 4, row_hdr1, tittle_style)
#        self.xls_write_row(ws, None, data, parser, 5, row_hdr2, tittle_style)
        self.xls_write_row(ws, None, data, parser, 3, row_hdr3, tittle_style2)#Space
        self.xls_write_row(ws, None, data, parser, 4, row_hdr4, tittle_bold_left_style)#Company
        self.xls_write_row(ws, None, data, parser, 5, row_hdr5, tittle_bold_left_style)#Budget Rolling
        self.xls_write_row(ws, None, data, parser, 6, row_hdr6, tittle_left_italic_style)#As of
        self.xls_write_row(ws, None, data, parser, 7, row_hdr7, tittle_style2)#Space
        self.xls_write_row(ws, None, data, parser, 8, row_hdr8, tittle_bold_center_style)
        self.xls_write_row(ws, None, data, parser, 9, row_hdr9, tittle_bold_center_style)
        
        row_count = 10
        ws.horz_split_pos = row_count
        
        if len(parser.get_department(data))>0:
            for dep in parser.get_department(data):
                self.xls_write_row(ws, dep, data, parser, row_count, row_hdr11, tittle_bold_left_style2)
                row_count += 1
                
                ###########ARYA############
                capexD = []
                for i in parser.get_data(data):
                    #print "iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii", i
                    if i['type_budget'] == 'capex':
                        capexD.append(i['id'])
                        if i['type'] == 'view':
                            style = row_bold_style
                        else:
                            style = row_normal_style
                        if data['form']['without_zero']:
                            if i['balance']:
                                self.xls_write_row(ws, i, data, parser, row_count, row_loopDep, style)
                                
                                col = 9
                                for val in parser.get_account_amount(data, i):
                                    print "val Amount-----------------", val[1] or 0.0
                                    ws.write(row_count,col,val[1] or 0.0)
                                    col += 1
                                
                                row_count += 1
                        else:
                            self.xls_write_row(ws, i, data, parser, row_count, row_loopDep, style)
                            col = 9
                            actual_col = 9
                            for val in parser.get_account_amount(data, i):
                                #print "val Amount-----------------", val[1] or 0.0
                                if val[0] < 13:
                                    ws.write(row_count,col,val[1] or 0.0, style)
                                ##########Kolom Total Budget##########
                                else:
                                    print "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP", row_count
                                    ws.write(row_count,22,val[1] or 0.0, style)
#                                    
                                ######################################
                                
                                col += 1
                                actual_col = val[2]
                            actual_col = 9 + actual_col - 1
                            cell1=xlwt.Utils.rowcol_to_cell(row_count,9)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count,actual_col)
                            formula_tot_budget="SUM(%s:%s)"%(cell1,cell2)
                            
                            cell1=xlwt.Utils.rowcol_to_cell(row_count,21)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count,22)
                            formula_variance="%s-%s"%(cell2,cell1)
                            
                            print "row_count Total", row_count
                            #if i['type'] <> 'view':
                            ws.write(row_count,21,xlwt.Formula(formula_tot_budget), style)
                            ws.write(row_count,23,xlwt.Formula(formula_variance), style)
                            row_count += 1
                        
                        
                #print "------",capexD
                if capexD:
                    print "))))))))))))))))))))))))))"
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
                    self.xls_write_row(ws, None, data, parser, row_count, row_total_capexDep, row_bold_style_total)
                    ws.write_merge(row_count,row_count,1,23,"Capital Expense",row_bold_style_total)
                    row_count += 1
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
                #######################
                
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
                                self.xls_write_row(ws, i, data, parser, row_count, row_loopDep, style)
                                col = 9
                                for val in parser.get_account_amount(data, i):
                                    print "val Amount-----------------", val[1] or 0.0
                                    ws.write(row_count,col,val[1] or 0.0)
                                    col += 1
                                row_count += 1
                        else:
                            self.xls_write_row(ws, i, data, parser, row_count, row_loopDep, style)
                            col = 9
                            actual_col = 9
                            for val in parser.get_account_amount(data, i):
                                #print "val Amount-----------------", val[1] or 0.0
                                if val[0] < 13:
                                    ws.write(row_count,col,val[1] or 0.0, style)
                                ##########Kolom Total Budget##########
                                else:
                                    print "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP", row_count
                                    ws.write(row_count,22,val[1] or 0.0, style)
#                                    
                                ######################################
                                
                                col += 1
                                actual_col = val[2]
                            actual_col = 9 + actual_col - 1
                            cell1=xlwt.Utils.rowcol_to_cell(row_count,9)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count,actual_col)
                            formula_tot_budget="SUM(%s:%s)"%(cell1,cell2)
                            
                            cell1=xlwt.Utils.rowcol_to_cell(row_count,21)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count,22)
                            formula_variance="%s-%s"%(cell2,cell1)
                            
                            print "row_count Total", row_count
                            #if i['type'] <> 'view':
                            ws.write(row_count,21,xlwt.Formula(formula_tot_budget), style)
                            ws.write(row_count,23,xlwt.Formula(formula_variance), style)
                            row_count += 1
                #print "------",cogsD
                if cogsD:
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
                    self.xls_write_row(ws, None, data, parser, row_count, row_total_cogsDep, row_bold_style_total)
                    ws.write_merge(row_count,row_count,1,23,"Cost of Goods Sale",row_bold_style_total)
                    row_count += 1
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
                expsD = []
                for i in parser.get_data(data):
                    #print "iiiiiiiiiiiiiiiiiiiiiiiiiiiiiii", i
                    if i['type_budget'] == 'expense':
                        expsD.append(i['id'])
                        if i['type'] == 'view':
                            style = row_bold_style
                        else:
                            style = row_normal_style
                        if data['form']['without_zero']:
                            if i['balance']:
                                self.xls_write_row(ws, i, data, parser, row_count, row_loopDep, style)
                                col = 9
                                for val in parser.get_account_amount(data, i):
                                    #print "val Amount-----------------", val[1] or 0.0
                                    ws.write(row_count,col,val[1] or 0.0 or 0.0)
                                    col += 1
                                row_count += 1
                        else:
                            self.xls_write_row(ws, i, data, parser, row_count, row_loopDep, style)
                            col = 9
                            actual_col = 9
                            for val in parser.get_account_amount(data, i):
                                #print "val Amount-----------------", val[1] or 0.0
                                if val[0] < 13:
                                    ws.write(row_count,col,val[1] or 0.0, style)
                                ##########Kolom Total Budget##########
                                else:
                                    print "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP", row_count
                                    ws.write(row_count,22,val[1] or 0.0, style)
#                                    
                                ######################################
                                
                                col += 1
                                actual_col = val[2]
                            actual_col = 9 + actual_col - 1
                            cell1=xlwt.Utils.rowcol_to_cell(row_count,9)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count,actual_col)
                            formula_tot_budget="SUM(%s:%s)"%(cell1,cell2)
                            
                            cell1=xlwt.Utils.rowcol_to_cell(row_count,21)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count,22)
                            formula_variance="%s-%s"%(cell2,cell1)
                            
                            print "row_count Total", row_count
                            #if i['type'] <> 'view':
                            ws.write(row_count,21,xlwt.Formula(formula_tot_budget), style)
                            ws.write(row_count,23,xlwt.Formula(formula_variance), style)
                            row_count += 1
                #print "xxxxx",expsD
                if expsD:
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
                    self.xls_write_row(ws, None, data, parser, row_count, row_total_expenseDep, row_bold_style_total)
                    ws.write_merge(row_count,row_count,1,23,"Operating Expense",row_bold_style_total)
                    row_count += 1
                    self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                    row_count += 1
        
        #####################NON Department########################
        
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
                            self.xls_write_row(ws, i, data, parser, row_count, row_loop, style)
                            row_count += 1
                    else:
                        self.xls_write_row(ws, i, data, parser, row_count, row_loop, style)
                        col = 9
                        for val in parser.get_account_amount(data, i):
                            print "val Amount-----------------", val[1]
                            ws.write(row_count,col,val[1])
                            col += 1
                        row_count += 1
            if cogs:
                self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                row_count += 1
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
                            self.xls_write_row(ws, i, data, parser, row_count, row_loop, style)
                            row_count += 1
                    else:
                        self.xls_write_row(ws, i, data, parser, row_count, row_loop, style)
                        row_count += 1
            if exps:
                self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                row_count += 1
                self.xls_write_row(ws, exps, data, parser, row_count, row_total_expense, row_bold_style_total)
                row_count += 1
                self.xls_write_row(ws, None, data, parser, row_count, row_hdr3, tittle_style2)
                row_count += 1
        pass

budget_rolling_xls(
        'report.budget.rolling.xls',
        'ad_budget.item',
        'addons/ad_budget_rolling/report/budget_rolling.mako',
        parser=budget_rolling,
        header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
