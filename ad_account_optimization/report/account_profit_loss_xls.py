# -*- coding: utf-8 -*-
# Copyright 2010 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import time
import xlwt
from report_engine_xls import report_xls
from ad_account_optimization.report.account_profit_loss import report_pl_account_horizontal
import cStringIO

class account_profit_loss_xls(report_xls):
    """def create_source_xls(self, cr, uid, ids, data, report_xml, context=None):
        print("START: "+time.strftime("%Y-%m-%d %H:%M:%S"))

        if not context:
            context = {}
        context = context.copy()
        rml_parser = self.parser(cr, uid, self.name2, context=context)
        objs = self.getObjects(cr, uid, ids, context=context)
        rml_parser.set_context(objs, data, ids, 'xls')

        n = cStringIO.StringIO()
        wb = xlwt.Workbook(encoding='utf-8')
        self.generate_xls_report(rml_parser, data, rml_parser.localcontext['objects'], wb)
        wb.save(n)
        n.seek(0)

        print("END: "+time.strftime("%Y-%m-%d %H:%M:%S"))

        return (n.read(), 'xls')"""
    
    def _sum_currency_amount(self, parser, cur):
        k = parser._sum_currency_amount_account(cur)
        if k:
            k = k
        return k
    
    def _display_filter(self, parser, data):
        #print "parser",parser
        #print "data",data
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
    
    def _display_net(self, net):
        if net > 0:
            net = 'Net Profit'
        elif net < 0:
            net = 'Net Loss'
        else:
            net = ''
        return net
    
    def generate_xls_report(self, parser, data, obj, wb):
        #print "ssss",data['form']['currency_rate']
        if data['form']['currency_rate'] == 0:
            c = parser.localcontext['company']
            ws = wb.add_sheet(('Profit and Loss- %s - %s' % (c.partner_id.ref, c.currency_id.name))[:31])
            ws.panes_frozen = True
            ws.remove_splits = True
            ws.portrait = 0 # Landscape
            ws.fit_width_to_pages = 1
            cols_specs = [
                    # Headers data
                    ('Title', 3, 0, 'text',
                        lambda x, d, p: "PROFIT AND LOSS"),
                    ('Kosong', 3, 0, 'text',
                        lambda x, d, p: ""),
                    ('Fiscal Year', 2, 0, 'text',
                        lambda x, d, p: self._display_fiscalyear(p, d)),
                    ('Create Date', 1, 0, 'text',
                        lambda x, d, p: 'Create date: ' + p.formatLang(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),date_time = True)),
                    ('Filter', 3, 0, 'text',
                        lambda x, d, p: self._display_filter(p, d)),
                    # Expenses column
                     ('Code', 1, 67, 'text',
                        lambda x, d, p: x['code']),
                    ('Account', 1, 270, 'text',
                        lambda x, d, p: '  '*x['level'] + x['name']),
                    ('Balance', 1, 180, 'number',
                        lambda x, d, p: -x['balance']), 
            ]                 
    
            row_hdr0 = self.xls_row_template(cols_specs, ['Title'])
            row_hdr1 = self.xls_row_template(cols_specs, ['Kosong'])
            row_hdr2 = self.xls_row_template(cols_specs, ['Fiscal Year', 'Create Date'])
            row_hdr3 = self.xls_row_template(cols_specs, ['Filter'])
            row_hdr4 = self.xls_row_template(cols_specs, ['Kosong'])
            row_balance = self.xls_row_template(cols_specs,
                    ['Code','Account','Balance'])
            
            tittle_style = xlwt.easyxf('font: height 240, name Arial Black, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            hdr_style = xlwt.easyxf('pattern: pattern solid, fore_color gray25;')
            row_normal_style=  xlwt.easyxf(num_format_str='#,##0.00;(#,##0.00)')
            row_bold_style = xlwt.easyxf('font: bold on', num_format_str='#,##0.00;(#,##0.00)')
            blank_style = xlwt.easyxf('font: height 650, name Arial, colour_index brown, bold off; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            total_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold on, italic on; align: wrap on, vert centre;', num_format_str='#,##0.00;(#,##0.00)')
            subtittle_center_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold on; align: wrap on, vert centre; pattern: pattern solid, fore_color gray25;')
            subtittle_left_style = xlwt.easyxf('font: height 240, name Arial, colour_index brown, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            # Write headers
            self.xls_write_row(ws, None, data, parser, 0, row_hdr0, tittle_style)
            self.xls_write_row(ws, None, data, parser, 1, row_hdr1, blank_style)
            self.xls_write_row(ws, None, data, parser, 2, row_hdr2, subtittle_left_style)
            self.xls_write_row(ws, None, data, parser, 3, row_hdr3, hdr_style)
            self.xls_write_row(ws, None, data, parser, 4, row_hdr4, blank_style)
            self.xls_write_row_header(ws, 5, row_balance, hdr_style, set_column_size=True)
    
            row_count = 6
            ws.horz_split_pos = row_count
          
            parser.get_data(data)
            total = {
                     'tot_expenses':0,
                     'tot_income':0,
                     'tot_net':0,
            }
            
            #INCOME
            cols_specs = [
                     ('Code_i', 1, 67, 'text',
                        lambda x, d, p: 'Code'),
                     ('Income', 1, 67, 'text',
                        lambda x, d, p: 'Income'),
                     ('Balance_i', 1, 67, 'text',
                        lambda x, d, p: 'Balance'),      
                
            ]
            row_ftr2 = self.xls_row_template(cols_specs, ['Code_i','Income','Balance_i'])
            
            self.xls_write_row(ws, None, data, parser, row_count, row_ftr2, subtittle_center_style)                  
            row_count += 1 
            
            for w in parser.get_lines_another('income'):
                if w['type'] <> 'view': 
                    style = row_normal_style   
                    total['tot_income'] += w['balance']
                else:
                    style = row_bold_style
                        
                self.xls_write_row(ws, w, data, parser, row_count, row_balance, style)
                row_count += 1
            cols_specs = [
                    ('Label_Income_Total', 2, 67, 'text',
                        lambda x, d, p: 'TOTAL INCOME'),
                    # Row Total
                    ('Income Total', 1, 67, 'number',
                        lambda x, d, p: -x['tot_income']),
            ]
            row_ftr1 = self.xls_row_template(cols_specs, ['Label_Income_Total', 'Income Total'])
    
            self.xls_write_row(ws, total, data, parser, row_count, row_ftr1, row_bold_style)                  
            row_count += 1                 
            row_count += 1
            #EXPENSES
            cols_specs = [
                     ('Code_e', 1, 67, 'text',
                        lambda x, d, p: 'Code'),
                     ('Expenses', 1, 67, 'text',
                        lambda x, d, p: 'Expenses'),
                     ('Balance_e', 1, 67, 'text',
                        lambda x, d, p: 'Balance'),      
                
            ]
            row_ftr2 = self.xls_row_template(cols_specs, ['Code_e','Expenses','Balance_e'])
            
            self.xls_write_row(ws, None, data, parser, row_count, row_ftr2, subtittle_center_style)                  
            row_count += 1
            for e in parser.get_lines():
                #if parser._sum_currency_amount_account(e['balance']):
                if e['type'] <> 'view':
                    style = row_normal_style
                    total['tot_expenses'] += -e['balance']
                else:
                    style = row_bold_style        
                self.xls_write_row(ws, e, data, parser, row_count, row_balance, style)
                row_count += 1     
                 
            cols_specs = [
                    ('Label_Expenses_Total', 2, 67, 'text',
                        lambda x, d, p: 'TOTAL EXPENSES'),
                    # Row Total
                    ('Expenses Total', 1, 67, 'number',
                        lambda x, d, p: x['tot_expenses']),
            ]
            row_ftr1 = self.xls_row_template(cols_specs, ['Label_Expenses_Total', 'Expenses Total'])
    
            #row_count += 1
            self.xls_write_row(ws, total, data, parser, row_count, row_ftr1, row_bold_style)                  
            row_count += 1
            row_count += 1
            
            #NET PROFIT/LOSS
            #print "total['tot_income'] + total['tot_expenses']>>>>>>>>>>>>>>>>>>>>>", total['tot_income'], total['tot_expenses']
            
            total['tot_net'] = -total['tot_income'] + total['tot_expenses']
            cols_specs = [
                    ('Label_Net_Total', 2, 67, 'text',
                        lambda x, d, p: self._display_net(x['tot_net'])),
                    # Row Total
                    ('Total', 1, 67, 'number',
                        lambda x, d, p: x['tot_net']),
            ]
            row_ftr1 = self.xls_row_template(cols_specs, ['Label_Net_Total', 'Total'])
            self.xls_write_row(ws, total, data, parser, row_count, row_ftr1, row_bold_style)                  
            row_count += 1   
        else:
            c = parser.localcontext['company']
            ws = wb.add_sheet(('Profit and Loss- %s - %s' % (c.partner_id.ref, c.currency_id.name))[:31])
            ws.panes_frozen = True
            ws.remove_splits = True
            ws.portrait = 0 # Landscape
            ws.fit_width_to_pages = 1
            cols_specs = [
                    # Headers data
                    ('Title', 4, 0, 'text',
                        lambda x, d, p: "PROFIT AND LOSS"),
                    ('Kosong', 4, 0, 'text',
                        lambda x, d, p: ""),
                    ('Fiscal Year', 3, 0, 'text',
                        lambda x, d, p: self._display_fiscalyear(p, d)),
                    ('Create Date', 1, 0, 'text',
                        lambda x, d, p: 'Create date: ' + p.formatLang(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),date_time = True)),
                    ('Filter', 4, 0, 'text',
                        lambda x, d, p: self._display_filter(p, d)),
                    ('Currency', 4, 0, 'number',
                        lambda x, d, p: 'Currency Rate IDR: ' + p.formatLang(self._sum_currency_amount(p, 1))),
                    # Expenses column
                     ('Code', 1, 67, 'text',
                        lambda x, d, p: x['code']),
                    ('Account', 1, 270, 'text',
                        lambda x, d, p: '  '*x['level'] + x['name']),
                    ('Balance', 1, 130, 'number',
                        lambda x, d, p: -x['balance']),
                    ('Balance IDR', 1, 180, 'number',
                        lambda x, d, p: parser._sum_currency_amount_account(-x['balance']))
            ]                 
    
            row_hdr0 = self.xls_row_template(cols_specs, ['Title'])
            row_hdr1 = self.xls_row_template(cols_specs, ['Kosong'])
            row_hdr2 = self.xls_row_template(cols_specs, ['Fiscal Year', 'Create Date'])
            row_hdr3 = self.xls_row_template(cols_specs, ['Filter'])
            row_hdr4 = self.xls_row_template(cols_specs, ['Currency'])
            row_hdr5 = self.xls_row_template(cols_specs, ['Kosong'])
            row_balance = self.xls_row_template(cols_specs,
                    ['Code','Account','Balance','Balance IDR'])
            
            tittle_style = xlwt.easyxf('font: height 240, name Arial Black, colour_index black, bold on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            hdr_style = xlwt.easyxf('pattern: pattern solid, fore_color gray25;')
            row_normal_style=  xlwt.easyxf(num_format_str='#,##0.00;(#,##0.00)')
            row_bold_style = xlwt.easyxf('font: bold on', num_format_str='#,##0.00;(#,##0.00)')
            blank_style = xlwt.easyxf('font: height 650, name Arial, colour_index brown, bold off; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            total_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold on, italic on; align: wrap on, vert centre;', num_format_str='#,##0.00;(#,##0.00)')
            subtittle_left_style = xlwt.easyxf('font: height 240, name Arial, colour_index brown, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
            subtittle_center_style = xlwt.easyxf('font: height 240, name Arial, colour_index black, bold on; align: wrap on, vert centre; pattern: pattern solid, fore_color gray25;')
            # Write headers
            self.xls_write_row(ws, None, data, parser, 0, row_hdr0, tittle_style)
            self.xls_write_row(ws, None, data, parser, 1, row_hdr1, blank_style)
            self.xls_write_row(ws, None, data, parser, 2, row_hdr2, subtittle_left_style)
            self.xls_write_row(ws, None, data, parser, 3, row_hdr3, hdr_style)
            self.xls_write_row(ws, None, data, parser, 4, row_hdr4, hdr_style)
            self.xls_write_row(ws, None, data, parser, 5, row_hdr5, blank_style)
            self.xls_write_row_header(ws, 6, row_balance, hdr_style, set_column_size=True)
    
            row_count = 7
            ws.horz_split_pos = row_count
          
            parser.get_data(data)
            total = {
                     'tot_expenses':0,
                     'tot_income':0,
                     'tot_net':0,
                     'tot_expenses_idr':0,
                     'tot_income_idr':0,
                     'tot_net_idr':0,
            }
            
            #INCOME
            cols_specs = [
                     ('Code_i', 1, 67, 'text',
                        lambda x, d, p: 'Code'),
                     ('Income', 1, 67, 'text',
                        lambda x, d, p: 'Income'),
                     ('Balance_i', 1, 67, 'text',
                        lambda x, d, p: 'Balance'),
                     ('Balance_i_idr', 1, 67, 'text',
                        lambda x, d, p: 'Balance IDR')      
                
            ]
            row_ftr2 = self.xls_row_template(cols_specs, ['Code_i','Income','Balance_i','Balance_i_idr'])
            
            self.xls_write_row(ws, None, data, parser, row_count, row_ftr2, subtittle_center_style)                  
            row_count += 1 
            
            for w in parser.get_lines_another('income'):
                if w['level'] <> 2: 
                        style = row_normal_style
                else:
                        style = row_bold_style   
                        total['tot_income'] += w['balance']
                        total['tot_income_idr'] += parser._sum_currency_amount_account(w['balance'])
                        
                self.xls_write_row(ws, w, data, parser, row_count, row_balance, style)
                row_count += 1
            cols_specs = [
                    ('Label_Income_Total', 2, 67, 'text',
                        lambda x, d, p: 'TOTAL INCOME'),
                    # Row Total
                    ('Income Total', 1, 67, 'number',
                        lambda x, d, p: abs(x['tot_income']),),
                    ('Income IDR Total', 1, 67, 'number',
                        lambda x, d, p: parser._sum_currency_amount_account(abs(x['tot_income'])),),
            ]
            row_ftr1 = self.xls_row_template(cols_specs, ['Label_Income_Total', 'Income Total', 'Income IDR Total'])
    
            self.xls_write_row(ws, total, data, parser, row_count, row_ftr1, row_bold_style)                  
            row_count += 1                 
            row_count += 1
            #EXPENSES
            cols_specs = [
                     ('Code_e', 1, 67, 'text',
                        lambda x, d, p: 'Code'),
                     ('Expenses', 1, 67, 'text',
                        lambda x, d, p: 'Expenses'),
                     ('Balance_e', 1, 67, 'text',
                        lambda x, d, p: 'Balance'),
                     ('Balance_e_idr', 1, 67, 'text',
                        lambda x, d, p: 'Balance IDR'),      
                
            ]
            row_ftr2 = self.xls_row_template(cols_specs, ['Code_e','Expenses','Balance_e','Balance_e_idr'])
            
            self.xls_write_row(ws, None, data, parser, row_count, row_ftr2, subtittle_center_style)                  
            row_count += 1
            for e in parser.get_lines():
                if parser._sum_currency_amount_account(e['balance']):
                    if e['level'] <> 2:
                        style = row_normal_style
                    else:
                        style = row_bold_style
                        total['tot_expenses'] += e['balance']   
                        total['tot_expenses_idr'] += parser._sum_currency_amount_account(e['balance'])
                self.xls_write_row(ws, e, data, parser, row_count, row_balance, style)
                row_count += 1     
                 
            cols_specs = [
                    ('Label_Expenses_Total', 2, 67, 'text',
                        lambda x, d, p: 'TOTAL EXPENSES'),
                    # Row Total
                    ('Expenses Total', 1, 67, 'number',
                        lambda x, d, p: x['tot_expenses']),
                    ('Expenses IDR Total', 1, 67, 'number',
                        lambda x, d, p: x['tot_expenses_idr']),
            ]
            row_ftr1 = self.xls_row_template(cols_specs, ['Label_Expenses_Total', 'Expenses Total', 'Expenses IDR Total'])
    
            #row_count += 1
            self.xls_write_row(ws, total, data, parser, row_count, row_ftr1, row_bold_style)                  
            row_count += 1
            row_count += 1
            
            #NET PROFIT/LOSS
            total['tot_net'] = abs(total['tot_income'])-abs(total['tot_expenses'])
            cols_specs = [
                    ('Label_Net_Total', 2, 67, 'text',
                        lambda x, d, p: self._display_net(x['tot_net'])),
                    # Row Total
                    ('Total', 1, 67, 'number',
                        lambda x, d, p: abs(x['tot_net'])),
                    ('Total IDR', 1, 67, 'number',
                        lambda x, d, p: parser._sum_currency_amount_account(abs(x['tot_net']))),
            ]
            row_ftr1 = self.xls_row_template(cols_specs, ['Label_Net_Total', 'Total', 'Total IDR'])
            self.xls_write_row(ws, total, data, parser, row_count, row_ftr1, row_bold_style)                  
            row_count += 1
#===============================================================================
#        parser.get_data(data)
#        """total = {
#                 'tot_expenses':0,
#                 'tot_income':0,
#        }"""
#        print "@@@", parser
#        for e in parser.get_lines():
#            if e['level'] <> 2: 
#            #if parser.get_lines_another('income'):
#                print "################################################################",e['level']
#                style = row_normal_style
#            else:
#                style = row_bold_style
#            self.xls_write_row(ws, e, data, parser,
#                        row_count, row_balance, row_normal_style)
#            row_count += 1    
#            print"--------------------------------------------------------------------------------------------------"             
#        """total['tot_expenses'] += e['balance']
#        total['tot_income'] += e['balance']
#            
#        self.xls_write_row(ws, e, data, parser,
#                        row_count, row_balance, style)
#        row_count += 1     
#             
#        cols_specs = [
#                ('Label_Expenses_Total', 2, 67, 'text',
#                    lambda x, d, p: 'TOTAL EXPENSES'),
#                # Row Total
#                ('Expenses Total', 1, 67, 'number',
#                    lambda x, d, p: abs(x['tot_expenses'])),
#                ('Label_Income_Total', 2, 67, 'text',
#                    lambda x, d, p: 'TOTAL INCOME'),
#                # Row Total
#                ('Income Total', 1, 67, 'number',
#                    lambda x, d, p: abs(x['tot_income'])),                      
#        ]
#        row_ftr1 = self.xls_row_template(cols_specs, 
#                                         ['Label_Expenses_Total', 'Expenses Total','Label_Income_Total', 'Income Total'])
# 
#        row_count += 1
#        self.xls_write_row(ws, total, data, parser, row_count, row_ftr1, total_style)                  
#        row_count += 1"""
#        for w in parser.get_lines_another('income'):
#            if parser._sum_currency_amount_account(w['balance1']): 
#                    style = row_normal_style
#            else:
#                    style = row_bold_style
#                    
# 
#            self.xls_write_row(ws, w, data, parser,
#                        row_count, row_balance, style)
#            row_count += 1
#===============================================================================
        


        pass

account_profit_loss_xls(
        'report.account.profit.loss.xls',
        'account.account',
        'addons/ad_account_optimization/report/account_profit_loss.rml',
        parser=report_pl_account_horizontal,
        header=False)


