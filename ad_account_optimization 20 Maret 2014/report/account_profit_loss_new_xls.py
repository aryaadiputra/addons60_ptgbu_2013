# -*- coding: utf-8 -*-
# Copyright 2010 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import time
import xlwt
from report_engine_xls import report_xls
from ad_account_optimization.report.account_profit_loss_new import report_pl_account_horizontal_new
import cStringIO

class account_profit_loss_new_xls(report_xls):
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
    
    def romawi_number(self, number):
        if number == 1:
            romawi_number = "I"
        elif number == 2:
            romawi_number = "II"
        elif number == 3:
            romawi_number = "III"
        elif number == 4:
            romawi_number = "IV"
        elif number == 5:
            romawi_number = "V"
        else:
            romawi_number = "Error Number"
        return romawi_number
    
    def custom_total(self, code):
            if code == '6-0-00-00-00':
                custom_label = 'Gross Profit'
            
            elif code == '7-0-00-00-00':
                custom_label = 'Income / (Loss) from Operation - EBITDA'
                
            elif code == '8-0-00-00-00':
                custom_label = 'Net Income / (Loss) Before Tax - NIBT'
                
            else:
                custom_label = ''
                
            custom_res = {
                        'custom_label'    : custom_label,
                        #'custom_amount'   : 9999999
                          }
            return custom_res
    
    def generate_xls_report(self, parser, data, obj, wb):
        c = parser.localcontext['company']
        ws = wb.add_sheet(('Profit and Loss- %s - %s' % (c.partner_id.ref, c.currency_id.name))[:31])
        #ws.panes_frozen = True
        #ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        ws.show_grid = 0
        
        ws.col(0).width     = len("AB")*256
        ####B####
        ws.col(1).width     = len("AB")*256
        ####C####
        ws.col(2).width     = len("AB")*256
        ####D####
        ws.col(3).width     = len("ABCDEFGHIJKL")*1024
        ####E####
        #ws.col(4).width     = len("ABC")*256
        ####F####
        ws.col(5).width     = len("AB")*256
        ####G####
        ws.col(6).width     = len("ABCDEF")*1024
        ####H####
        ws.col(7).width     = len("AB")*256
        
        c = parser.get_data(data)
        print "---------------------------------------------", c
        result_select_date_hdr  = c['result_select_date_hdr']
        select_date             = c['result_select_date']
        
        ws.fit_width_to_pages = 1
        
        judul1      = "PT GUNUNG BARA UTAMA"
        judul2      = "Statement of Proft / (Loss)"
        tgl_judul   = result_select_date_hdr
        judul4      = "(In Indonesian Rupiah)"
        
        cols_specs = [
                # Headers data
                ('Title', 8, 0, 'text',
                    lambda x, d, p: judul1),
                ('Title2', 8, 0, 'text',
                    lambda x, d, p: judul2),
                ('Title3', 8, 0, 'text',
                    lambda x, d, p: result_select_date_hdr),
                    #lambda x, d, p: x['result_select_date_hdr']),
                ('Title4', 8, 0, 'text',
                    lambda x, d, p: judul4),
                
                ('Field Kosong', 1, 0, 'text',
                    lambda x, d, p: ''),
                ('Kosong', 8, 0, 'text',
                    lambda x, d, p: " "),
                ('Notes', 1, 0, 'text',
                    lambda x, d, p: 'Notes'),
                ('No', 1, 0, 'text',
                    lambda x, d, p: 'No.'),
                ('Select Date', 1, 0, 'text',
                    #lambda x, d, p: x['select_date']),
                    lambda x, d, p: 'Tanggal'),
                ('Rp', 1, 0, 'text',
                    lambda x, d, p: 'Rp.'),
                
                
                ('Level 2 No', 1, 800, 'text',
                    lambda x, d, p: romawi_number),
                ('Level 2 Name', 1, 800, 'text',
                    lambda x, d, p: 'Total ' + x['lv2_name']),
                ('Account Name', 1, 800, 'text',
                    lambda x, d, p: x['name']),
                ###Revisi Minus###
                ('Balance', 1, 0, 'number',
                    lambda x, d, p: -x['balance']),
                ##################
                ('Balance Income Total', 1, 0, 'number',
                    lambda x, d, p: x['balance_tot']),
                ('Balance Expense Total', 1, 0, 'number',
                    lambda x, d, p: x['balance_tot']),
                     
                ('Label Net Loss', 1, 0, 'text',
                    lambda x, d, p: 'NET INCOME'),
                ('Net Loss', 1, 0, 'number',
                    lambda x, d, p: x['net_loss']), 
                
        ]                 

        ##################TITLE TEMPLATE########################
        row_hdr0 = self.xls_row_template(cols_specs, ['Kosong'])
        row_hdr1 = self.xls_row_template(cols_specs, ['Title'])
        row_hdr2 = self.xls_row_template(cols_specs, ['Title2'])
        row_hdr3 = self.xls_row_template(cols_specs, ['Title3'])
        row_hdr4 = self.xls_row_template(cols_specs, ['Title4'])
        row_hdr5 = self.xls_row_template(cols_specs, ['Kosong'])
        
        row_hdr_date = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong','Field Kosong','Field Kosong','Field Kosong','Field Kosong','Select Date',])
        row_hdr_notes = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong','Field Kosong','Notes'])
        row_hdr_no = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong','Field Kosong','No','Field Kosong'])
        
        
        ##################INCOME TEMPLATE########################
        row_income_level2 = self.xls_row_template(cols_specs, ['Level 2 No','Field Kosong','Account Name','Field Kosong','Field Kosong','Field Kosong','Field Kosong','Field Kosong'])
        row_income_level2_kosong = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong'])
        row_income_level3 = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong','Account Name','Field Kosong','Field Kosong','Balance','Field Kosong'])
        row_income_total_level2 = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Level 2 Name','Field Kosong','Field Kosong','Field Kosong','Balance Income Total','Field Kosong'])
        #######################################################
        
        
        ##################EXPENSES TEMPLATE########################
        row_expense_level2 = self.xls_row_template(cols_specs, ['Level 2 No','Field Kosong','Account Name','Field Kosong','Field Kosong','Field Kosong','Field Kosong','Field Kosong'])
        row_expense_level2_kosong = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong'])
        row_expense_level3 = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong','Account Name','Field Kosong','Field Kosong','Balance','Field Kosong'])
        row_expense_total_level2 = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Level 2 Name','Field Kosong','Field Kosong','Field Kosong','Balance Expense Total','Field Kosong'])
        
        net_loss = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Label Net Loss'])
        
        #######################################################
        
        ## Style variable Begin
        hdr_style = xlwt.easyxf('pattern: pattern solid, fore_color gray25;')
        row_normal_style=  xlwt.easyxf('font: height 200, name Times New Romance; align: wrap off;' ,num_format_str='#,##0.00;(#,##0.00)')
        row_bold_underline_style = xlwt.easyxf('font: height 200, name Times New Romance, underline on, bold on; align: wrap on, vert centre, horiz centre;',num_format_str='#,##0.00;(#,##0.00)')
        row_italic_style = xlwt.easyxf('font: height 200, name Times New Romance, italic on, bold off; align: wrap off,',num_format_str='#,##0.00;(#,##0.00)')
        row_bold_style = xlwt.easyxf('font: height 200, name Times New Romance, bold on;',num_format_str='#,##0.00;(#,##0.00)')
        row_bold_center_style = xlwt.easyxf('font: height 200, name Times New Romance, bold on; align: wrap on, vert centre, horiz centre;',num_format_str='#,##0.00;(#,##0.00)')
        
        ############TITLE################
        tittle_style0 = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold off; align: wrap on, vert centre, horiz centre; pattern: pattern solid, fore_color white;')
        tittle_style1 = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold on; align: wrap on, vert centre, horiz centre;')
        tittle_style2 = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold off; align: wrap on, vert centre, horiz centre;')
        tittle_style3 = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold off; align: wrap on, vert centre, horiz centre;')
        tittle_style4 = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz centre;')
        tittle_style5 = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold off; align: wrap on, vert centre, horiz centre;')
        
        tittle_date = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold on; align: wrap on, vert centre, horiz centre;')
        tittle_notes = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold off; align: wrap on, vert centre, horiz centre; borders: bottom dotted;')
        
        row_bold_non_border_style = xlwt.easyxf('font: height 200, name Times New Romance, bold on;',num_format_str='#,##0;(#,##0)')
        row_bold_top_border_style = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold off; align: wrap on, vert centre, horiz centre; borders: top dotted;')
        row_bold_bottom_border_style = xlwt.easyxf('font: height 200, name Times New Romance, bold on; borders: bottom dotted;',num_format_str='#,##0;(#,##0)')
        row_bold_right_style = xlwt.easyxf('font: height 200, name Times New Romance, bold on; borders: bottom double;',num_format_str='#,##0;(#,##0)')
        
        ##################################

        tittle_style = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold on; align: wrap on, vert centre, horiz centre; pattern: pattern solid, fore_color gray25;')
        subtittle_left_style = xlwt.easyxf('font: height 240, name Times New Romance, colour_index brown, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        subtittle_right_style = xlwt.easyxf('font: height 240, name Times New Romance, colour_index brown, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        subtittle_top_and_bottom_style = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        blank_style = xlwt.easyxf('font: height 650, name Times New Romance, colour_index brown, bold off; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        normal_style = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold off; align: wrap on, vert centre, horiz left;')
        total_style = xlwt.easyxf('font: height 240, name Times New Romance, colour_index brown, bold on, italic on; align: wrap on, vert centre;', num_format_str='#,##0.00;(#,##0.00)')
        
        ## Style variable End
        
        # Write headers
        self.xls_write_row(ws, None, data, parser, 0, row_hdr0, tittle_style0)
        self.xls_write_row(ws, None, data, parser, 1, row_hdr1, tittle_style1)
        self.xls_write_row(ws, None, data, parser, 2, row_hdr2, tittle_style2)
        self.xls_write_row(ws, None, data, parser, 3, row_hdr3, tittle_style3)
        self.xls_write_row(ws, None, data, parser, 4, row_hdr4, tittle_style4)
        self.xls_write_row(ws, None, data, parser, 5, row_hdr5, tittle_style5)
        
        self.xls_write_row(ws, None, data, parser, 7, row_hdr_notes, tittle_style2)
        #self.xls_write_row(ws, None, data, parser, 8, row_hdr_no, tittle_notes)
        
        ws.write(8, 4, 'No.', tittle_notes)
        ws.write(8, 6, 'Rp.', tittle_notes)

        row_count = 12
        #ws.horz_split_pos = row_count
      
        #parser.get_data(data)
        
        total = {
                 'tot_expenses':0,
                 'tot_income':0,
                 'tot_net':0,
        }
        
        ###Net LOss
        for w in parser.get_lines_another('income'):
            if w['type'] <> 'view': 
                style = row_normal_style   
                total['tot_income'] += w['balance']
            else:
                style = row_bold_style
        for e in parser.get_lines_another('expense'):
            if e['type'] <> 'view':
                style = row_normal_style
                total['tot_expenses'] += e['balance']
            else:
                style = row_bold_style
        #print "yyyyyyyyy",total['tot_income']+total['tot_expenses']
        #-------------------------------
        total['tot_net'] = abs(total['tot_income'])-abs(total['tot_expenses'])
        
        print "total['tot_net']------------------------------------>>", total['tot_net']
        #####
        ###INCOME###
        lv2_name    = ""
        lv2_total    = 0.0
        total_income = 0.0
        total_expense = 0.0
        level2_no   = 0
        custom_amount_total = 0.0
        
        for a in parser.get_lines_another('income'):
            if a['level'] == 2:
                style = row_bold_style
            elif a['level'] == 3:
                style = row_italic_style
            else:
                style = row_normal_style
            if a['type'] == 'view' and a['level'] == 2:
                if lv2_name <> "":
                    #print "level",level2_no,total_expense
                    
                    custom_amount_total += lv2_total
                    
                    ws.write(row_count, 6, None, row_bold_top_border_style)
                    row_count += 1
                    ###Remove Border###
                    #self.xls_write_row(ws, a, data, parser, row_count, row_expense_level2_kosong, style)
                    #row_count += 1
                    ws.write(row_count, 2, 'Total ' + lv2_name, row_bold_non_border_style)
                    ws.write(row_count, 6, lv2_total, row_bold_bottom_border_style)
                    row_count += 3
                    #Remove Border
#                    self.xls_write_row(ws, a, data, parser, row_count, row_income_level2_kosong, style)
#                    row_count += 1
#                    self.xls_write_row(ws, {'lv2_name' : lv2_name,'balance_tot' : lv2_total}, data, parser, row_count, row_income_total_level2, style)
#                    row_count += 3
                level2_no+=1
                romawi_number = self.romawi_number(level2_no)
                self.xls_write_row(ws, a, data, parser, row_count, row_income_level2, style)
                row_count += 1
                self.xls_write_row(ws, a, data, parser, row_count, row_income_level2_kosong, style)
                row_count += 1
                
                lv2_name =  a['name']
                ###Revisi Minus###
                lv2_total =  -a['balance']
                
            if a['type'] == 'view' and a['level'] == 3:
                
                total_income += lv2_total
                    
                self.xls_write_row(ws, a, data, parser, row_count, row_income_level3, style)
                row_count += 1
        
        custom_amount_total += lv2_total
        total_income += lv2_total
        row_count += 1
        ws.write(row_count, 2, 'Total ' + lv2_name , row_bold_non_border_style)
        ws.write(row_count, 6, lv2_total, row_bold_bottom_border_style)
        row_count += 3
        
        
        
        
        
        
        
        
        
        
        
     ###EXPENSE###
        
        lv2_code    = ''
        lv2_name    = ""
        lv2_total    = 0.0
        total_expense = 0.0
        #level2_no   = 0
        
        for a in parser.get_lines_another('expense'):
            if a['level'] == 2:
                style = row_bold_style
            elif a['level'] == 3:
                style = row_italic_style
            else:
                style = row_normal_style
            if a['type'] == 'view' and a['level'] == 2:
                if lv2_name <> "":
                    #print "level",level2_no,total_expense
                    custom_amount_total += lv2_total
                    ws.write(row_count, 6, None, row_bold_top_border_style)
                    row_count += 1
                    ###Remove Border###
                    #self.xls_write_row(ws, a, data, parser, row_count, row_expense_level2_kosong, style)
                    #row_count += 1
                    ws.write(row_count, 2, 'Total ' + lv2_name, row_bold_non_border_style)
                    ws.write(row_count, 6, lv2_total, row_bold_bottom_border_style)
                    row_count += 3
                    
                    ####CUSTOM TOTAL###
                    custom = self.custom_total(lv2_code)
                    
                    if custom['custom_label'] <> "":
                    
                        ws.write(row_count, 2,  custom['custom_label'], row_bold_non_border_style)
                        ####EDit####
                        if custom['custom_label'] == "Income / (Loss) from Operation - EBITDA":
                            ###Revisi Minus###
                            custom_amount_total_ebitda = custom_amount_total
                            ##################
                            ws.write(row_count, 6,  custom_amount_total_ebitda, row_bold_right_style)
                        else:
                            ###Revisi Minus###
                            ws.write(row_count, 6,  custom_amount_total, row_bold_right_style)
                            #################
                        row_count += 3
                        ############
                        
                    ###Remove Border###
                    #self.xls_write_row(ws, {'lv2_name' : lv2_name,'balance_tot' : lv2_total}, data, parser, row_count, row_expense_total_level2, style)
                    #row_count += 3
                level2_no+=1
                romawi_number = self.romawi_number(level2_no)
                self.xls_write_row(ws, a, data, parser, row_count, row_expense_level2, style)
                row_count += 1
                self.xls_write_row(ws, a, data, parser, row_count, row_expense_level2_kosong, style)
                row_count += 1
                
                lv2_code    =  a['code']
                lv2_name    =  a['name']
                ###Revisi Minus###
                lv2_total   =  -a['balance']
                ##################
                
            if a['type'] == 'view' and a['level'] == 3:
                
                total_expense += lv2_total
                    
                self.xls_write_row(ws, a, data, parser, row_count, row_expense_level3, style)
                row_count += 1
        
        custom_amount_total += lv2_total
        total_expense += lv2_total
        row_count += 1
        ws.write(row_count, 2, 'Total ' + lv2_name , row_bold_non_border_style)
        ws.write(row_count, 6, lv2_total, row_bold_style)
        row_count += 2
        
        ws.write(row_count, 2,  '', row_bold_right_style)
        ws.write(row_count, 3,  '', row_bold_right_style)
        ws.write(row_count, 4,  '', row_bold_right_style)
        ws.write(row_count, 6,  '', row_bold_right_style)
        row_count += 1
        
        ws.write(row_count, 2,  'NET INCOME (LOSS)', row_bold_right_style)
        ws.write(row_count, 3,  '', row_bold_right_style)
        ws.write(row_count, 4,  '', row_bold_right_style)
        ws.write(row_count, 6,  total['tot_net'], row_bold_right_style)
        row_count += 1
        
        ###Remove Border###
        #self.xls_write_row(ws, {'net_loss' : total['tot_net']}, data, parser, row_count, net_loss, row_bold_right_style)
        #row_count += 1
           
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

account_profit_loss_new_xls(
        'report.account.profit.loss.new.xls',
        'account.account',
        'addons/ad_account_optimization/report/account_profit_loss.rml',
        parser=report_pl_account_horizontal_new,
        header=False)


