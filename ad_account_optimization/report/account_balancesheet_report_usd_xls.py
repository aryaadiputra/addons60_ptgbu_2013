# -*- coding: utf-8 -*-
# Copyright 2010 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import time
import xlwt
from report_engine_xls import report_xls
from ad_account_optimization.report.account_balance_sheet import report_balancesheet_horizontal
import cStringIO

class account_balance_report_usd_xls(report_xls):
    
    def _display_filter(self, parser, data):
        filter_mode = parser._get_filter(data)
        filter_string = filter_mode
        if filter_mode == 'Date':
            filter_string = '%s -> %s' % (parser.formatLang(parser._get_start_date(data), date=True),
                                          parser.formatLang(parser._get_end_date(data), date=True))
        elif filter_mode == 'Periods':
            filter_string = '%s -> %s' % (parser.get_start_period(data),
                                 parser.get_end_period(data))

        moves_string = parser._get_target_move(data)
        display_acct_string = ''
        if data['form']['display_account'] == 'bal_all':
            display_acct_string = 'All'
        elif data['form']['display_account'] == 'bal_movement':
            display_acct_string = 'With movements'
        else:
            display_acct_string = 'With balance is not equal to 0'

        return 'Display Account: %s, Filter By: %s, Target Moves: %s' % (display_acct_string, filter_string, moves_string)

    def _display_fiscalyear(self, parser, data):
        k = parser._get_fiscalyear(data)
        if k:
            k = 'Fiscal Year: %s' % (k)
        return k
    
    def _sum_currency_amount(self, parser, cur):
        k = parser._sum_currency_amount_account(cur)
        if k:
            k = k
        return k
    
    def _display_balance(self, name, balance):
        #print "xxxx",name
        if name == 'Net Profit':
            bl = 0
        else:
            if balance > 0:
                bl = abs(balance)
            elif balance < 0:
                bl = balance
            else:
                bl = 0
        return bl
    
    def _display_code(self, code):
        if code == 'Net Profit':
            code = ''
        else:
            code = code
        return code
    
    def _display_net(self, net):
        if net > 0:
            net = 'Net Profit'
        elif net < 0:
            net = 'Net Loss'
        else:
            net = ''
        return net
    
    ## Modules Begin
    def _size_col(sheet, col):
        return sheet.col_width(col)
     
    def _size_row(sheet, row):
        return sheet.row_height(row)
        ## Modules End    
    
    def generate_xls_report(self, parser, data, obj, wb):
        if data['form']['currency_rate'] == 1:
            #print parser._sum_currency_amount_account(1)
            c = parser.localcontext['company']
            ws = wb.add_sheet(('Balance Sheet- %s - %s' % (c.partner_id.ref, c.currency_id.name))[:31])
            ws.panes_frozen = True
            ws.remove_splits = True
            ws.portrait = 0 # Landscape
            ws.fit_width_to_pages = 1
            judul = "BALANCE SHEET REPORT"
    
            cols_specs = [
                    # Headers data
                    ('Title', 8, 0, 'text',
                        lambda x, d, p: judul),
                    ('Kosong', 8, 0, 'text',
                        lambda x, d, p: ""),
                    ('Fiscal Year', 4, 0, 'text',
                        lambda x, d, p: self._display_fiscalyear(p, d)),
                    ('Create Date', 4, 0, 'text',
                        lambda x, d, p: 'Create date: ' + p.formatLang(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),date_time = True)),
                    ('Filter', 8, 0, 'text',
                        lambda x, d, p: self._display_filter(p, d)),
                    ('Currency', 8, 0, 'number',
                        lambda x, d, p: 'Currency Rate IDR: ' + p.formatLang(self._sum_currency_amount(p, 1))),
                    # Balance column
                    ('Asset Code', 1, 67, 'text',
                        lambda x, d, p: x['code1']),
                    ('Assets Account', 1, 270, 'text',
                        lambda x, d, p: '  '*x['level1'] + x['name1']),
                    ('Asset Balance', 1, 80, 'number',
                        lambda x, d, p: x['balance_dual1']),
                    ('Asset Balance IDR', 1, 120, 'number',
                        lambda x, d, p: parser._sum_currency_amount_account(x['balance_dual1'])),
                    ('Liab. Code', 1, 67, 'text',
                        lambda x, d, p: self._display_code(x['code'])),
                    ('Liabilities and Equities Account', 1, 270, 'text',
                        lambda x, d, p: '  '*x['level'] + self._display_code(x['name'])),
                    ('Liab. Balance', 1, 80, 'number',
                        lambda x, d, p: self._display_balance(x['name'],x['balance_dual'])),
                    ('Liab. Balance IDR', 1, 120, 'number',
                        lambda x, d, p: parser._sum_currency_amount_account(self._display_balance(x['name'],x['balance_dual']))),
            ]
    
            row_hdr0 = self.xls_row_template(cols_specs, ['Title'])
            row_hdr1 = self.xls_row_template(cols_specs, ['Kosong'])
            row_hdr2 = self.xls_row_template(cols_specs, ['Fiscal Year', 'Create Date'])
            row_hdr3 = self.xls_row_template(cols_specs, ['Filter'])
            row_hdr4 = self.xls_row_template(cols_specs, ['Currency'])
            row_hdr5 = self.xls_row_template(cols_specs, ['Kosong'])
            row_balance = self.xls_row_template(cols_specs,
                    ['Asset Code','Assets Account','Asset Balance','Asset Balance IDR','Liab. Code','Liabilities and Equities Account','Liab. Balance','Liab. Balance IDR'])
    
            ## Style variable Begin
            hdr_style = xlwt.easyxf('pattern: pattern solid, fore_color gray25;')
            row_normal_style=  xlwt.easyxf(num_format_str='#,##0.00;(#,##0.00)')
            row_bold_style = xlwt.easyxf('font: bold on;',num_format_str='#,##0.00;(#,##0.00)')
    
            tittle_style = xlwt.easyxf('font: height 240, name Arial Black, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            subtittle_left_style = xlwt.easyxf('font: height 240, name Arial, colour_index brown, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            subtittle_right_style = xlwt.easyxf('font: height 240, name Arial, colour_index brown, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            subtittle_top_and_bottom_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            blank_style = xlwt.easyxf('font: height 650, name Arial, colour_index brown, bold off; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            normal_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off; align: wrap on, vert centre, horiz left;')
            total_style = xlwt.easyxf('font: height 240, name Arial, colour_index brown, bold on, italic on; align: wrap on, vert centre;', num_format_str='#,##0.00;(#,##0.00)')
            ## Style variable End
    
            # Write headers
            self.xls_write_row(ws, None, data, parser, 0, row_hdr0, tittle_style)
            self.xls_write_row(ws, None, data, parser, 1, row_hdr1, blank_style)
            self.xls_write_row(ws, None, data, parser, 2, row_hdr2, subtittle_left_style)
            self.xls_write_row(ws, None, data, parser, 3, row_hdr3, hdr_style)
            self.xls_write_row(ws, None, data, parser, 4, row_hdr4, hdr_style)
            self.xls_write_row(ws, None, data, parser, 5, row_hdr1, blank_style)
            self.xls_write_row_header(ws, 6, row_balance, hdr_style, set_column_size=True)
    
            row_count = 7
            ws.horz_split_pos = row_count
     
            c = parser.get_data(data)
            total = {
                     'tot_asset':0,
                     'tot_lia':0,
                     'tot_asset_idr':0,
                     'tot_lia_idr':0,
                     }
            for a in parser.get_lines():
                if a['level1'] <> 2:
                    style = row_normal_style
                else:
                    #style = row_bold_style
                    style = row_normal_style
                    total['tot_asset'] += a['balance_dual1']
                    total['tot_asset_idr'] += parser._sum_currency_amount_account(a['balance_dual1'])
                    
                if a['level'] <> 2:
                    style = row_normal_style
                else:
                    #style = row_bold_style
                    style = row_normal_style
                    total['tot_lia'] += a['balance_dual']
                    total['tot_lia_idr'] += parser._sum_currency_amount_account(a['balance_dual'])
                
                self.xls_write_row(ws, a, data, parser, row_count, row_balance, style)
                row_count += 1          
            
    
            cols_specs = [
                    ('Label_Asset_Total', 2, 67, 'text',
                        lambda x, d, p: 'BALANCE ASSET'),
                    ('Label_Liabilities_Total', 2, 67, 'text',
                        lambda x, d, p: 'BALANCE LIABILITY AND EQUITY'),
                    # Row Total
                    ('Asset Total', 1, 67, 'number',
                        lambda x, d, p: x['tot_asset']),
                    ('Asset Total IDR', 1, 80, 'number',
                        lambda x, d, p: x['tot_asset_idr']),
                    ('Liabilities and Equities Total', 1, 67, 'number',
                        lambda x, d, p: x['tot_lia']),
                    ('Liabilities and Equities Total IDR', 1, 80, 'number',
                        lambda x, d, p: x['tot_lia_idr']),
            ]
            row_ftr1 = self.xls_row_template(cols_specs, ['Label_Asset_Total','Asset Total','Asset Total IDR','Label_Liabilities_Total', 'Liabilities and Equities Total', 'Liabilities and Equities Total IDR'])
    
            row_count += 1
            self.xls_write_row(ws, total, data, parser, row_count, row_ftr1, total_style)                  
            row_count += 1
        else:
            c = parser.localcontext['company']
            ws = wb.add_sheet(('Balance Sheet- %s - %s' % (c.partner_id.ref, c.currency_id.name))[:31])
            ws.panes_frozen = True
            ws.remove_splits = True
            ws.portrait = 0 # Landscape
            ws.fit_width_to_pages = 1
            judul = "BALANCE SHEET REPORT"
    
            cols_specs = [
                    # Headers data
                    ('Title', 6, 0, 'text',
                        lambda x, d, p: judul),
                    ('Kosong', 6, 0, 'text',
                        lambda x, d, p: ""),
                    ('Fiscal Year', 3, 0, 'text',
                        lambda x, d, p: self._display_fiscalyear(p, d)),
                    ('Create Date', 3, 0, 'text',
                        lambda x, d, p: 'Create date: ' + p.formatLang(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),date_time = True)),
                    ('Filter', 6, 0, 'text',
                        lambda x, d, p: self._display_filter(p, d)),
                    # Balance column
                    ('Asset Code', 1, 67, 'text',
                        lambda x, d, p: x['code1']),
                    ('Assets Account', 1, 270, 'text',
                        lambda x, d, p: '  '*x['level1'] + x['name1']),
                    ('Asset Balance', 1, 100, 'number',
                        lambda x, d, p: x['balance_dual1']),
                    ('Liab. Code', 1, 67, 'text',
                        lambda x, d, p: self._display_code(x['code'])),
                    ('Liabilities and Equities Account', 1, 270, 'text',
                        lambda x, d, p: '  '*x['level'] + self._display_code(x['name'])),
                    ('Liab. Balance', 1, 100, 'number',
                        lambda x, d, p: self._display_balance(x['name'],x['balance_dual'])),
            ]
    
            row_hdr0 = self.xls_row_template(cols_specs, ['Title'])
            row_hdr1 = self.xls_row_template(cols_specs, ['Kosong'])
            row_hdr2 = self.xls_row_template(cols_specs, ['Fiscal Year', 'Create Date'])
            row_hdr3 = self.xls_row_template(cols_specs, ['Filter'])
            row_hdr4 = self.xls_row_template(cols_specs, ['Kosong'])
            row_balance = self.xls_row_template(cols_specs,
                    ['Asset Code','Assets Account','Asset Balance','Liab. Code','Liabilities and Equities Account','Liab. Balance'])
    
            ## Style variable Begin
            hdr_style = xlwt.easyxf('pattern: pattern solid, fore_color gray25;')
            row_normal_style=  xlwt.easyxf(num_format_str='#,##0.00;(#,##0.00)')
            row_bold_style = xlwt.easyxf('font: bold on;',num_format_str='#,##0.00;(#,##0.00)')
    
            tittle_style = xlwt.easyxf('font: height 240, name Arial Black, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            subtittle_left_style = xlwt.easyxf('font: height 240, name Arial, colour_index brown, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            subtittle_right_style = xlwt.easyxf('font: height 240, name Arial, colour_index brown, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            subtittle_top_and_bottom_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            blank_style = xlwt.easyxf('font: height 650, name Arial, colour_index brown, bold off; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            normal_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold off; align: wrap on, vert centre, horiz left;')
            total_style = xlwt.easyxf('font: height 240, name Arial, colour_index brown, bold on, italic on; align: wrap on, vert centre;', num_format_str='#,##0.00;(#,##0.00)')
            ## Style variable End
    
            # Write headers
            self.xls_write_row(ws, None, data, parser, 0, row_hdr0, tittle_style)
            self.xls_write_row(ws, None, data, parser, 1, row_hdr1, blank_style)
            self.xls_write_row(ws, None, data, parser, 2, row_hdr2, subtittle_left_style)
            self.xls_write_row(ws, None, data, parser, 3, row_hdr3, hdr_style)
            self.xls_write_row(ws, None, data, parser, 4, row_hdr1, blank_style)
            self.xls_write_row_header(ws, 5, row_balance, hdr_style, set_column_size=True)
    
            row_count = 6
            ws.horz_split_pos = row_count
     
            c = parser.get_data(data)
            total = {
                     'tot_asset':0,
                     'tot_lia':0,
                     'tot_income':0,
                     'tot_expenses':0,
                     }
            for a in parser.get_lines():       
                
                if a['level1'] <> 2:
                    style = row_normal_style
                else:
                    #style = row_bold_style
                    style = row_normal_style
                    total['tot_asset'] += a['balance_dual1']
                    
                if a['level'] <> 2:
                    style = row_normal_style
                else:
                    #style = row_bold_style
                    style = row_normal_style
                    total['tot_lia'] += a['balance_dual']
                
                self.xls_write_row(ws, a, data, parser, row_count, row_balance, style)
                row_count += 1          
            #-------------------------------
            for w in parser.get_lines_another('income'):
                if w['type'] <> 'view': 
                    style = row_normal_style   
                    total['tot_income'] += w['balance_dual']
                else:
                    style = row_bold_style
            for e in parser.get_lines_another('expense'):
                if e['type'] <> 'view':
                    style = row_normal_style
                    total['tot_expenses'] += e['balance_dual']
                else:
                    style = row_bold_style
            #print "yyyyyyyyy",total['tot_income']+total['tot_expenses']
            #-------------------------------
            total['tot_net'] = abs(total['tot_income'])-abs(total['tot_expenses'])
            cols_specs = [
                    ('Kosong', 1, 0, 'text',
                        lambda x, d, p: ""),
                    ('Kosong', 1, 0, 'text',
                        lambda x, d, p: ""),
                    ('Kosong', 1, 0, 'text',
                        lambda x, d, p: ""),
                    ('Label_Net_Total', 1, 67, 'text',
                        lambda x, d, p: self._display_net(x['tot_net'])),
                    ('Kosong', 1, 0, 'text',
                        lambda x, d, p: ""),
                    # Row Total
                    ('Total', 1, 67, 'number',
                        lambda x, d, p: x['tot_net']),
            ]
            row_ftr1 = self.xls_row_template(cols_specs, ['Kosong','Kosong','Kosong','Label_Net_Total','Kosong', 'Total'])
            self.xls_write_row(ws, total, data, parser, row_count, row_ftr1, row_normal_style)                  
            row_count += 1
            #------------------------------
            cols_specs = [
                    ('Label_Asset_Total', 2, 67, 'text',
                        lambda x, d, p: 'BALANCE ASSET'),
                    ('Label_Liabilities_Total', 2, 67, 'text',
                        lambda x, d, p: 'BALANCE LIABILITY AND EQUITY'),
                    # Row Total
                    ('Asset Total', 1, 75, 'number',
                        lambda x, d, p: x['tot_asset']),
                    ('Liabilities and Equities Total', 1, 75, 'number',
                        lambda x, d, p: x['tot_lia']+x['tot_income']+x['tot_expenses']),
            ]
            row_ftr1 = self.xls_row_template(cols_specs, ['Label_Asset_Total','Asset Total','Label_Liabilities_Total', 'Liabilities and Equities Total'])
    
            row_count += 1
            self.xls_write_row(ws, total, data, parser, row_count, row_ftr1, row_bold_style)                  
            row_count += 1
        pass

account_balance_report_usd_xls(
        'report.account.balancesheet.usd.xls',
        'account.account',
        'addons/account/report/account_balance_sheet_horizontal.rml',
        parser=report_balancesheet_horizontal,
        header=False)


