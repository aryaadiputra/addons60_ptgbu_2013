# -*- coding: utf-8 -*-
# Copyright 2010 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import time
import xlwt
from report_engine_xls import report_xls
from ad_raw_data.report.raw_data_report import raw_data_report
import cStringIO
import pooler
import datetime, dateutil.parser
import re

class account_raw_data_report_xls(report_xls):
    
    
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
        
        #print "*********************************"
        #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", parser
        #print parser._sum_currency_amount_account(1)
        c = parser.localcontext['company']
        ws = wb.add_sheet(('Raw Data- %s - %s' % (c.partner_id.ref, c.currency_id.name))[:31])
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
        hdr3      = "Raw Data"
        
        judul1      = "PT GUNUNG BARA UTAMA"
        judul2      = "Raw Data"
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
                      
                #################Label Data############
                ('Label Division', 1, 0, 'text',
                    lambda x, d, p: 'Division'),
                ('Label Department', 1, 0, 'text',
                    lambda x, d, p: 'Department'),
                      
                ('Label DigitCOA', 1, 0, 'text',
                    lambda x, d, p: '1st Digit COA'),
                ('Label Parent Account', 1, 0, 'text',
                    lambda x, d, p: 'Parent COA'),
                ('Label Account', 1, 0, 'text',
                    lambda x, d, p: 'COA'),
                      
                ('Label DigitAnalytic', 1, 0, 'text',
                    lambda x, d, p: '1st Digit Analytic'),
                ('Label Parent Analytic Code Name', 1, 0, 'text',
                    lambda x, d, p: 'Parent Analytic COA'),
                ('Label Analytic Code Name', 1, 0, 'text',
                    lambda x, d, p: 'Analytic COA'),
                
                
                ('Label Analytic Account', 1, 0, 'text',
                    lambda x, d, p: 'Analytic COA & Dept'),
                ('Label Analytic COA Code', 1, 0, 'text',
                    lambda x, d, p: 'Analytic COA Code'),
                      
                ('Label Parent Category', 1, 0, 'text',
                    lambda x, d, p: 'CFLevel-1'),
                ('Label Category', 1, 0, 'text',
                    lambda x, d, p: 'CFLevel-2'),      
                
                ('Label Journal', 1, 0, 'text',
                    lambda x, d, p: 'Journal'),
                ('Label Move', 1, 0, 'text',
                    lambda x, d, p: 'Journal Reff#'),
                ('Label Name', 1, 0, 'text',
                    lambda x, d, p: 'Trx Desc-1'),    
                ('Label Ref', 1, 0, 'text',
                    lambda x, d, p: 'Trx Desc-2'),  
                ('Label Description', 1, 0, 'text',
                    lambda x, d, p: 'Trx Desc-3'),
                ('Label Partner', 1, 0, 'text',
                    lambda x, d, p: 'Partner'),
                ('Label Period', 1, 0, 'text',
                    lambda x, d, p: 'Period'),
                ('Label Process Date', 1, 0, 'text',
                    lambda x, d, p: 'DB Date'),
                ('Label Get Period', 1, 0, 'text',
                    lambda x, d, p: 'Trx Period'),
                ('Label Date', 1, 0, 'text',
                    lambda x, d, p: 'Trx Date'),
                ('Label Create Date', 1, 0, 'text',
                    lambda x, d, p: 'Posting Date'),
                
                ('Label Actual Amount', 1, 0, 'text',
                    lambda x, d, p: 'Actual YTD'),
                ('Label Budget YTD', 1, 0, 'text',
                    lambda x, d, p: 'Budget YTD'),
                ('Label Budget Amount', 1, 0, 'text',
                    lambda x, d, p: 'Annual Budget'),
                      
                ('Label Actual01', 1, 0, 'text',
                    lambda x, d, p: 'Actual01'),
                ('Label Actual02', 1, 0, 'text',
                    lambda x, d, p: 'Actual02'),
                ('Label Actual03', 1, 0, 'text',
                    lambda x, d, p: 'Actual03'),
                ('Label Actual04', 1, 0, 'text',
                    lambda x, d, p: 'Actual04'),
                ('Label Actual05', 1, 0, 'text',
                    lambda x, d, p: 'Actual05'),
                ('Label Actual06', 1, 0, 'text',
                    lambda x, d, p: 'Actual06'),
                ('Label Actual07', 1, 0, 'text',
                    lambda x, d, p: 'Actual07'),
                ('Label Actual08', 1, 0, 'text',
                    lambda x, d, p: 'Actual08'),
                ('Label Actual09', 1, 0, 'text',
                    lambda x, d, p: 'Actual09'),
                ('Label Actual10', 1, 0, 'text',
                    lambda x, d, p: 'Actual10'),
                ('Label Actual11', 1, 0, 'text',
                    lambda x, d, p: 'Actual11'),
                ('Label Actual12', 1, 0, 'text',
                    lambda x, d, p: 'Actual12'),
                      
                ('Label Budget01', 1, 0, 'text',
                    lambda x, d, p: 'Budget01'),
                ('Label Budget02', 1, 0, 'text',
                    lambda x, d, p: 'Budget02'),
                ('Label Budget03', 1, 0, 'text',
                    lambda x, d, p: 'Budget03'),
                ('Label Budget04', 1, 0, 'text',
                    lambda x, d, p: 'Budget04'),
                ('Label Budget05', 1, 0, 'text',
                    lambda x, d, p: 'Budget05'),
                ('Label Budget06', 1, 0, 'text',
                    lambda x, d, p: 'Budget06'),
                ('Label Budget07', 1, 0, 'text',
                    lambda x, d, p: 'Budget07'),
                ('Label Budget08', 1, 0, 'text',
                    lambda x, d, p: 'Budget08'),
                ('Label Budget09', 1, 0, 'text',
                    lambda x, d, p: 'Budget09'),
                ('Label Budget10', 1, 0, 'text',
                    lambda x, d, p: 'Budget10'),
                ('Label Budget11', 1, 0, 'text',
                    lambda x, d, p: 'Budget11'),
                ('Label Budget12', 1, 0, 'text',
                    lambda x, d, p: 'Budget12'),
                
                ('Label Current Amount', 1, 0, 'text',
                    lambda x, d, p: 'Current Actual'),
                ('Label Current Budget', 1, 0, 'text',
                    lambda x, d, p: 'Current Budget'),
                      
                ('Label Journal Entries ID', 1, 0, 'text',
                    lambda x, d, p: 'Journal Entries ID'),
                
                ('Label Journal Item ID', 1, 0, 'text',
                    lambda x, d, p: 'Journal Item ID'),
                      
                #####################################
                
                #################Raw Data############
                ('Data Division', 1, 0, 'text',
                    lambda x, d, p: x['division']),
                ('Data Department', 1, 0, 'text',
                    lambda x, d, p: x['department']),
                      
                ('Data DigitCOA', 1, 0, 'number',
                    lambda x, d, p: x['digit_coa']),
                ('Data Parent Account', 1, 0, 'text',
                    lambda x, d, p: x['parent_account']),
                ('Data Account', 1, 0, 'text',
                    lambda x, d, p: x['account']),
                
                ('Data DigitAnalytic', 1, 0, 'text',
                    lambda x, d, p: x['digit_analytic']),
                ('Data Parent Analytic Code Name', 1, 0, 'text',
                    lambda x, d, p: x['parent_analytic_code_name']),
                ('Data Analytic Code Name', 1, 0, 'text',
                    lambda x, d, p: x['analytic_code_name']),
                
                ('Data Analytic Account', 1, 0, 'text',
                    lambda x, d, p: x['analytic_account']),
                ('Data Analytic COA Code', 1, 0, 'text',
                    lambda x, d, p: x['analytic_coa_code']),
                
                ('Data Parent Category', 1, 0, 'text',
                    lambda x, d, p: x['parent_category']),
                ('Data Category', 1, 0, 'text',
                    lambda x, d, p: x['category']),
                      
                
                ('Data Journal', 1, 0, 'text',
                    lambda x, d, p: x['journal']),
                ('Data Move', 1, 0, 'text',
                    lambda x, d, p: x['move']),
                ('Data Name', 1, 0, 'text',
                    lambda x, d, p: x['name']),  
                ('Data Ref', 1, 0, 'text',
                    lambda x, d, p: x['ref']), 
                ('Data Description', 1, 0, 'text',
                    lambda x, d, p: x['description']),   
                ('Data Partner', 1, 0, 'text',
                    lambda x, d, p: x['partner']),
                ('Data Period', 1, 0, 'text',
                    lambda x, d, p: x['period']),
                ('Data Process Date', 1, 0, 'text',
                    lambda x, d, p: x['process_date']),
                ('Data Get Period', 1, 0, 'text',
                    lambda x, d, p: x['get_periods']),
                ('Data Date', 1, 0, 'text',
                    lambda x, d, p: x['date']),
                ('Data Create Date', 1, 0, 'text',
                    lambda x, d, p: x['create_date']),
                
                ('Data Actual Amount', 1, 0, 'number',
                    lambda x, d, p: x['actual_amount']),
                ('Data Budget YTD', 1, 0, 'number',
                    lambda x, d, p: x['budget_ytd']),
                ('Data Budget Amount', 1, 0, 'number',
                    lambda x, d, p: x['budget_amount']),
                
                ('Data Actual01', 1, 0, 'number',
                    lambda x, d, p: x['Actual01']),
                ('Data Actual02', 1, 0, 'number',
                    lambda x, d, p: x['Actual02']),
                ('Data Actual03', 1, 0, 'number',
                    lambda x, d, p: x['Actual03']),
                ('Data Actual04', 1, 0, 'number',
                    lambda x, d, p: x['Actual04']),
                ('Data Actual05', 1, 0, 'number',
                    lambda x, d, p: x['Actual05']),
                ('Data Actual06', 1, 0, 'number',
                    lambda x, d, p: x['Actual06']),
                ('Data Actual07', 1, 0, 'number',
                    lambda x, d, p: x['Actual07']),
                ('Data Actual08', 1, 0, 'number',
                    lambda x, d, p: x['Actual08']),
                ('Data Actual09', 1, 0, 'number',
                    lambda x, d, p: x['Actual09']),
                ('Data Actual10', 1, 0, 'number',
                    lambda x, d, p: x['Actual10']),
                ('Data Actual11', 1, 0, 'number',
                    lambda x, d, p: x['Actual11']),
                ('Data Actual12', 1, 0, 'number',
                    lambda x, d, p: x['Actual12']),
                      
                ('Data Budget01', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Budget02', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Budget03', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Budget04', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Budget05', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Budget06', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Budget07', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Budget08', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Budget09', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Budget10', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Budget11', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Budget12', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                
                ('Data Current Amount', 1, 0, 'number',
                    lambda x, d, p: x['current_amount']),
                ('Data Current Budget', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                      
                ('Data Journal Entries ID', 1, 0, 'text',
                    lambda x, d, p: x['data_journal_entries_id']),
                
                ('Data Journal Item ID', 1, 0, 'text',
                    lambda x, d, p: x['data_journal_item_id']),
                
                #####################################
                
                
                #################Raw Data Budget############
                ('Data Division Budget', 1, 0, 'text',
                    lambda x, d, p: x['division_budget']),
                ('Data Department Budget', 1, 0, 'text',
                    lambda x, d, p: x['department_budget']),
                
                ('Data DigitCOA Budget', 1, 0, 'number',
                    lambda x, d, p: x['digit_coa_budget']),
                ('Data Parent Account Budget', 1, 0, 'text',
                    lambda x, d, p: x['parent_account_budget']),
                ('Data Account Budget', 1, 0, 'text',
                    lambda x, d, p: x['account_budget']),
                
                ('Data DigitAnalytic Budget', 1, 0, 'text',
                    lambda x, d, p: x['digit_analytic_budget']),
                ('Data Parent Analytic Code Name Budget', 1, 0, 'text',
                    lambda x, d, p: x['parent_analytic_code_name_budget']),
                ('Data Analytic Code Name Budget', 1, 0, 'text',
                    lambda x, d, p: x['analytic_code_name_budget']),
                
                ('Data Analytic Account Budget', 1, 0, 'text',
                    lambda x, d, p: x['analytic_account_budget']),
                      
                ('Data Analytic COA Code Budget', 1, 0, 'text',
                    lambda x, d, p: x['analytic_coa_code_budget']),                      
                ('Data Parent Category Budget', 1, 0, 'text',
                    lambda x, d, p: x['parent_category_budget']),
                ('Data Category Budget', 1, 0, 'text',
                    lambda x, d, p: x['category_budget']),
                
                
                ('Data Journal Budget', 1, 0, 'text',
                    lambda x, d, p: x['journal_budget']),
                ('Data Move Budget', 1, 0, 'text',
                    lambda x, d, p: x['move_budget']),
                ('Data Name Budget', 1, 0, 'text',
                    lambda x, d, p: x['name_budget']),  
                ('Data Ref Budget', 1, 0, 'text',
                    lambda x, d, p: x['ref_budget']),    
                ('Data Description Budget', 1, 0, 'text',
                    lambda x, d, p: x['description_budget']),
                ('Data Partner Budget', 1, 0, 'text',
                    lambda x, d, p: x['partner_budget']),
                ('Data Period Budget', 1, 0, 'text',
                    lambda x, d, p: x['period_budget']),
                ('Data Process Date Budget', 1, 0, 'text',
                    lambda x, d, p: x['process_date_budget']),
                ('Data Get Period Budget', 1, 0, 'text',
                    lambda x, d, p: x['get_periods_budget']),
                ('Data Date Budget', 1, 0, 'text',
                    lambda x, d, p: x['date_budget']),
                ('Data Create Date Budget', 1, 0, 'text',
                    lambda x, d, p: x['create_date_budget']),  
                ('Data Actual Amount Budget', 1, 0, 'number',
                    lambda x, d, p: x['actual_amount_budget']),
                ('Data Budget YTD Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget_ytd_budget']),
                ('Data Budget Amount Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget_amount_budget']),
                
                ('Data Actual01 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                ('Data Actual02 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                ('Data Actual03 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                ('Data Actual04 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                ('Data Actual05 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                ('Data Actual06 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                ('Data Actual07 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                ('Data Actual08 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                ('Data Actual09 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                ('Data Actual10 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                ('Data Actual11 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                ('Data Actual12 Budget', 1, 0, 'number',
                    lambda x, d, p: 0.0),
                      
                ('Data Budget01 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget01budget']),
                ('Data Budget02 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget02budget']),
                ('Data Budget03 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget03budget']),
                ('Data Budget04 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget04budget']),
                ('Data Budget05 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget05budget']),
                ('Data Budget06 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget06budget']),
                ('Data Budget07 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget07budget']),
                ('Data Budget08 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget08budget']),
                ('Data Budget09 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget09budget']),
                ('Data Budget10 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget10budget']),
                ('Data Budget11 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget11budget']),
                ('Data Budget12 Budget', 1, 0, 'number',
                    lambda x, d, p: x['budget12budget']),
                
                ('Data Current Amount Budget', 1, 0, 'number',
                    lambda x, d, p: '0.0'),
                ('Data Current Budget Budget', 1, 0, 'number',
                    lambda x, d, p: x['current_amount_budget']),
                      
                ('Data Journal Entries ID Budget', 1, 0, 'text',
                    lambda x, d, p: ''),
                
                ('Data Journal Item ID Budget', 1, 0, 'text',
                    lambda x, d, p: ''),
                
                #####################################
                
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
        
        label_data = self.xls_row_template(cols_specs, [
                                                        'Label Division',
                                                        'Label Department',
                                                        
                                                        'Label DigitCOA',
                                                        'Label Parent Account',
                                                        'Label Account',
                                                        
                                                        'Label DigitAnalytic',
                                                        'Label Parent Analytic Code Name',
                                                        'Label Analytic Code Name',
                                                        
                                                        'Label Analytic Account',
                                                        'Label Analytic COA Code',
                                                        'Label Parent Category',
                                                        'Label Category',
                                                        
                                                        'Label Journal',
                                                        'Label Move',
                                                        'Label Name',
                                                        'Label Ref',
                                                        'Label Description',
                                                        'Label Partner',
                                                        'Label Period',
                                                        'Label Process Date',
                                                        'Label Get Period',
                                                        'Label Date',
                                                        'Label Create Date',
                                                        'Label Actual Amount',
                                                        'Label Budget YTD',
                                                        'Label Budget Amount',
                                                        
                                                        'Label Actual01',
                                                        'Label Actual02',
                                                        'Label Actual03',
                                                        'Label Actual04',
                                                        'Label Actual05',
                                                        'Label Actual06',
                                                        'Label Actual07',
                                                        'Label Actual08',
                                                        'Label Actual09',
                                                        'Label Actual10',
                                                        'Label Actual11',
                                                        'Label Actual12',
                                                        
                                                        'Label Budget01',
                                                        'Label Budget02',
                                                        'Label Budget03',
                                                        'Label Budget04',
                                                        'Label Budget05',
                                                        'Label Budget06',
                                                        'Label Budget07',
                                                        'Label Budget08',
                                                        'Label Budget09',
                                                        'Label Budget10',
                                                        'Label Budget11',
                                                        'Label Budget12',
                                                                              
                                                        'Label Current Amount',
                                                        'Label Current Budget',  
                                                        
                                                        'Label Journal Entries ID',
                                                        'Label Journal Item ID',
                                                      ])
        
        row_data = self.xls_row_template(cols_specs, [
                                                      'Data Division',
                                                        'Data Department',
                                                        
                                                        'Data DigitCOA',
                                                        'Data Parent Account',
                                                        'Data Account',
                                                        
                                                        'Data DigitAnalytic',
                                                        'Data Parent Analytic Code Name',
                                                        'Data Analytic Code Name',
                                                        
                                                        'Data Analytic Account',
                                                        'Data Analytic COA Code',
                                                        'Data Parent Category',
                                                        'Data Category',
                                                        
                                                        'Data Journal',
                                                        'Data Move',
                                                        'Data Name',
                                                        'Data Ref',
                                                        'Data Description',
                                                        'Data Partner',
                                                        'Data Period',
                                                        'Data Process Date',
                                                        'Data Get Period',
                                                        'Data Date',
                                                        'Data Create Date',
                                                        'Data Actual Amount',
                                                        'Data Budget YTD',
                                                        'Data Budget Amount',
                                                        
                                                        'Data Actual01',
                                                        'Data Actual02',
                                                        'Data Actual03',
                                                        'Data Actual04',
                                                        'Data Actual05',
                                                        'Data Actual06',
                                                        'Data Actual07',
                                                        'Data Actual08',
                                                        'Data Actual09',
                                                        'Data Actual10',
                                                        'Data Actual11',
                                                        'Data Actual12',
                                                        
                                                        'Data Budget01',
                                                        'Data Budget02',
                                                        'Data Budget03',
                                                        'Data Budget04',
                                                        'Data Budget05',
                                                        'Data Budget06',
                                                        'Data Budget07',
                                                        'Data Budget08',
                                                        'Data Budget09',
                                                        'Data Budget10',
                                                        'Data Budget11',
                                                        'Data Budget12',
                                                                              
                                                        'Data Current Amount',
                                                        'Data Current Budget',  
                                                      
                                                      
#                                                        'Data Division',
#                                                        'Data Department',
#                                                        
#                                                        'Data DigitCOA',
#                                                        'Data Parent Account',
#                                                        'Data Account',
#                                                        
#                                                        'Data DigitAnalytic',
#                                                        'Data Parent Analytic Code Name',
#                                                        'Data Analytic Code Name',
#                                                        
#                                                        'Data Analytic Account',
#                                                        'Data Parent Category',
#                                                        'Data Category',
#                                                        
#                                                        'Data Date',
#                                                        'Data Journal',
#                                                        'Data Move',
#                                                        'Data Name',
#                                                        'Data Partner',
#                                                        'Data Period',
#                                                        'Data Ref',
#                                                        'Data Actual Amount',
#                                                        'Data Process Date',
#                                                        'Data Budget Amount',
#                                                        
#                                                        'Data Description',
#                                                        
#                                                        'Data Create Date',
#                                                        
#                                                        'Data Get Period',
#                                                        
#                                                        'Data Current Amount',
#                                                        'Data Current Budget',
#                                                        'Data Budget YTD',
#                                                        'Data Actual01',
#                                                        'Data Actual02',
#                                                        'Data Actual03',
#                                                        'Data Actual04',
#                                                        'Data Actual05',
#                                                        'Data Actual06',
#                                                        'Data Actual07',
#                                                        'Data Actual08',
#                                                        'Data Actual09',
#                                                        'Data Actual10',
#                                                        'Data Actual11',
#                                                        'Data Actual12',
#                                                        
#                                                        'Data Budget01',
#                                                        'Data Budget02',
#                                                        'Data Budget03',
#                                                        'Data Budget04',
#                                                        'Data Budget05',
#                                                        'Data Budget06',
#                                                        'Data Budget07',
#                                                        'Data Budget08',
#                                                        'Data Budget09',
#                                                        'Data Budget10',
#                                                        'Data Budget11',
#                                                        'Data Budget12',
                                                        
                                                        'Data Journal Entries ID',
                                                        'Data Journal Item ID',
                                                        
                                                      ])
        
        row_data_budget = self.xls_row_template(cols_specs, [
                                                        'Data Division Budget',
                                                        'Data Department Budget',
                                                        
                                                        'Data DigitCOA Budget',
                                                        'Data Parent Account Budget',
                                                        'Data Account Budget',
                                                        
                                                        'Data DigitAnalytic Budget',
                                                        'Data Parent Analytic Code Name Budget',
                                                        'Data Analytic Code Name Budget',
                                                        
                                                        'Data Analytic Account Budget',
                                                        'Data Analytic COA Code Budget',
                                                        'Data Parent Category Budget',
                                                        'Data Category Budget',
                                                        
                                                        'Data Journal Budget',
                                                        'Data Move Budget',
                                                        'Data Name Budget',
                                                        'Data Ref Budget',
                                                        'Data Description Budget',
                                                        'Data Partner Budget',
                                                        'Data Period Budget',
                                                        'Data Process Date Budget',
                                                        'Data Get Period Budget',
                                                        'Data Date Budget',
                                                        'Data Create Date Budget',
                                                        'Data Actual Amount Budget',
                                                        'Data Budget YTD Budget',
                                                        'Data Budget Amount Budget',
                                                        
                                                        'Data Actual01 Budget',
                                                        'Data Actual02 Budget',
                                                        'Data Actual03 Budget',
                                                        'Data Actual04 Budget',
                                                        'Data Actual05 Budget',
                                                        'Data Actual06 Budget',
                                                        'Data Actual07 Budget',
                                                        'Data Actual08 Budget',
                                                        'Data Actual09 Budget',
                                                        'Data Actual10 Budget',
                                                        'Data Actual11 Budget',
                                                        'Data Actual12 Budget',
                                                        
                                                        'Data Budget01 Budget',
                                                        'Data Budget02 Budget',
                                                        'Data Budget03 Budget',
                                                        'Data Budget04 Budget',
                                                        'Data Budget05 Budget',
                                                        'Data Budget06 Budget',
                                                        'Data Budget07 Budget',
                                                        'Data Budget08 Budget',
                                                        'Data Budget09 Budget',
                                                        'Data Budget10 Budget',
                                                        'Data Budget11 Budget',
                                                        'Data Budget12 Budget',
                                                                              
                                                        'Data Current Amount Budget',
                                                        'Data Current Budget Budget',  
                                                        
                                                        
                                                        
#                                                        'Data Division Budget',
#                                                        'Data Department Budget',
#                                                        
#                                                        'Data DigitCOA Budget',
#                                                        'Data Parent Account Budget',
#                                                        'Data Account Budget',
#                                                        
#                                                        'Data DigitAnalytic Budget',
#                                                        'Data Parent Analytic Code Name Budget',
#                                                        'Data Analytic Code Name Budget',
#                                                        
#                                                        'Data Analytic Account Budget',
#                                                        'Data Parent Category Budget',
#                                                        'Data Category Budget',
#                                                        
#                                                        'Data Date Budget',
#                                                        'Data Journal Budget',
#                                                        'Data Move Budget',
#                                                        'Data Name Budget',
#                                                        'Data Partner Budget',
#                                                        'Data Period Budget',
#                                                        'Data Ref Budget',
#                                                        'Data Actual Amount Budget',
#                                                        'Data Process Date Budget',
#                                                        'Data Budget Amount Budget',
#                                                        
#                                                        'Data Description Budget',
#                                                        
#                                                        'Data Create Date Budget',
#                                                        
#                                                        'Data Get Period Budget',
#                                                        
#                                                        'Data Current Amount Budget',
#                                                        'Data Current Budget Budget',
#                                                        'Data Budget YTD Budget',
#                                                        
#                                                        'Data Actual01 Budget',
#                                                        'Data Actual02 Budget',
#                                                        'Data Actual03 Budget',
#                                                        'Data Actual04 Budget',
#                                                        'Data Actual05 Budget',
#                                                        'Data Actual06 Budget',
#                                                        'Data Actual07 Budget',
#                                                        'Data Actual08 Budget',
#                                                        'Data Actual09 Budget',
#                                                        'Data Actual10 Budget',
#                                                        'Data Actual11 Budget',
#                                                        'Data Actual12 Budget',
#                                                        
#                                                        'Data Budget01 Budget',
#                                                        'Data Budget02 Budget',
#                                                        'Data Budget03 Budget',
#                                                        'Data Budget04 Budget',
#                                                        'Data Budget05 Budget',
#                                                        'Data Budget06 Budget',
#                                                        'Data Budget07 Budget',
#                                                        'Data Budget08 Budget',
#                                                        'Data Budget09 Budget',
#                                                        'Data Budget10 Budget',
#                                                        'Data Budget11 Budget',
#                                                        'Data Budget12 Budget',
                                                        'Data Journal Entries ID Budget',
                                                        'Data Journal Item ID Budget',
                                                      ])
        
        
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
        #c = parser._get_data(data)
        #print "x___________________", c
        #self.xls_write_row(ws, None, data, parser, 0, row_hdr0, tittle_style0)
        #self.xls_write_row(ws, None, data, parser, 1, row_hdr1, tittle_style1)
        #self.xls_write_row(ws, None, data, parser, 2, row_hdr2, tittle_style2)
        #self.xls_write_row(ws, {'date' : c['result_date_start'] +' s/d '+ c['result_date_end']}, data, parser, 3, row_hdr3, tittle_style3)
        #self.xls_write_row(ws, None, data, parser, 4, row_hdr4, tittle_style4)
        #self.xls_write_row(ws, None, data, parser, 5, row_hdr5, tittle_style5)
        
        
        
        #self.xls_write_row(ws, None, data, parser, 6, row_hdr0, tittle_style0)
        row_count = 0
        no        = 0 
        amount    = 0.0
        parent_categ    = ""
        tot_parent_amount   = 0.0
        
        self.xls_write_row(ws, None, data, parser, 0, label_data, tittle_style3)
        row_count += 1
        
        process_date        = datetime.datetime.today().strftime('%d-%b-%y')
        #print "QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ", data['period_end']
        start_date_period   = parser._get_start_date_period(data)
        current_date_start  = parser._get_current_date_start(data)
        current_date_end    = parser._get_current_date_end(data)
        
        print "current_date_start", current_date_start
        #current_date_end    = self.get_date(data['period_end'])
        #print "data-------------------------*************************>", data['form']['period_start']
        
        
        date01 = parser._last_day_of_month(data, '-01-01')
        date02 = parser._last_day_of_month(data, '-02-01') 
        date03 = parser._last_day_of_month(data, '-03-01')
        date04 = parser._last_day_of_month(data, '-04-01')
        date05 = parser._last_day_of_month(data, '-05-01') 
        date06 = parser._last_day_of_month(data, '-06-01') 
        date07 = parser._last_day_of_month(data, '-07-01') 
        date08 = parser._last_day_of_month(data, '-08-01') 
        date09 = parser._last_day_of_month(data, '-09-01') 
        date10 = parser._last_day_of_month(data, '-10-01') 
        date11 = parser._last_day_of_month(data, '-11-01') 
        date12 = parser._last_day_of_month(data, '-12-01')
        
       
        
        print "date01xxxxxxxxxxxxxxxxxxx", date01
        print "date06xxxxxxxxxxxxxxxxxxx", date06
        
        get_periods         = parser._get_periods(data)
        get_range_periods   = parser._get_range_periods(data, start_date_period, current_date_end)
        
        for move_line in parser._get_move_line(data):
            account             = move_line.account_id.code +" - "+move_line.account_id.name
            analytic_account    = move_line.analytic_account_id.code
            date                = move_line.date
            journal             = move_line.journal_id.name
            move                = move_line.move_id.name
            name                = move_line.name
            partner             = move_line.partner_id.name
            period              = move_line.period_id.name
            ref                 = move_line.ref
            
            parent_account      = move_line.account_id.parent_id.code +" - "+ move_line.account_id.parent_id.name
            actual_amount       = (move_line.debit - move_line.credit)#Year To Date Amount
            budget_amount       = 0.0
            
            department          = ""
            division            = ""
            if move_line.analytic_account_id.department_id:
                department      = move_line.analytic_account_id.department_id.name
                if move_line.analytic_account_id.department_id.division_id:
                    division    = move_line.analytic_account_id.department_id.division_id.name
            
            description         = move_line.narration
            current_amount      = 0.0
            if date >= current_date_start and date <= current_date_end: 
                current_amount      = (move_line.debit - move_line.credit)
            
            if move_line.account_id.sub_cashflow_category_id :
                category            = move_line.account_id.sub_cashflow_category_id.name
                parent_category     = move_line.account_id.sub_cashflow_category_id.category_id.name
            else:
                category            = ""
                parent_category     = ""
                
            digit_coa               = move_line.account_id.code[0]
            analytic_code_name      = ""
            parent_analytic_code_name      = ""
            digit_analytic          = ""
            analytic_coa_code       = ""
            if move_line.analytic_account_id:
                analytic_coa_code               = move_line.analytic_account_id.budget_expense.code
                analytic_code_name              = re.split(' ',move_line.analytic_account_id.code)[1] +" - "+move_line.analytic_account_id.name
                parent_analytic_code_name       = re.split(' ',move_line.analytic_account_id.parent_id.code)[1] +" - "+move_line.analytic_account_id.parent_id.name
            
                digit_analytic          = re.split(' ',move_line.analytic_account_id.code)[1][0]
            get_periods             = get_periods
            
            data_journal_entries_id = str(move_line.move_id.id)
            data_journal_item_id    = str(move_line.id)
            
            actual01 = 0.0
            actual02 = 0.0
            actual03 = 0.0
            actual04 = 0.0
            actual05 = 0.0
            actual06 = 0.0
            actual07 = 0.0
            actual08 = 0.0
            actual09 = 0.0
            actual10 = 0.0
            actual11 = 0.0
            actual12 = 0.0
            
            budget01 = 0.0
            budget02 = 0.0
            budget03 = 0.0
            budget04 = 0.0
            budget05 = 0.0
            budget06 = 0.0
            budget07 = 0.0
            budget08 = 0.0
            budget09 = 0.0
            budget10 = 0.0
            budget11 = 0.0
            budget12 = 0.0
            
            #print "date>>>>>>>>>>", type(time.strptime(date,"%Y-%m-%d")), type(date01['start_month'])
            #print "date??????????????", date, date01
            
            if time.strptime(date,"%Y-%m-%d") >= time.strptime(date01['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date01['end_month'], "%Y-%m-%d"):
                #print "MASUK", "date>>>>>>>>>>", type(date), type(date01['start_month']), type(date01['end_month'])
                actual01 = (move_line.debit - move_line.credit)
            elif time.strptime(date,"%Y-%m-%d") >= time.strptime(date02['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date02['end_month'], "%Y-%m-%d"):
                actual02 = (move_line.debit - move_line.credit)
            elif time.strptime(date,"%Y-%m-%d") >= time.strptime(date03['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date03['end_month'], "%Y-%m-%d"):
                actual03 = (move_line.debit - move_line.credit)
            elif time.strptime(date,"%Y-%m-%d") >= time.strptime(date04['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date04['end_month'], "%Y-%m-%d"):
                actual04 = (move_line.debit - move_line.credit)
            elif time.strptime(date,"%Y-%m-%d") >= time.strptime(date05['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date05['end_month'], "%Y-%m-%d"):
                actual05 = (move_line.debit - move_line.credit)
            elif time.strptime(date,"%Y-%m-%d") >= time.strptime(date06['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date06['end_month'], "%Y-%m-%d"):
                actual06 = (move_line.debit - move_line.credit)
            elif time.strptime(date,"%Y-%m-%d") >= time.strptime(date07['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date07['end_month'], "%Y-%m-%d"):
                actual07 = (move_line.debit - move_line.credit)
            elif time.strptime(date,"%Y-%m-%d") >= time.strptime(date08['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date08['end_month'], "%Y-%m-%d"):
                actual08 = (move_line.debit - move_line.credit)
            elif time.strptime(date,"%Y-%m-%d") >= time.strptime(date09['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date09['end_month'], "%Y-%m-%d"):
                actual09 = (move_line.debit - move_line.credit)
            elif time.strptime(date,"%Y-%m-%d") >= time.strptime(date10['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date10['end_month'], "%Y-%m-%d"):
                actual10 = (move_line.debit - move_line.credit)
            elif time.strptime(date,"%Y-%m-%d") >= time.strptime(date11['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date11['end_month'], "%Y-%m-%d"):
                actual11 = (move_line.debit - move_line.credit)
            elif time.strptime(date,"%Y-%m-%d") >= time.strptime(date12['start_month'], "%Y-%m-%d") and time.strptime(date,"%Y-%m-%d") <= time.strptime(date12['end_month'], "%Y-%m-%d"):
                actual12 = (move_line.debit - move_line.credit)
            
            #print "qqqqqqqqqqqqqqqqqqqqqqqqqqq", date['start_month']
            
            create_date             = parser._get_create_date_move_line(move_line.id)
            self.xls_write_row(ws, {
                                    'account'           : account,
                                    'analytic_account'  : analytic_account,
                                    'date'              : date,
                                    'journal'           : journal,
                                    'move'              : move,
                                    'name'              : name,
                                    'partner'           : partner,
                                    'period'            : period,
                                    'ref'               : ref,
                                    'parent_account'    : parent_account,
                                    'actual_amount'     : actual_amount,
                                    'process_date'      : process_date,
                                    'budget_amount'     : budget_amount,
                                    'department'        : department,
                                    'division'          : division,
                                    'description'       : description,
                                    'category'          : category,
                                    'parent_category'   : parent_category,
                                    'create_date'       : create_date,
                                    'current_amount'    : current_amount,
                                    'current_budget'    : 0.0,
                                    'budget_ytd'        : 0.0,
                                    
                                    'Actual01'          : actual01,
                                    'Actual02'          : actual02,
                                    'Actual03'          : actual03,
                                    'Actual04'          : actual04,
                                    'Actual05'          : actual05,
                                    'Actual06'          : actual06,
                                    'Actual07'          : actual07,
                                    'Actual08'          : actual08,
                                    'Actual09'          : actual09,
                                    'Actual10'          : actual10,
                                    'Actual11'          : actual11,
                                    'Actual12'          : actual12,
                                    
                                    'Budget01'          : budget01,
                                    'Budget02'          : budget02,
                                    'Budget03'          : budget03,
                                    'Budget04'          : budget04,
                                    'Budget05'          : budget05,
                                    'Budget06'          : budget06,
                                    'Budget07'          : budget07,
                                    'Budget08'          : budget08,
                                    'Budget09'          : budget09,
                                    'Budget10'          : budget10,
                                    'Budget11'          : budget11,
                                    'Budget12'          : budget12,
                                    'digit_coa'         : digit_coa,
                                    'analytic_code_name': analytic_code_name,
                                    'parent_analytic_code_name' : parent_analytic_code_name,
                                    'digit_analytic' : digit_analytic,
                                    'get_periods' : get_periods,
                                    'analytic_coa_code' : analytic_coa_code,
                                    'data_journal_entries_id' : data_journal_entries_id,
                                    'data_journal_item_id' : data_journal_item_id,
                                    
                                    }, data, parser, row_count, row_data, normal_style)
            row_count += 1
        
        #row_count += 1
        for budget_line in parser._get_budget_line(data):
            account_budget             = budget_line.budget_item_id.code +" - "+ budget_line.analytic_account_id.budget_expense.name
            analytic_account_budget    = budget_line.analytic_account_id.code
            date_budget                = budget_line.period_id.date_start
            journal_budget             = ""
            move_budget                = ""
            name_budget                = budget_line.name
            partner_budget             = ""
            period_budget              = budget_line.period_id.name
            ref_budget                 = ""
            
            parent_account_budget      = budget_line.budget_item_id.parent_id.code +" - "+ budget_line.budget_item_id.parent_id.name
            actual_amount_budget       = 0.0
            budget_amount_budget       = budget_line.amount
            
            department_budget          = budget_line.dept_relation.name
            division_budget            = budget_line.div_relation.name
            description_budget         = ""
            analytic_coa_code_budget   = budget_line.analytic_account_id.budget_expense.code
            
            if budget_line.analytic_account_id and budget_line.analytic_account_id.budget_expense and budget_line.analytic_account_id.budget_expense.sub_cashflow_category_id:
                category_budget         = budget_line.analytic_account_id.budget_expense.sub_cashflow_category_id.name
                parent_category_budget  = budget_line.analytic_account_id.budget_expense.sub_cashflow_category_id.category_id.name
            else:
                category_budget         = ""
                parent_category_budget  = ""
                
            current_amount_budget       = 0.0
            digit_coa_budget            = budget_line.analytic_account_id.budget_expense.code[0]
            
            if budget_line.period_id.id == data['form']['period_end']:
                current_amount_budget   = budget_amount_budget
            
            analytic_code_name_budget      = re.split(' ',budget_line.analytic_account_id.code)[1] +" - "+budget_line.analytic_account_id.name
            parent_analytic_code_name_budget = re.split(' ',budget_line.analytic_account_id.parent_id.code)[1] +" - "+budget_line.analytic_account_id.parent_id.name
            
            digit_analytic_budget          = re.split(' ',budget_line.analytic_account_id.code)[1][0]
            get_periods_budget             = 'yyyyyy'
            
            #get_range_periods               = 
            budget_ytd_budget       = 0.0
            if budget_line.period_id.id in get_range_periods:
                budget_ytd_budget = budget_amount_budget
            
            budget01budget = 0.0
            budget02budget = 0.0
            budget03budget = 0.0
            budget04budget = 0.0
            budget05budget = 0.0
            budget06budget = 0.0
            budget07budget = 0.0
            budget08budget = 0.0
            budget09budget = 0.0
            budget10budget = 0.0
            budget11budget = 0.0
            budget12budget = 0.0
            
            #print "**************************************", budget_line.period_id.date_start, type(date01['start_month'])
            #print "######################", type(budget_line.period_id.date_start), time.strptime(date01['start_month'], "%Y-%m-%d")
            if time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date01['start_month'], "%Y-%m-%d"):
                budget01budget = budget_amount_budget
            elif time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date02['start_month'], "%Y-%m-%d"):
                budget02budget = budget_amount_budget
            elif time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date03['start_month'], "%Y-%m-%d"):
                budget03budget = budget_amount_budget
            elif time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date04['start_month'], "%Y-%m-%d"):
                budget04budget = budget_amount_budget
            elif time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date05['start_month'], "%Y-%m-%d"):
                budget05budget = budget_amount_budget
            elif time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date06['start_month'], "%Y-%m-%d"):
                budget06budget = budget_amount_budget
            elif time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date07['start_month'], "%Y-%m-%d"):
                budget07budget = budget_amount_budget
            elif time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date08['start_month'], "%Y-%m-%d"):
                budget08budget = budget_amount_budget
            elif time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date09['start_month'], "%Y-%m-%d"):
                budget09budget = budget_amount_budget
            elif time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date10['start_month'], "%Y-%m-%d"):
                budget10budget = budget_amount_budget
            elif time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date11['start_month'], "%Y-%m-%d"):
                budget11budget = budget_amount_budget
            elif time.strptime(budget_line.period_id.date_start, "%Y-%m-%d") == time.strptime(date12['start_month'], "%Y-%m-%d"):
                budget12budget = budget_amount_budget



                
            
            create_date_budget          = parser._get_create_date_budget(budget_line.id)
            
            self.xls_write_row(ws, {
                                    'account_budget'           : account_budget,
                                    'analytic_account_budget'  : analytic_account_budget,
                                    'date_budget'              : date_budget,
                                    'journal_budget'           : journal_budget,
                                    'move_budget'              : move_budget,
                                    'name_budget'              : name_budget,
                                    'partner_budget'           : partner_budget,
                                    'period_budget'            : period_budget,
                                    'ref_budget'               : ref_budget,
                                    'parent_account_budget'    : parent_account_budget,
                                    'actual_amount_budget'     : actual_amount_budget,
                                    'process_date_budget'      : process_date,
                                    'budget_amount_budget'     : budget_amount_budget,
                                    'department_budget'        : department_budget,
                                    'division_budget'          : division_budget,
                                    'description_budget'       : description_budget,
                                    'category_budget'          : category_budget,
                                    'parent_category_budget'   : parent_category_budget,
                                    'create_date_budget'       : create_date_budget,
                                    'current_amount_budget'    : current_amount_budget,
                                    'budget_ytd_budget'        : budget_ytd_budget,
                                    
                                    'budget01budget'          : budget01budget,
                                    'budget02budget'          : budget02budget,
                                    'budget03budget'          : budget03budget,
                                    'budget04budget'          : budget04budget,
                                    'budget05budget'          : budget05budget,
                                    'budget06budget'          : budget06budget,
                                    'budget07budget'          : budget07budget,
                                    'budget08budget'          : budget08budget,
                                    'budget09budget'          : budget09budget,
                                    'budget10budget'          : budget10budget,
                                    'budget11budget'          : budget11budget,
                                    'budget12budget'          : budget12budget,
                                    
                                    'digit_coa_budget'          : digit_coa_budget,
                                    'analytic_code_name_budget' : analytic_code_name_budget,
                                    'parent_analytic_code_name_budget' : parent_analytic_code_name_budget,
                                    
                                    'digit_analytic_budget' : digit_analytic_budget,
                                    'get_periods_budget' : get_periods,
                                    'analytic_coa_code_budget' : analytic_coa_code_budget,
                                    
                                    }, data, parser, row_count, row_data_budget, normal_style)
            row_count += 1
            
        pass

account_raw_data_report_xls(
        'report.raw.data.report.xls',
        'account.move.line',
        'addons/account/report/account_balance_sheet_horizontal.rml',
        parser=raw_data_report,
        header=False)
