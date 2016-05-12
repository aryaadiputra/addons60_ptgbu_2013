# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import time
from report import report_sxw
from tools import amount_to_text_en


class report_print_check(report_sxw.rml_parse):
    '''
    Class to parse check report
    '''
    def __init__(self, cr, uid, name, context):
        super(report_print_check, self).__init__(cr, uid, name, context)
        self.number_lines = 0
        self.number_add = 0
        self.localcontext.update({
            'time': time,
            'get_lines': self.get_lines,
            'fill_stars' : self.fill_stars,
            'find_lang':self.find_lang,
            'get_zip_line':self.get_zip_line,
            'chk_no':self.get_chk_no,
        })
    def get_chk_no(self, voucher):
        '''
        return the check number
        '''
        if voucher.journal_id.use_preprint_check:
            ret = ' '
        else:
            ret = voucher.chk_seq or ' '
        return ret
    def get_zip_line(self, address):
        '''
        Get the address line
        '''
        ret = ''
        if address:
            address_obj = address[0]
            if 'zip_id' in address_obj._columns.keys():
                if address_obj.city:
                    ret += address_obj.city
                if address_obj.state_id:
                    if address_obj.state_id.name:
                        if ret:
                            ret += ', '
                        ret += address_obj.state_id.code
                if address_obj.zip_id:
                    if address_obj.zip_id.zipcode:
                        if ret:
                            ret += ' '
                        ret += address_obj.zip_id.zipcode
            else:
                if address_obj.city_id:
                    if address_obj.city_id.name:
                        ret += address_obj.city_id.name
                    if address_obj.city_id.state_id:
                        if address_obj.city_id.state_id.code:
                            if ret:
                                ret += ', '
                            ret += address_obj.city_id.state_id.code
                    if address_obj.zip:
                        if ret:
                            ret += ' '
                        ret += address_obj.zip
        return ret

    def find_lang(self,):
        '''
        Find language of user
        '''
        return pooler.get_pool(self.cr.dbname).get('res.users').browse(self.cr, self.uid, self.uid).company_id.lang

    def fill_stars(self, amount):
        '''
        Fills stars after amount in words
        '''
        amount = amount.replace('Dollars','')
        if len(amount) < 100: #TODO
            stars = 100 - len(amount)
            return ' '.join([amount,'*'*stars])

        else: return amount


    def get_lines(self, voucher_lines):
        '''
        return date_original, name, amount_original, amount, amount_due, invoice and purchase order details of selected voucher lines
        '''
        result = []
        self.number_lines = len(voucher_lines)
        for num_i in range(0, self.number_lines):
            if num_i < self.number_lines:
                print 'discount_used' in voucher_lines[num_i]._columns
                res = {
                    'date_original' : voucher_lines[num_i].date_original,
                    'name' : voucher_lines[num_i].name,
                    'amount_original' : voucher_lines[num_i].amount_original and voucher_lines[num_i].amount_original or False,
                    'amount' : voucher_lines[num_i].amount and voucher_lines[num_i].amount or False,
                    'amount_due' : (voucher_lines[num_i].amount and voucher_lines[num_i].amount_unreconciled)and voucher_lines[num_i].amount_unreconciled - voucher_lines[num_i].amount or False,
                    'invoice' : voucher_lines[num_i].invoice_id and voucher_lines[num_i].invoice_id.inv_ref or voucher_lines[num_i].invoice_id.reference or ' ',
                    'pur_order' : voucher_lines[num_i].invoice_id and voucher_lines[num_i].invoice_id.origin or ' ',
                    'discount_used' : 'discount_used' in voucher_lines[num_i]._columns and voucher_lines[num_i].discount_used or ' ',
                }
            else :
                res = {
                    'date_original' : False,
                    'name' : False,
                    'amount_original' : False,
                    'amount_due' : False,
                    'amount' : False,
                    'invoice' : ' ',
                    'pur_order' : ' ',
                    'discount_used' : ' ',
                }
            if res.get('amount',False):
                result.append(res)
        result = result[:10]
        return result

report_sxw.report_sxw(
    'report.account.print.check.top',
    'account.voucher',
    'addons/account_check_writing/report/check_print_top.rml',
    parser=report_print_check,header=False
)

report_sxw.report_sxw(
    'report.account.print.check.middle',
    'account.voucher',
    'addons/account_check_writing/report/check_print_middle.rml',
    parser=report_print_check,header=False
)

report_sxw.report_sxw(
    'report.account.print.check.bottom',
    'account.voucher',
    'addons/account_check_writing/report/check_print_bottom.rml',
    parser=report_print_check,header=False
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
