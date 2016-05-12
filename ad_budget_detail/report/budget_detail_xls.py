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
from ad_budget_detail.report.budget_detail import budget_detail
import cStringIO
from tools.translate import _
from xlwt import Workbook, Formula

class budget_detail_xls(report_xls):
    
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
        ws = wb.add_sheet(('Detail Account'))
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        ws.col(0).width = len("ABC")*256
        ws.col(1).width = len("ABC")*1280
        ws.col(2).width = len("ABCDEF")*2048
        ws.col(3).width = len("ABC")*256
        ws.col(4).width = len("ABC")*1280
        ws.col(5).width = len("ABC")*256
        ws.col(7).width = len("ABC")*256
        ws.col(9).width = len("ABC")*256
        ws.col(11).width = len("ABC")*256
        ws.col(13).width = len("ABC")*256
        ws.col(15).width = len("ABC")*256
        ws.col(17).width = len("ABC")*256
        ws.col(19).width = len("ABC")*256
        ws.col(21).width = len("ABC")*256
        ws.col(23).width = len("ABC")*256
        ws.col(25).width = len("ABC")*256
        ws.col(27).width = len("ABC")*256
        ws.col(29).width = len("ABC")*256
        ws.col(30).width = len("ABC")*1280
        ws.col(31).width = len("ABC")*256
        #ws.col(33).width = len("ABC")*256
        #ws.col(35).width = len("ABC")*256
#        ws.col(11).width = len("ABC")*256
#        ws.col(21).width = len("ABCD")*1024
#        ws.col(22).width = len("ABCD")*1024
#        ws.col(23).width = len("ABCD")*1024
        #ws.col(4).width = len("A bunch of longer text not wrapped")*256
        #ws.row(4).height = len("A bunch of longer text not wrapped")*256
        company = "%s" % (c.name)
        as_of = data['form']['as_of_date']
        fy = data['form']['fiscalyear_id']
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
                ('Space', 31, 0, 'text',
                    lambda x, d, p: ""),
                ('Space2', 32, 0, 'text',
                    lambda x, d, p: ""),
                ('Space_dep', 31, 0, 'text',
                    lambda x, d, p: x.name),
                ('Company', 31, 0, 'text',
                    lambda x, d, p: company.upper()),
                ('Judul', 31, 0, 'text',
                    lambda x, d, p: "Detail of Account"),
                ('Dept', 31, 0, 'text',
                    lambda x, d, p: x.name),
                ('AsOff', 31, 0, 'text',
                    lambda x, d, p: "As of %s " % (parser.formatLang(as_of, date=True))),
                ('HeaderCOA', 5, 0, 'text',
                    lambda x, d, p: "Account"),
                ('HeaderDesc', 2, 0, 'text',
                    lambda x, d, p: "Descriptions"),
#                ('Fiscal Year', 5, 0, 'text',
#                    lambda x, d, p: 'self._display_filter(p, d)'),
#                ('Create Date', 5, 0, 'text',
#                    lambda x, d, p: 'Create date: ' + p.formatLang(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),date_time = True)),
                #('Filter', 10, 0, 'text',
                #    lambda x, d, p: self._display_filter(p, d)),
                # Balance column
                #WITH DEPARTMENT
                ('Code',      1, 67,  'text',   lambda x, d, p: '   '*x['level'] + x['name']),
                ('Name',      1, 270, 'text',   lambda x, d, p: 'Budget'),           ('Variance',  1, 270, 'number', lambda x, d, p: x['balance']-parser.get_total(as_of, fy, i['id'], i['type'], False) or 0.0),
        ]

        row_hdr0 = self.xls_row_template(cols_specs, ['Kosong','Note','Note1'])
        row_hdr1 = self.xls_row_template(cols_specs, ['Kosong','Kosong','Note2'])
        row_hdr2 = self.xls_row_template(cols_specs, ['Kosong','Kosong','Note3'])
        row_hdr3 = self.xls_row_template(cols_specs, ['Kosong','Space'])
        row_hdr4 = self.xls_row_template(cols_specs, ['Kosong','Company'])
        row_hdr5 = self.xls_row_template(cols_specs, ['Kosong','Judul'])
        row_hdr6 = self.xls_row_template(cols_specs, ['Kosong','AsOff'])
        row_hdr7 = self.xls_row_template(cols_specs, ['Space2'])
        row_hdr_dep = self.xls_row_template(cols_specs, ['Kosong','Space_dep'])
        row_hdr8 = self.xls_row_template(cols_specs, ['Kosong','HeaderCOA','HeaderDesc','HeaderM1','HeaderM2','HeaderM3','HeaderM4','HeaderM5','HeaderM6','HeaderM7','HeaderM8','HeaderM9','HeaderM10','HeaderM11','HeaderM12','HeaderTotal','HeaderBudget','HeaderVariance'])
        row_hdr9 = self.xls_row_template(cols_specs, ['Kosong','StateCOA','StateDesc','StateM1','StateM2','StateM3','StateM4','StateM5','StateM6','StateM7','StateM8','StateM9','StateM10','StateM11','StateM12','Kosong','Kosong','Kosong'])
        #row_hdr9 = self.xls_row_template(cols_specs, ['Kosong','Space'])
        row_hdr10 = self.xls_row_template(cols_specs, ['Kosong','Space'])
        row_hdr11 = self.xls_row_template(cols_specs, ['Kosong','Dept'])
        row_loopDep = self.xls_row_template(cols_specs, ['Kosong','Kosong','Code','Name','MD1','MD2','MD3','MD4','MD5','MD6','MD7','MD8','MD9','MD10','MD11','MD12','TotalD','BudgetD','VarianceD'])#
        row_loop = self.xls_row_template(cols_specs, ['Kosong','Kosong','Code','Kosong','Name','SP','M1','SP','M2','SP','M3','SP','M4','SP','M5','SP','M6','SP','M7','SP','M8','SP','M9','SP','M10','SP','M11','SP','M12','SP'])
        row_loop_actual = self.xls_row_template(cols_specs, ['Kosong','Kosong','Kosong','Kosong','Actual','Kosong','Mact1','SP','Mact2','SP','Mact3','SP','Mact4','SP','Mact5','SP','Mact6','SP','Mact7','SP','Mact8','SP','Mact9','SP','Mact10','SP','Mact11','SP','Mact12','SP'])
        row_loop_under = self.xls_row_template(cols_specs, ['Kosong','Kosong','Kosong','Kosong','Under','Kosong','Mund1','SP','Mund2','SP','Mund3','SP','Mund4','SP','Mund5','SP','Mund6','SP','Mund7','SP','Mund8','SP','Mund9','SP','Mund10','SP','Mund11','SP','Mund12','SP'])
        row_total_cogs = self.xls_row_template(cols_specs, ['Kosong','TotalCOGSDesc','MtotCOGS1','MtotCOGS2','MtotCOGS3','MtotCOGS4','MtotCOGS5','MtotCOGS6','MtotCOGS7','MtotCOGS8','MtotCOGS9','MtotCOGS10','MtotCOGS11','MtotCOGS12','TotalCOGS','BudgetCOGS','VarianceCOGS'])
        row_total_expense = self.xls_row_template(cols_specs, ['Kosong','TotalExpense','MtotEXP1','MtotEXP2','MtotEXP3','MtotEXP4','MtotEXP5','MtotEXP6','MtotEXP7','MtotEXP8','MtotEXP9','MtotEXP10','MtotEXP11','MtotEXP12','TotalEXP','BudgetEXP','VarianceEXP'])
#
#
        row_total_cogsDep = self.xls_row_template(cols_specs, ['Kosong','TotalCOGSDepDesc','MtotCOGSDep1','MtotCOGSDep2','MtotCOGSDep3','MtotCOGSDep4','MtotCOGSDep5','MtotCOGSDep6','MtotCOGSDep7','MtotCOGSDep8','MtotCOGSDep9','MtotCOGSDep10','MtotCOGSDep11','MtotCOGSDep12','TotalCOGSDep','BudgetCOGSDep','VarianceCOGSDep'])
        row_total_expenseDep = self.xls_row_template(cols_specs, ['Kosong','TotalExpenseDep','MtotEXPDep1','MtotEXPDep2','MtotEXPDep3','MtotEXPDep4','MtotEXPDep5','MtotEXPDep6','MtotEXPDep7','MtotEXPDep8','MtotEXPDep9','MtotEXPDep10','MtotEXPDep11','MtotEXPDep12','TotalEXPDep','BudgetEXPDep','VarianceEXPDep'])

        ## Style variable Begin borders: top thick, bottom solid, left double, right double;
        hdr_style = xlwt.easyxf('pattern: pattern solid, fore_color gray25;')
        row_normal_style=  xlwt.easyxf('font: height 170, colour_index black;pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        row_bold_style = xlwt.easyxf('font: height 180, colour_index black, bold on;pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        row_bold_style_total = xlwt.easyxf('font: height 180, colour_index black, bold on;pattern: pattern solid, fore_color white;borders: top thin, bottom medium;',num_format_str='#,##0;(#,##0)')
        style = xlwt.easyxf(styles['reversed'])
        style_bold = xlwt.easyxf('font: height 170, colour_index black, bold on; align: wrap on, vert top, horiz right;pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        style_italic_bold = xlwt.easyxf('font: height 170, colour_index black, bold on, italic on; align: wrap on, vert top, horiz left;pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        style_under = xlwt.easyxf('font: height 170, colour_index black;pattern: pattern solid, fore_color white; borders: top thin;',num_format_str='#,##0;(#,##0)')
        style_under_bold = xlwt.easyxf('font: height 170, colour_index black, bold on; align: wrap on, vert top, horiz right;pattern: pattern solid, fore_color white; borders: top thin;',num_format_str='#,##0;(#,##0)')
        tittle_style_closed = xlwt.easyxf('font: height 180, colour_index black, bold on;pattern: pattern solid, fore_color white; borders: right thin;',num_format_str='#,##0;(#,##0)')
        tittle_style_closed_dep = xlwt.easyxf('font: height 180, colour_index black, bold on;pattern: pattern solid, fore_color white; borders: bottom double;',num_format_str='#,##0;(#,##0)')
        tittle_style_closed_bottom = xlwt.easyxf('font: height 180, colour_index black, bold on;pattern: pattern solid, fore_color white; borders: right thin, bottom thin;',num_format_str='#,##0;(#,##0)')
        tittle_style = xlwt.easyxf('font: height 180,name Arial, colour_index white, bold on; pattern: pattern solid, fore_color brown;')
        tittle_style2 = xlwt.easyxf('font: height 180,name Arial, colour_index white, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        tittle_bold_left_style = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        tittle_left_style = xlwt.easyxf('font: height 200, name Arial, colour_index black; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        tittle_bold_left_style2 = xlwt.easyxf('font: height 200, name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;borders: bottom double;')
        tittle_left_italic_style = xlwt.easyxf('font: height 190, name Arial, colour_index black, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;')
        tittle_bold_center_style_top = xlwt.easyxf('font: height 190, name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz centre; pattern: pattern solid, fore_color gray25;borders: top thin;')
        tittle_bold_center_style_bottom = xlwt.easyxf('font: height 190, name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz centre; pattern: pattern solid, fore_color gray25;borders: bottom thin;')
        #row_normal_style = xlwt.easyxf('font: height 170, name Arial, colour_index black; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        #row_bold_style = xlwt.easyxf('font: height 180, name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color white;',num_format_str='#,##0;(#,##0)')
        subtittle_right_style = xlwt.easyxf('font: height 170, name Arial, colour_index black, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        subtittle_top_and_bottom_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        blank_style = xlwt.easyxf('font: height 650, name Arial, colour_index brown, bold off; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        normal_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off; align: wrap on, vert centre, horiz left;')
        total_style = xlwt.easyxf('font: height 240, name Arial, colour_index brown, bold on, italic on; align: wrap on, vert centre;', num_format_str='#,##0.00;(#,##0.00)')
        ## Style variable End

        # Write headers
        for u in [0,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]:
            ws.write(4, u, '', tittle_style2)
        #ws.write(4, 31, '', tittle_style_closed)
        for s in [1,2,4,6,8,10,12,14,16,18,20,22,24,26,28]:
            ws.write(4, s, '', tittle_bold_center_style_top)
        ws.write(4, 30, 'TOTAL', tittle_bold_center_style_top)
        #ws.write(4, 32, 'TOTAL', tittle_bold_center_style_top)
        #ws.write(4, 34, 'REMAINING', tittle_bold_center_style_top)
        #ws.write(6, 0, '', tittle_style2)
        ws.write(5, 1, 'Code', tittle_bold_center_style_bottom)
        ws.write(5, 2, 'Account', tittle_bold_center_style_bottom)
        ws.write(5, 4, 'Descriptions', tittle_bold_center_style_bottom)
        ws.write(5, 6, data['form']['1']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 8, data['form']['2']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 10, data['form']['3']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 12, data['form']['4']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 14, data['form']['5']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 16, data['form']['6']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 18, data['form']['7']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 20, data['form']['8']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 22, data['form']['9']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 24, data['form']['10']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 26, data['form']['11']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 28, data['form']['12']['date'], tittle_bold_center_style_bottom)
        ws.write(5, 30, '', tittle_bold_center_style_bottom)
        #ws.write(5, 32, 'BUDGET', tittle_bold_center_style_bottom)
        #ws.write(5, 34, 'BUDGET', tittle_bold_center_style_bottom)
        #ws.write(6, 5, '', tittle_style2)
        for a in [0,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31]:
            ws.write(5, a, '', tittle_style2)
        #ws.write(5, 31, '', tittle_style_closed)
#        for b in [6,8,10,12,14,16,18,20,22,24,26,28,30]:
#            ws.write(5, b, '', tittle_bold_center_style_bottom)
            
        self.xls_write_row(ws, None, data, parser, 0, row_hdr4, tittle_left_style)#Company
        self.xls_write_row(ws, None, data, parser, 1, row_hdr5, tittle_left_style)#Budget Rolling
        self.xls_write_row(ws, None, data, parser, 2, row_hdr6, tittle_left_italic_style)#As of
        self.xls_write_row(ws, None, data, parser, 3, row_hdr7, tittle_left_style)#Space
        #self.xls_write_row(ws, None, data, parser, 5, row_hdr10, tittle_bold_center_style_top)#header space
        #self.xls_write_row(ws, None, data, parser, 6, row_hdr8, tittle_bold_center_style_bottom)#header
        #self.xls_write_row(ws, None, data, parser, 6, row_hdr7, tittle_style2)#space white
        #self.xls_write_row(ws, None, data, parser, 6, row_hdr9, tittle_bold_center_style)#state
        
        row_count = 6
        ws.horz_split_pos = row_count
        
        
        #IF WITH DEPARTMENTstr(number) + '.' + str(subnumber) + ' '*i['level'] +  i['name']
        if len(parser._get_department(data))>0:
            val = False
            for dep in parser._get_department(data):
                self.xls_write_row(ws, dep, data, parser, row_count, row_hdr_dep, tittle_style_closed_dep)
                row_count += 1
                self.xls_write_row(ws, None, data, parser, row_count, row_hdr7, tittle_style_closed)
                row_count += 1
                number2=0
                subnumber2=0
                for i in parser.get_data(data):
                    if i['type'] == 'view':
                        style = row_bold_style
                    else:
                        style = row_normal_style
                    if data['form']['without_zero']:
                        if i['balance'] >= 0.00 and i['type'] == 'view':
                            number2 += 1
                            subnumber2 = 0
                            
                            for a in [0,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]:
                                ws.write(row_count, a, '', tittle_style2)
                            ws.write(row_count, 1, i['code'], style)
                            ws.write(row_count, 2, str(number2) + '. ' + i['name'], style)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            
                            row_count += 1
                            
                            
                        elif i['balance'] >= 0.00 and i['type'] == 'normal':
                            subnumber2 += 1
                            for a in [0,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                ws.write(row_count, a, '', tittle_style2)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            ws.write(row_count, 1, i['code'], style)
                            ws.write(row_count, 2, ' '*i['level'] + str(number2) + '.' + str(subnumber2) + ' '*i['level'] + i['name'], style)
                            ws.write(row_count, 4, 'Budget :', style_bold)

                            #####################NEW############################
                            col = 6
                            for val in parser.get_account_amount(data, i):
                                ws.write(row_count, col, val[1], style)
                                ws.write(row_count+1, col, val[3], style)
                                
                                cell1=xlwt.Utils.rowcol_to_cell(row_count,col)
                                cell2=xlwt.Utils.rowcol_to_cell(row_count+1,col)
                                formula_under_over = "%s-%s"%(cell1,cell2)
                                
                                ws.write(row_count+2,col,xlwt.Formula(formula_under_over), style_under)
                                                            
                                col += 2
                                
                                
                            ##########TOTAL###########
                            cell1=xlwt.Utils.rowcol_to_cell(row_count,6)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count,28)
                            formula_tot_budget = "SUM(%s:%s)"%(cell1,cell2)
                            
                            cell1=xlwt.Utils.rowcol_to_cell(row_count+1,6)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count+1,28)
                            formula_tot_actual = "SUM(%s:%s)"%(cell1,cell2)

                            cell1=xlwt.Utils.rowcol_to_cell(row_count+2,6)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count+2,28)
                            formula_tot_under_over = "SUM(%s:%s)"%(cell1,cell2)
                            
                            ws.write(row_count,30,xlwt.Formula(formula_tot_budget), style)
                            ws.write(row_count+1,30,xlwt.Formula(formula_tot_actual), style)
                            ws.write(row_count+2,30,xlwt.Formula(formula_tot_under_over), style_under)
                            
                            ##########################
                            row_count += 1
                            
                            ####################################################
                            
                            
                            for b in [0,1,2,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                ws.write(row_count, b, '', tittle_style2)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            ws.write(row_count, 4, 'Actual :', style_bold)
                            row_count += 1
                            #self.xls_write_row(ws, i, data, parser, row_count, row_loop_under, style_under)
                            for c in [0,1,2,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                ws.write(row_count, c, '', tittle_style2)
                            #ws.write(row_count, 31, '', tittle_style_closed)
                            ws.write(row_count, 4, 'Under/(Over) :', style_under_bold)
                            row_count += 1
                            ws.write(row_count, 2, '   '*i['level']+'Actual', style_italic_bold)
                            for e in [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]:
                                ws.write(row_count, e, '', tittle_style2)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            row_count += 1
                            
                            if data['form']['with_transaction'] and i['type'] == 'normal' and val:
                                
                                #for t in parser.get_transaction(data['form']['as_of_date'],i['id'],dep['id']):
                                for t in parser.get_detail(data, i, val[4]):
                                    ws.write(row_count, 2, '   '*i['level']+'- '+t[0], style)
                                    ws.write(row_count, 4, '', style)
                                    
                                    col_t   = 6
                                    
                                    for p in parser.get_all_period(data, i):
                                        amount_t    = 0.0
                                        if t[2] >= p[0] and t[2] <= p[1]:
                                            amount_t = t[1]
                                        ws.write(row_count, col_t, amount_t, style)
                                        col_t += 2
                                    cell1=xlwt.Utils.rowcol_to_cell(row_count,6)
                                    cell2=xlwt.Utils.rowcol_to_cell(row_count,28)
                                    formula_tot_detail = "SUM(%s:%s)"%(cell1,cell2)
                                    
                                    ws.write(row_count,30,xlwt.Formula(formula_tot_detail), style)
                                    
                                    for l in [0,1,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                        ws.write(row_count, l, '', style)
                                    ws.write(row_count, 31, '', tittle_style_closed)
                                    row_count += 1
                            #ws.write(row_count, 2, '   '*i['level']+'Budget (unutilized)', style_italic_bold)
                            for f in [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]:
                                ws.write(row_count, f, '', tittle_style2)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            row_count += 1
                            
                            col = 6
                            #ws.write(row_count, 2, '   '*i['level']+"- "+i['name'], style)
#                            for u in parser.get_budget_unutilize(data, i):
#                                ws.write(row_count, col, u[1], style)
#                                
#                                col += 2
                            for z in [0,1,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                ws.write(row_count, z, '', tittle_style2)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            row_count += 1
                    #ELSE WITH ZERO
                    else:
                        print "2222222222222222222222222222222"
                        if i['type'] == 'view':
                            for x in parser.get_account_amount(data, i):
                                print  "cccc"
                            number2 += 1
                            subnumber2 = 0
                            for a in [0,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]:
                                ws.write(row_count, a, '', tittle_style2)
                            ws.write(row_count, 1, i['code'], style)
                            ws.write(row_count, 2, str(number2) + '. ' + i['name'], style)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            row_count += 1
                        elif i['type'] == 'normal':
                            subnumber2 += 1
                            for a in [0,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                ws.write(row_count, a, '', tittle_style2)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            ws.write(row_count, 1, i['code'], style)
                            ws.write(row_count, 2, ' '*i['level'] + str(number2) + '.' + str(subnumber2) + ' '*i['level'] + i['name'], style)
                            ws.write(row_count, 4, 'Budget :', style_bold)

                            #####################NEW############################
                            col = 6
                            for val in parser.get_account_amount(data, i):
                                ws.write(row_count, col, val[1], style)
                                ws.write(row_count+1, col, val[3], style)
                                
                                cell1=xlwt.Utils.rowcol_to_cell(row_count,col)
                                cell2=xlwt.Utils.rowcol_to_cell(row_count+1,col)
                                formula_under_over = "%s-%s"%(cell1,cell2)
                                
                                ws.write(row_count+2,col,xlwt.Formula(formula_under_over), style_under)
                                                            
                                col += 2
                                
                                
                            ##########TOTAL###########
                            cell1=xlwt.Utils.rowcol_to_cell(row_count,6)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count,28)
                            formula_tot_budget = "SUM(%s:%s)"%(cell1,cell2)
                            
                            cell1=xlwt.Utils.rowcol_to_cell(row_count+1,6)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count+1,28)
                            formula_tot_actual = "SUM(%s:%s)"%(cell1,cell2)

                            cell1=xlwt.Utils.rowcol_to_cell(row_count+2,6)
                            cell2=xlwt.Utils.rowcol_to_cell(row_count+2,28)
                            formula_tot_under_over = "SUM(%s:%s)"%(cell1,cell2)
                            
                            ws.write(row_count,30,xlwt.Formula(formula_tot_budget), style)
                            ws.write(row_count+1,30,xlwt.Formula(formula_tot_actual), style)
                            ws.write(row_count+2,30,xlwt.Formula(formula_tot_under_over), style_under)
                            
                            ##########################
                            row_count += 1
                            
                            ####################################################
                            
                            
                            for b in [0,1,2,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                ws.write(row_count, b, '', tittle_style2)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            ws.write(row_count, 4, 'Actual :', style_bold)
                            row_count += 1
                            #self.xls_write_row(ws, i, data, parser, row_count, row_loop_under, style_under)
                            for c in [0,1,2,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                ws.write(row_count, c, '', tittle_style2)
                            #ws.write(row_count, 31, '', tittle_style_closed)
                            ws.write(row_count, 4, 'Under/(Over) :', style_under_bold)
                            row_count += 1
                            ws.write(row_count, 2, '   '*i['level']+'Actual', style_italic_bold)
                            for e in [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]:
                                ws.write(row_count, e, '', tittle_style2)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            row_count += 1
                            
                            if data['form']['with_transaction'] and i['type'] == 'normal' and val:
                                
                                #for t in parser.get_transaction(data['form']['as_of_date'],i['id'],dep['id']):
                                for t in parser.get_detail(data, i, val[4]):
                                    ws.write(row_count, 2, '   '*i['level']+'- '+t[0], style)
                                    ws.write(row_count, 4, '', style)
                                    
                                    col_t   = 6
                                    
                                    for p in parser.get_all_period(data, i):
                                        amount_t    = 0.0
                                        if t[2] >= p[0] and t[2] <= p[1]:
                                            amount_t = t[1]
                                        ws.write(row_count, col_t, amount_t, style)
                                        col_t += 2
                                    cell1=xlwt.Utils.rowcol_to_cell(row_count,6)
                                    cell2=xlwt.Utils.rowcol_to_cell(row_count,28)
                                    formula_tot_detail = "SUM(%s:%s)"%(cell1,cell2)
                                    
                                    ws.write(row_count,30,xlwt.Formula(formula_tot_detail), style)
                                    
                                    for l in [0,1,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                        ws.write(row_count, l, '', style)
                                    ws.write(row_count, 31, '', tittle_style_closed)
                                    row_count += 1
                            #ws.write(row_count, 2, '   '*i['level']+'Budget (unutilized)', style_italic_bold)
                            for f in [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]:
                                ws.write(row_count, f, '', tittle_style2)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            row_count += 1
                            
                            col = 6
                            #ws.write(row_count, 2, '   '*i['level']+"- "+i['name'], style)
#                            for u in parser.get_budget_unutilize(data, i):
#                                ws.write(row_count, col, u[1], style)
#                                
#                                col += 2
                            for z in [0,1,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                ws.write(row_count, z, '', tittle_style2)
                            ws.write(row_count, 31, '', tittle_style_closed)
                            row_count += 1
        else:
            #ELSE WITHOUT DEPARTMENT AND WITHOUT ZERO
            self.xls_write_row(ws, None, data, parser, row_count, row_hdr7, tittle_style_closed)
            row_count += 1
            number=0
            subnumber=0
            budgets_levels = {}
            for i in parser.get_data(data):
                if i['type'] == 'view':
                    style = row_bold_style
                else:
                    style = row_normal_style
                if data['form']['without_zero']:
                    if  i['balance'] >= 0.00 and i['type'] == 'view':
                        number += 1
                        subnumber = 0
                        for a in [0,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]:
                            ws.write(row_count, a, '', tittle_style2)
                        ws.write(row_count, 1, i['code'], style)
                        ws.write(row_count, 2, str(number) + '. ' + i['name'], style)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        row_count += 1
                    elif i['balance'] >= 0.00 and i['type'] == 'normal':
                        subnumber += 1
                        for a in [0,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                            ws.write(row_count, a, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        ws.write(row_count, 1, i['code'], style)
                        ws.write(row_count, 2, ' '*i['level'] + str(number) + '.' + str(subnumber) + ' '*i['level'] + i['name'], style)
                        ws.write(row_count, 4, 'Budget :', style_bold)
                        ws.write(row_count, 6, parser.get_period(as_of, data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 8, parser.get_period(as_of, data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 10, parser.get_period(as_of, data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 12, parser.get_period(as_of, data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 14, parser.get_period(as_of, data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 16, parser.get_period(as_of, data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 18, parser.get_period(as_of, data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 20, parser.get_period(as_of, data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 22, parser.get_period(as_of, data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 24, parser.get_period(as_of, data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 26, parser.get_period(as_of, data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 28, parser.get_period(as_of, data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], False), style)
                        total_budget = parser.get_period_budget_total(data['form']['fiscalyear_id'],data['form']['as_of_date'],i['id'], i['type'])
                        ws.write(row_count, 30, total_budget, style)
                        row_count += 1
                        #ws.write(row_count, 20, parser.get_period(as_of, data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], False), tittle_bold_center_style_bottom)
                        #self.xls_write_row(ws, i, data, parser, row_count, row_loop_actual, style)
                        for b in [0,1,2,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                            ws.write(row_count, b, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        ws.write(row_count, 4, 'Actual :', style_bold)
                        ws.write(row_count, 6, parser.get_period_actual(as_of, data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 8, parser.get_period_actual(as_of, data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 10, parser.get_period_actual(as_of, data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 12, parser.get_period_actual(as_of, data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 14, parser.get_period_actual(as_of, data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 16, parser.get_period_actual(as_of, data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 18, parser.get_period_actual(as_of, data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 20, parser.get_period_actual(as_of, data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 22, parser.get_period_actual(as_of, data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 24, parser.get_period_actual(as_of, data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 26, parser.get_period_actual(as_of, data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 28, parser.get_period_actual(as_of, data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], False), style)
                        total_actual = parser.get_period_actual_total(data['form']['fiscalyear_id'],data['form']['as_of_date'],i['id'], i['type'],)
                        ws.write(row_count, 30, total_actual, style)
                        row_count += 1
                        #self.xls_write_row(ws, i, data, parser, row_count, row_loop_under, style_under)
                        for c in [0,1,2,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                            ws.write(row_count, c, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        ws.write(row_count, 4, 'Under/(Over) :', style_under_bold)
                        ws.write(row_count, 6, parser.get_period_under(as_of, data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 8, parser.get_period_under(as_of, data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 10, parser.get_period_under(as_of, data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 12, parser.get_period_under(as_of, data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 14, parser.get_period_under(as_of, data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 16, parser.get_period_under(as_of, data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 18, parser.get_period_under(as_of, data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 20, parser.get_period_under(as_of, data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 22, parser.get_period_under(as_of, data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 24, parser.get_period_under(as_of, data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 26, parser.get_period_under(as_of, data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 28, parser.get_period_under(as_of, data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 30, (total_budget-total_actual), style_under)
                        row_count += 1
                        ws.write(row_count, 2, '   '*i['level']+'Actual', style_italic_bold)
                        for e in [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]:
                            ws.write(row_count, e, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        row_count += 1
                        if data['form']['with_transaction'] and i['type'] == 'normal':
                            for t in parser.get_transaction(data['form']['as_of_date'],i['id'],False):
                                actual_1 = parser.get_transaction_period(as_of,i['id'], data['form']['1']['start'], data['form']['1']['end'], t['id'],) 
                                actual_2 = parser.get_transaction_period(as_of,i['id'], data['form']['2']['start'], data['form']['2']['end'], t['id'],) 
                                actual_3 = parser.get_transaction_period(as_of,i['id'], data['form']['3']['start'], data['form']['3']['end'], t['id'],) 
                                actual_4 = parser.get_transaction_period(as_of,i['id'], data['form']['4']['start'], data['form']['4']['end'], t['id'],) 
                                actual_5 = parser.get_transaction_period(as_of,i['id'], data['form']['5']['start'], data['form']['5']['end'], t['id'],) 
                                actual_6 = parser.get_transaction_period(as_of,i['id'], data['form']['6']['start'], data['form']['6']['end'], t['id'],) 
                                actual_7 = parser.get_transaction_period(as_of,i['id'], data['form']['7']['start'], data['form']['7']['end'], t['id'],) 
                                actual_8 = parser.get_transaction_period(as_of,i['id'], data['form']['8']['start'], data['form']['8']['end'], t['id'],) 
                                actual_9 = parser.get_transaction_period(as_of,i['id'], data['form']['9']['start'], data['form']['9']['end'], t['id'],) 
                                actual_10 = parser.get_transaction_period(as_of,i['id'], data['form']['10']['start'], data['form']['10']['end'], t['id'],) 
                                actual_11 = parser.get_transaction_period(as_of,i['id'], data['form']['11']['start'], data['form']['11']['end'], t['id'],) 
                                actual_12 = parser.get_transaction_period(as_of,i['id'], data['form']['12']['start'], data['form']['12']['end'], t['id'],)
                                #--------
                                ws.write(row_count, 2, '   '*i['level']+'- '+t.name, style)
                                ws.write(row_count, 4, '', style)
                                ws.write(row_count, 6, actual_1, style)
                                ws.write(row_count, 8, actual_2, style)
                                ws.write(row_count, 10, actual_3, style)
                                ws.write(row_count, 12, actual_4, style)
                                ws.write(row_count, 14, actual_5, style)
                                ws.write(row_count, 16, actual_6, style)
                                ws.write(row_count, 18, actual_7, style)
                                ws.write(row_count, 20, actual_8, style)
                                ws.write(row_count, 22, actual_9, style)
                                ws.write(row_count, 24, actual_10, style)
                                ws.write(row_count, 26, actual_11, style)
                                ws.write(row_count, 28, actual_12, style)
                                actual_total = actual_1 + actual_2 + actual_3 + actual_4 + actual_5 + actual_6 + actual_7 + actual_8 + actual_9 + actual_10 + actual_11 + actual_12
                                ws.write(row_count, 30, actual_total, style)
                                for l in [0,1,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                    ws.write(row_count, l, '', style)
                                ws.write(row_count, 31, '', tittle_style_closed)
                                row_count += 1
                        ws.write(row_count, 2, '   '*i['level']+'Budget (unutilized)', style_italic_bold)
                        for f in [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]:
                            ws.write(row_count, f, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        row_count += 1
                        unutulized_1 = parser.get_period_unutilized(as_of,data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_2 = parser.get_period_unutilized(as_of,data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_3 = parser.get_period_unutilized(as_of,data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_4 = parser.get_period_unutilized(as_of,data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_5 = parser.get_period_unutilized(as_of,data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_6 = parser.get_period_unutilized(as_of,data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_7 = parser.get_period_unutilized(as_of,data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_8 = parser.get_period_unutilized(as_of,data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_9 = parser.get_period_unutilized(as_of,data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_10 = parser.get_period_unutilized(as_of,data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_11 = parser.get_period_unutilized(as_of,data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_12 = parser.get_period_unutilized(as_of,data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['1']['end'], i['type'], i['item'])
                        ws.write(row_count, 2, '   '*i['level']+'- %s'%parser.get_desc_budget_line(as_of,data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item']), style)
                        for z in [0,1,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                            ws.write(row_count, z, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        ws.write(row_count, 6, unutulized_1, style)
                        ws.write(row_count, 8, unutulized_2, style)
                        ws.write(row_count, 10, unutulized_3, style)
                        ws.write(row_count, 12, unutulized_4, style)
                        ws.write(row_count, 14, unutulized_5, style)
                        ws.write(row_count, 16, unutulized_6, style)
                        ws.write(row_count, 18, unutulized_7, style)
                        ws.write(row_count, 20, unutulized_8, style)
                        ws.write(row_count, 22, unutulized_9, style)
                        ws.write(row_count, 24, unutulized_10, style)
                        ws.write(row_count, 26, unutulized_11, style)
                        ws.write(row_count, 28, unutulized_12, style)
                        unutilized_total = unutulized_1 + unutulized_2 + unutulized_3 + unutulized_4 + unutulized_5 + unutulized_6 + unutulized_7 + unutulized_8 + unutulized_9 + unutulized_10 + unutulized_11 + unutulized_12
                        ws.write(row_count, 30, unutilized_total, style)
                        row_count += 1
                        self.xls_write_row(ws, None, data, parser, row_count, row_hdr7, tittle_style_closed)
                        row_count += 1
                #ELSE WITH ZERO AND WITHOUT DEPARTMENT
                else:
                    if i['type'] == 'view':
                        number += 1
                        subnumber = 0
                        for a in [0,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]:
                            ws.write(row_count, a, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        ws.write(row_count, 1, i['code'], style)
                        ws.write(row_count, 2, str(number) + '. ' + i['name'], style)
                        row_count += 1
                    elif i['type'] == 'normal':
                        subnumber += 1
                        for a in [0,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                            ws.write(row_count, a, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        #self.xls_write_row(ws, i, data, parser, row_count, row_loop, style)
                        ws.write(row_count, 1, i['code'], style)
                        ws.write(row_count, 2, ' '*i['level'] + str(number) + '.' + str(subnumber) + ' '*i['level'] + i['name'], style)
                        ws.write(row_count, 4, 'Budget :', style_bold)
                        ws.write(row_count, 6, parser.get_period(as_of, data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 8, parser.get_period(as_of, data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 10, parser.get_period(as_of, data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 12, parser.get_period(as_of, data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 14, parser.get_period(as_of, data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 16, parser.get_period(as_of, data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 18, parser.get_period(as_of, data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 20, parser.get_period(as_of, data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 22, parser.get_period(as_of, data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 24, parser.get_period(as_of, data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 26, parser.get_period(as_of, data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 28, parser.get_period(as_of, data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], False), style)
                        total_budget = parser.get_period_budget_total(data['form']['fiscalyear_id'],data['form']['as_of_date'],i['id'], i['type'])
                        ws.write(row_count, 30, total_budget, style)
                        row_count += 1
                        #ws.write(row_count, 20, parser.get_period(as_of, data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], False), tittle_bold_center_style_bottom)
                        #self.xls_write_row(ws, i, data, parser, row_count, row_loop_actual, style)
                        for b in [0,1,2,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                            ws.write(row_count, b, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        ws.write(row_count, 4, 'Actual :', style_bold)
                        ws.write(row_count, 6, parser.get_period_actual(as_of, data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 8, parser.get_period_actual(as_of, data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 10, parser.get_period_actual(as_of, data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 12, parser.get_period_actual(as_of, data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 14, parser.get_period_actual(as_of, data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 16, parser.get_period_actual(as_of, data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 18, parser.get_period_actual(as_of, data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 20, parser.get_period_actual(as_of, data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 22, parser.get_period_actual(as_of, data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 24, parser.get_period_actual(as_of, data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 26, parser.get_period_actual(as_of, data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], False), style)
                        ws.write(row_count, 28, parser.get_period_actual(as_of, data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], False), style)
                        total_actual = parser.get_period_actual_total(data['form']['fiscalyear_id'],data['form']['as_of_date'],i['id'], i['type'],)
                        ws.write(row_count, 30, total_actual, style)
                        row_count += 1
                        #self.xls_write_row(ws, i, data, parser, row_count, row_loop_under, style_under)
                        for c in [0,1,2,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                            ws.write(row_count, c, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        ws.write(row_count, 4, 'Under/(Over) :', style_under_bold)
                        ws.write(row_count, 6, parser.get_period_under(as_of, data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 8, parser.get_period_under(as_of, data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['2']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 10, parser.get_period_under(as_of, data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['3']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 12, parser.get_period_under(as_of, data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['4']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 14, parser.get_period_under(as_of, data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['5']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 16, parser.get_period_under(as_of, data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['6']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 18, parser.get_period_under(as_of, data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['7']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 20, parser.get_period_under(as_of, data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['8']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 22, parser.get_period_under(as_of, data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['9']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 24, parser.get_period_under(as_of, data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['10']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 26, parser.get_period_under(as_of, data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['11']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 28, parser.get_period_under(as_of, data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['12']['end'], i['type'], i['item'], False), style_under)
                        ws.write(row_count, 30, (total_budget-total_actual), style_under)
                        row_count += 1
                        ws.write(row_count, 2, '   '*i['level']+'Actual', style_italic_bold)
                        for e in [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]:
                            ws.write(row_count, e, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        row_count += 1
                        if data['form']['with_transaction'] and i['type'] == 'normal':
                            for t in parser.get_transaction(data['form']['as_of_date'],i['id'],False):
                                actual_1 = parser.get_transaction_period(as_of,i['id'], data['form']['1']['start'], data['form']['1']['end'], t['id'],) 
                                actual_2 = parser.get_transaction_period(as_of,i['id'], data['form']['2']['start'], data['form']['2']['end'], t['id'],) 
                                actual_3 = parser.get_transaction_period(as_of,i['id'], data['form']['3']['start'], data['form']['3']['end'], t['id'],) 
                                actual_4 = parser.get_transaction_period(as_of,i['id'], data['form']['4']['start'], data['form']['4']['end'], t['id'],) 
                                actual_5 = parser.get_transaction_period(as_of,i['id'], data['form']['5']['start'], data['form']['5']['end'], t['id'],) 
                                actual_6 = parser.get_transaction_period(as_of,i['id'], data['form']['6']['start'], data['form']['6']['end'], t['id'],) 
                                actual_7 = parser.get_transaction_period(as_of,i['id'], data['form']['7']['start'], data['form']['7']['end'], t['id'],) 
                                actual_8 = parser.get_transaction_period(as_of,i['id'], data['form']['8']['start'], data['form']['8']['end'], t['id'],) 
                                actual_9 = parser.get_transaction_period(as_of,i['id'], data['form']['9']['start'], data['form']['9']['end'], t['id'],) 
                                actual_10 = parser.get_transaction_period(as_of,i['id'], data['form']['10']['start'], data['form']['10']['end'], t['id'],) 
                                actual_11 = parser.get_transaction_period(as_of,i['id'], data['form']['11']['start'], data['form']['11']['end'], t['id'],) 
                                actual_12 = parser.get_transaction_period(as_of,i['id'], data['form']['12']['start'], data['form']['12']['end'], t['id'],)
                                #--------
                                ws.write(row_count, 2, '   '*i['level']+'- '+t.name, style)
                                ws.write(row_count, 4, '', style)
                                ws.write(row_count, 6, actual_1, style)
                                ws.write(row_count, 8, actual_2, style)
                                ws.write(row_count, 10, actual_3, style)
                                ws.write(row_count, 12, actual_4, style)
                                ws.write(row_count, 14, actual_5, style)
                                ws.write(row_count, 16, actual_6, style)
                                ws.write(row_count, 18, actual_7, style)
                                ws.write(row_count, 20, actual_8, style)
                                ws.write(row_count, 22, actual_9, style)
                                ws.write(row_count, 24, actual_10, style)
                                ws.write(row_count, 26, actual_11, style)
                                ws.write(row_count, 28, actual_12, style)
                                actual_total = actual_1 + actual_2 + actual_3 + actual_4 + actual_5 + actual_6 + actual_7 + actual_8 + actual_9 + actual_10 + actual_11 + actual_12
                                ws.write(row_count, 30, actual_total, style)
                                for l in [0,1,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                                    ws.write(row_count, l, '', style)
                                ws.write(row_count, 31, '', tittle_style_closed)
                                row_count += 1
                        ws.write(row_count, 2, '   '*i['level']+'Budget (unutilized)', style_italic_bold)
                        for f in [0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]:
                            ws.write(row_count, f, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        row_count += 1
                        unutulized_1 = parser.get_period_unutilized(as_of,data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_2 = parser.get_period_unutilized(as_of,data['form']['2']['id'], i['id'], data['form']['2']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_3 = parser.get_period_unutilized(as_of,data['form']['3']['id'], i['id'], data['form']['3']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_4 = parser.get_period_unutilized(as_of,data['form']['4']['id'], i['id'], data['form']['4']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_5 = parser.get_period_unutilized(as_of,data['form']['5']['id'], i['id'], data['form']['5']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_6 = parser.get_period_unutilized(as_of,data['form']['6']['id'], i['id'], data['form']['6']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_7 = parser.get_period_unutilized(as_of,data['form']['7']['id'], i['id'], data['form']['7']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_8 = parser.get_period_unutilized(as_of,data['form']['8']['id'], i['id'], data['form']['8']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_9 = parser.get_period_unutilized(as_of,data['form']['9']['id'], i['id'], data['form']['9']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_10 = parser.get_period_unutilized(as_of,data['form']['10']['id'], i['id'], data['form']['10']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_11 = parser.get_period_unutilized(as_of,data['form']['11']['id'], i['id'], data['form']['11']['start'], data['form']['1']['end'], i['type'], i['item'])
                        unutulized_12 = parser.get_period_unutilized(as_of,data['form']['12']['id'], i['id'], data['form']['12']['start'], data['form']['1']['end'], i['type'], i['item'])
                        ws.write(row_count, 2, '   '*i['level']+'- %s'%parser.get_desc_budget_line(as_of,data['form']['1']['id'], i['id'], data['form']['1']['start'], data['form']['1']['end'], i['type'], i['item']), style)
                        for z in [0,1,3,5,7,9,11,13,15,17,19,21,23,25,27,29]:
                            ws.write(row_count, z, '', tittle_style2)
                        ws.write(row_count, 31, '', tittle_style_closed)
                        ws.write(row_count, 6, unutulized_1, style)
                        ws.write(row_count, 8, unutulized_2, style)
                        ws.write(row_count, 10, unutulized_3, style)
                        ws.write(row_count, 12, unutulized_4, style)
                        ws.write(row_count, 14, unutulized_5, style)
                        ws.write(row_count, 16, unutulized_6, style)
                        ws.write(row_count, 18, unutulized_7, style)
                        ws.write(row_count, 20, unutulized_8, style)
                        ws.write(row_count, 22, unutulized_9, style)
                        ws.write(row_count, 24, unutulized_10, style)
                        ws.write(row_count, 26, unutulized_11, style)
                        ws.write(row_count, 28, unutulized_12, style)
                        unutilized_total = unutulized_1 + unutulized_2 + unutulized_3 + unutulized_4 + unutulized_5 + unutulized_6 + unutulized_7 + unutulized_8 + unutulized_9 + unutulized_10 + unutulized_11 + unutulized_12
                        ws.write(row_count, 30, unutilized_total, style)
                        row_count += 1
                        self.xls_write_row(ws, None, data, parser, row_count, row_hdr7, tittle_style_closed)
                        row_count += 1
            self.xls_write_row(ws, None, data, parser, row_count, row_hdr7, tittle_style_closed_bottom)
            row_count += 1
        pass

budget_detail_xls(
        'report.budget.detail.xls',
        'ad_budget.item',
        'addons/ad_budget_detail/report/budget_detail.mako',
        parser=budget_detail,
        header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
