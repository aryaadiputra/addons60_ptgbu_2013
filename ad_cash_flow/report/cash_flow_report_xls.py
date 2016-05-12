# -*- coding: utf-8 -*-
# Copyright 2010 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import time
import xlwt
from report_engine_xls import report_xls
from ad_cash_flow.report.cash_flow_report import cash_flow_report
import cStringIO
import pooler

class account_cash_flow_report_xls(report_xls):
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
    
    def generate_xls_report(self, parser, data, obj, wb):
        
        print "*********************************"
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", parser
        #print parser._sum_currency_amount_account(1)
        c = parser.localcontext['company']
        ws = wb.add_sheet(('Cash Flow- %s - %s' % (c.partner_id.ref, c.currency_id.name))[:31])
        #ws.panes_frozen = True
        #ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        ws.show_grid = 1
        ####A####
        ws.col(0).width     = len("AB")*256
        ####B####
        ws.col(1).width     = len("ABC")*256
        ####C####
        ws.col(2).width     = len("ABCDEFGH")*1024
        
        ####D####
        ws.col(3).width     = len("ABCDEFGHI")*1024
        ####E####
        #ws.col(4).width     = len("ABC")*256
        ####F####
        #ws.col(5).width     = len("ABC")*
        ####G####
        ws.col(6).width     = len("AB")*256
        ####H####
        ws.col(7).width     = len("ABCDEFG")*1024
        ####I####
        ws.col(8).width     = len("AB")*256
        ####J####
        ws.col(9).width     = len("ABCDEFG")*1024
        ####K####
        ws.col(10).width    = len("AB")*len("AB")*256
        
        
        
        hdr1      = "Name"
        hdr2      = "Keterangan"
        hdr3      = "Cash Flow Account"
        
        judul1      = "PT GUNUNG BARA UTAMA"
        judul2      = "Statement of Cashflow"
        tgl_judul   = "TANGGAL"
        judul4      = "(In Indonesian Rupiah)"
        
        cols_specs = [
                # Headers data
                
                ('Title', 1, 0, 'text',
                    lambda x, d, p: judul1),
                ('Title2', 1, 0, 'text',
                    lambda x, d, p: judul2),
                ('Title3', 1, 0, 'text',
                    lambda x, d, p: x['date']),
                ('Title4', 1, 0, 'text',
                    lambda x, d, p: judul4),
                
                
                
                ('Nama', 1, 0, 'text',
                    lambda x, d, p: hdr1),
                ('Keterangan', 1, 0, 'text',
                    lambda x, d, p: hdr2),
                ('Cash Flow Account', 1, 0, 'text',
                    lambda x, d, p: hdr3),
                      
                ('Data Nama', 1, 0, 'text',
                    lambda x, d, p: x['nama']),
                ('Data Keterangan', 1, 0, 'text',
                    lambda x, d, p: x['keterangan']),
                ('Data Cash Flow Account', 1, 0, 'text',
                    lambda x, d, p: x['category']),
                ('Data Account', 1, 0, 'text',
                    lambda x, d, p: x['account']),
                ('Data Amount', 1, 0, 'number',
                    lambda x, d, p: x['amount']),
                
                #######SUB TOTAL##############
                ('Data Sub Cash Flow Account', 1, 0, 'text',
                    lambda x, d, p: x['sub_category']),
                ('Data Total Sub Amount', 1, 0, 'number',
                    lambda x, d, p: x['tot_sub_amount']),
                ######Parent TOTAL ###########
                ('Data Parent Cash Flow Account', 1, 0, 'text',
                    lambda x, d, p: x['parent_category']),
                ('Data Total Parent Amount', 1, 0, 'number',
                    lambda x, d, p: x['tot_parent_amount']),
                ##############################
                      
                ('Romawi Number', 1, 0, 'text',
                    lambda x, d, p: x['romawi_number']),
                ('Category Header', 1, 0, 'text',
                    lambda x, d, p: x['category_name']),
                
                
                ('Kosong', 11, 0, 'text',
                    lambda x, d, p: " "),
                ('Notes', 1, 0, 'text',
                    lambda x, d, p: 'Notes'),
                ('Select Date', 1, 0, 'text',
                    lambda x, d, p: x['select_date']),
                ('Initial Date', 1, 0, 'text',
                    lambda x, d, p: x['initial_date']),
                
                ('Rp', 1, 0, 'text',
                    lambda x, d, p: 'Rp.'),
                
         
                ('Field Kosong', 1, 0, 'text',
                    lambda x, d, p: ''),
                   
                ('Assets Account Level 2', 2, 0, 'text',
                    lambda x, d, p: x['name']),
                ('Liability Account Level 2', 2, 0, 'text',
                    lambda x, d, p: 'LIABILITY & EQUITY'),
                      
                      
                      
                ('Total', 1, 0, 'text',
                    lambda x, d, p: 'Total'),
                     
                      
                ('BalanceA', 1, 0, 'number',
                    lambda x, d, p: x['balance_tot1']),
                ('BalanceB', 1, 0, 'number',
                    lambda x, d, p: x['balance_tot2']),
                #########ASSET TOTAL###########
                ('Asset Total Label', 3, 0, 'text',
                    lambda x, d, p: 'TOTAL ASSET'),
                ('Asset TotalA', 1, 0, 'number',
                    lambda x, d, p: x['asset_tot1']),
                ('Asset TotalB', 1, 0, 'number',
                    lambda x, d, p: x['asset_tot2']),
                ##################################
                
                #########LIABILITY TOTAL###########
                ('Liability Total Label', 3, 0, 'text',
                    lambda x, d, p: 'TOTAL LIABILITY & EQUITY'),
                ('Liability TotalA', 1, 0, 'number',
                    lambda x, d, p: x['liability_tot1']),
                ('Liability TotalB', 1, 0, 'number',
                    lambda x, d, p: x['liability_tot2']),
                      
                      
                ('Net Loss Label', 3, 0, 'text',
                    lambda x, d, p: 'Current Year Surplus / (Deficit)'),
                ('Net Loss', 1, 0, 'number',
                    lambda x, d, p: x['net_loss']),
                ('Net Loss2', 1, 0, 'number',
                    lambda x, d, p: x['net_loss2']),
                ##################################
              
                ('Name1A', 1, 0, 'text',
                    lambda x, d, p: x['name']),
                ('Balance1A', 1, 0, 'number',
                    lambda x, d, p: x['balance']),
                ('Balance1B', 1, 0, 'number',
                    lambda x, d, p: x['balance2']),
                
                
                
                ('Asset Balance', 1, 0, 'number',
                    lambda x, d, p: x['balance1']),
                      
                ('Asset Balance IDR', 1, 0, 'number',
                    lambda x, d, p: parser._sum_currency_amount_account(x['balance1'])),
                ('Liab. Code', 1, 0, 'text',
                    lambda x, d, p: self._display_code(x['code'])),
                ('Liabilities and Equities Account', 1, 0, 'text',
                    lambda x, d, p: '  '*x['level'] + self._display_code(x['name'])),
                ('Liab. Balance', 1, 0, 'number',
                    lambda x, d, p: self._display_balance(x['name'],x['balance'])),
                ('Liab. Balance IDR', 1, 0, 'number',
                    lambda x, d, p: parser._sum_currency_amount_account(self._display_balance(x['name'],x['balance']))),
                      
#                ('Footer1', 1, 270, 'number',
#                    lambda x, d, p: x['footer1']),
#                ('Footer2', 1, 270, 'text',
#                    lambda x, d, p: 'SUM(B4:B18)'),
#                ('Footer3', 1, 270, 'text',
#                    lambda x, d, p: 'xxxx3'),
                
                
        ]
        
        ##################TITLE TEMPLATE########################
        row_hdr0 = self.xls_row_template(cols_specs, ['Field Kosong', 'Kosong'])
        row_hdr1 = self.xls_row_template(cols_specs, ['Field Kosong', 'Title'])
        row_hdr2 = self.xls_row_template(cols_specs, ['Field Kosong', 'Title2'])
        row_hdr3 = self.xls_row_template(cols_specs, ['Field Kosong', 'Title3'])
        row_hdr4 = self.xls_row_template(cols_specs, ['Field Kosong', 'Title4'])
        row_hdr5 = self.xls_row_template(cols_specs, ['Field Kosong', 'Kosong'])
        
        row_category    = self.xls_row_template(cols_specs, ['Field Kosong', 'Romawi Number', 'Category Header'])
        #row_hdr0 = self.xls_row_template(cols_specs, ['Field Kosong', 'Nama', 'Keterangan', 'Cash Flow Account'])
        
        row_data = self.xls_row_template(cols_specs, ['Field Kosong', 'Data Cash Flow Account', 'Field Kosong','Data Keterangan', 'Data Account', 'Field Kosong','Field Kosong','Data Amount'])
        tot_sub_categ = self.xls_row_template(cols_specs, ['Field Kosong', 'Data Sub Cash Flow Account', 'Field Kosong','Field Kosong', 'Field Kosong', 'Field Kosong','Field Kosong','Data Total Sub Amount'])
        tot_parent_categ = self.xls_row_template(cols_specs, ['Field Kosong', 'Field Kosong', 'Field Kosong','Data Parent Cash Flow Account', 'Field Kosong', 'Field Kosong','Field Kosong','Data Total Parent Amount'])
        
        row_hdr_date = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong','Field Kosong','Field Kosong','Field Kosong','Field Kosong','Select Date','Field Kosong','Initial Date'])
        row_hdr_notes = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong','Field Kosong','Field Kosong','Notes','Field Kosong','Rp','Field Kosong','Rp'])
        
        #row_hdr_date = self.xls_row_template(cols_specs, ['Notes'])
        #######################################################
        row_bold_top_border_dotted_style = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold on; borders: top dotted;',num_format_str='#,##0;(#,##0)')
        row_bold_top_border_double_style = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold on; borders: top double;',num_format_str='#,##0;(#,##0)')
#        
        ##################ASSET TEMPLATE########################
        row_asset_level2 = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Assets Account Level 2'])
        row_asset_level2_kosong = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong'])
        row_asset_total_level2 = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Level 3 Name','Field Kosong','Field Kosong','Field Kosong','Field Kosong','BalanceA','Field Kosong', 'BalanceB'])
        row_asset_level3 = self.xls_row_template(cols_specs, ['NumberA','Field Kosong','NameA'])
        row_asset_level4 = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong','Name1A','Field Kosong','Field Kosong','Field Kosong','Balance1A','Field Kosong', 'Balance1B'])
        row_asset_total = self.xls_row_template(cols_specs, ['Field Kosong','Asset Total Label'])
        #row_asset_total = self.xls_row_template(cols_specs, ['Field Kosong','Asset Total Label','Field Kosong','Field Kosong','Field Kosong','Asset TotalA','Field Kosong', 'Asset TotalB'])
        #######################################################
        
        ##################LIABILITY TEMPLATE########################
        row_liability_level2 = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Liability Account Level 2'])
        row_liability_level2_kosong = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong'])
        row_liability_total_level2 = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Level 3 Name','Field Kosong','Field Kosong','Field Kosong','Field Kosong','BalanceA','Field Kosong', 'BalanceB'])
        row_liability_level3 = self.xls_row_template(cols_specs, ['NumberA','Field Kosong','NameA'])
        row_liability_level4 = self.xls_row_template(cols_specs, ['Field Kosong','Field Kosong','Field Kosong','Name1A','Field Kosong','Field Kosong','Field Kosong','Balance1A','Field Kosong', 'Balance1B'])
        row_liability_total = self.xls_row_template(cols_specs, ['Field Kosong','Liability Total Label'])
        
        row_net_loss = self.xls_row_template(cols_specs, ['Field Kosong','Net Loss Label','Field Kosong','Field Kosong','Field Kosong','Net Loss','Field Kosong', 'Net Loss2'])
        #######################################################
        
        ## Style variable Begin
        hdr_style = xlwt.easyxf('pattern: pattern solid, fore_color gray25;')
        row_normal_style=  xlwt.easyxf('font: height 200, name Times New Romance; align: wrap off;' ,num_format_str='#,##0;(#,##0)')
        row_bold_underline_style = xlwt.easyxf('font: height 200, name Times New Romance, underline on, bold on; align: wrap on, vert centre, horiz centre;',num_format_str='#,##0;(#,##0)')
        row_italic_style = xlwt.easyxf('font: height 200, name Times New Romance, italic on, bold off; align: wrap off,',num_format_str='#,##0;(#,##0)')
        row_bold_style = xlwt.easyxf('font: height 200, name Times New Romance, bold on; borders: bottom dotted;',num_format_str='#,##0;(#,##0)')
        row_bold_non_border_style = xlwt.easyxf('font: height 200, name Times New Romance, bold on;',num_format_str='#,##0;(#,##0)')
        row_bold_non_border_center_style = xlwt.easyxf('font: height 200, name Times New Romance, bold on; align: vert centre, horiz centre;',num_format_str='#,##0;(#,##0)')
        row_bold_center_style = xlwt.easyxf('font: height 200, name Times New Romance, bold on; align: wrap on, vert centre, horiz centre; borders: bottom double;',num_format_str='#,##0;(#,##0)')
        row_bold_right_style = xlwt.easyxf('font: height 200, name Times New Romance, bold on; borders: bottom double;',num_format_str='#,##0;(#,##0)')
        ############TITLE################
        tittle_style0 = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold off;  pattern: pattern solid, fore_color green;')
        tittle_style1 = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold on; ')
        tittle_style2 = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold off; ')
        tittle_style3 = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold off; ')
        tittle_style4 = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold off, italic on;')
        tittle_style5 = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold off; ')
        
        category_bold_style = xlwt.easyxf('font: height 200, name Times New Romance, bold on;',num_format_str='#,##0;(#,##0)')
        
        tittle_date = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold on; align: wrap on, vert centre, horiz centre;')
        tittle_notes = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold off; align: wrap on, vert centre, horiz centre; borders: bottom dotted;')
        ##################################
        
        row_bold_top_border_style = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold off; align: wrap on, vert centre, horiz centre; borders: top dotted;')
        tittle_style = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold on; align: wrap on, vert centre, horiz centre; pattern: pattern solid, fore_color gray25;')
        subtittle_left_style = xlwt.easyxf('font: height 240, name Times New Romance, colour_index brown, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        subtittle_right_style = xlwt.easyxf('font: height 240, name Times New Romance, colour_index brown, bold on, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        subtittle_top_and_bottom_style = xlwt.easyxf('font: height 240, name Times New Romance, colour_index black, bold off, italic on; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        blank_style = xlwt.easyxf('font: height 650, name Times New Romance, colour_index brown, bold off; align: wrap on, vert centre, horiz left; pattern: pattern solid, fore_color gray25;')
        normal_style = xlwt.easyxf('font: height 200, name Times New Romance, colour_index black, bold off;',num_format_str='#,##0;(#,##0)')
        total_style = xlwt.easyxf('font: height 240, name Times New Romance, colour_index brown, bold on, italic on; align: wrap on, vert centre;', num_format_str='#,##0.00;(#,##0.00)')
        
        ## Style variable End

        # Write headers Title
        #c = parser.get_data(data)
        
        #parser._get_move_line(data)
        ############Header#################
        #parser._get_data(data)
        c = parser._get_data(data)
        print "x___________________", c
        self.xls_write_row(ws, None, data, parser, 0, row_hdr0, tittle_style0)
        self.xls_write_row(ws, None, data, parser, 1, row_hdr1, tittle_style1)
        self.xls_write_row(ws, None, data, parser, 2, row_hdr2, tittle_style2)
        self.xls_write_row(ws, {'date' : c['result_date_start'] +' s/d '+ c['result_date_end']}, data, parser, 3, row_hdr3, tittle_style3)
        self.xls_write_row(ws, None, data, parser, 4, row_hdr4, tittle_style4)
        self.xls_write_row(ws, None, data, parser, 5, row_hdr5, tittle_style5)
        
        
        
        self.xls_write_row(ws, None, data, parser, 6, row_hdr0, tittle_style0)
        row_count           = 8
        no                  = 0 
        amount              = 0.0
        parent_categ        = ""
        tot_parent_amount   = 0.0
        net_increase        = 0.0
        
        for categ in parser._get_cashflow_category(data):
            tot_parent_amount   = 0.0
            no += 1
            #print "wwwwwwwwwwwwwwwwwwwwwww", categ.name
            if no > 1:
                row_count += 2
                ws.write(row_count, 5, '', tittle_notes)
                row_count += 1
            
            parent_categ = categ.name
            romawi_number = self.romawi_number(no)
            self.xls_write_row(ws, {'romawi_number' : romawi_number, 'category_name': categ.name} , data, parser, row_count, row_category, category_bold_style)
            row_count += 2
            
            ##################################
            #for y in parser._get_move_line_partial(data):
            #    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", y
            ##################################
            
            sub_categ       = ""
            
            for subcateg in parser._get_cashflow_subcategory(categ.id):
                #print "YYYYYYYYYYYYYYYYYYYYY",subcateg.name
                sub_categ = ""
                tot_sub_amount = 0.0
                for i in parser._get_move_line(data, subcateg.id):
                    #name    = i.move_id.partner_id.name
                    #ref     = i.name + i.account_id.name
                    ref     = i.name
                    account = i.account_id.name
                    amount  = i.debit or 0.0 - i.credit or 0.0
                    ######
                    categ   = ""
                    if i.account_id.sub_cashflow_category_id:
                        categ   = i.account_id.sub_cashflow_category_id.name
                        sub_categ   = i.account_id.sub_cashflow_category_id.name
                    ####
                    
                    self.xls_write_row(ws, {'category' : categ, 'keterangan': ref, 'account': account, 'amount':amount} , data, parser, row_count, row_data, normal_style)
                    row_count += 1
                    tot_sub_amount += amount
                if sub_categ <> "" :
                    #self.xls_write_row(ws, {'sub_category' : 'Sub Total ' + sub_categ, 'tot_sub_amount':tot_sub_amount} , data, parser, row_count, tot_sub_categ, category_bold_style)
                    ws.write(row_count, 1, 'Sub Total ' + sub_categ, category_bold_style)
                    ws.write(row_count, 7, tot_sub_amount, row_bold_top_border_dotted_style)
                    row_count += 2
            
                tot_parent_amount += tot_sub_amount
            print "++++++++++++++++++++++++++++++", parent_categ, tot_parent_amount
            #if parent_categ <> "":
            #    self.xls_write_row(ws, {'parent_category' : 'Net Cash Provided by (Used in) ' + parent_categ, 'tot_parent_amount':tot_parent_amount} , data, parser, row_count, tot_parent_categ, category_bold_style)
            #    row_count += 1
            if parent_categ <> "":
                ws.write(row_count, 3, 'Net Cash Provided by (Used in) ' + parent_categ, category_bold_style)
                ws.write(row_count, 7, tot_parent_amount, row_bold_top_border_double_style)
                row_count += 1
                
                net_increase += tot_parent_amount
                #ws.write(row_count, 5, '', tittle_notes)
                #row_count += 1
        
        row_count += 2
        ws.write(row_count, 1, 'NET INCREASE IN CASH ON HAND AND IN BANKS', category_bold_style)
        ws.write(row_count, 7, net_increase, category_bold_style)
        row_count += 2
        
        #############Beginning############
        cash_beginning  = parser._get_cash_beginning(data)
        cash_ending     = cash_beginning - net_increase
        ##################################
            
        ws.write(row_count, 1, 'CASH ON HAND AND IN BANKS AT THE BEGINNING OF THE MONTH', category_bold_style)
        ws.write(row_count, 7, cash_beginning, category_bold_style)
        row_count += 2
        
        ws.write(row_count, 1, 'CASH ON HAND AND IN BANKS AT THE ENDING OF THE MONTH', category_bold_style)
        ws.write(row_count, 7, cash_ending, category_bold_style)
        row_count += 2
        
        pass

account_cash_flow_report_xls(
        'report.cash.flow.report.xls',
        'account.move.line',
        'addons/account/report/account_balance_sheet_horizontal.rml',
        parser=cash_flow_report,
        header=False)
