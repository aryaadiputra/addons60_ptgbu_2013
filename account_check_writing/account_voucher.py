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

from osv import osv,fields
from tools.translate import _
from tools.amount_to_text_en import amount_to_text
from lxml import etree
from amount_to_words import amount_to_words

check_layout_report = {
    'top' : 'account.print.check.top',
    'middle' : 'account.print.check.middle',
    'bottom' : 'account.print.check.bottom',
}

# Check Number : Journal sequence number is generated when we confirm voucher/check.This number is assumed as check number in check writing : Need to keep track right number while printing manually.

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    _columns = {    
        'amount_in_word' : fields.char("Amount in word" , size=128, readonly=True, states={'draft':[('readonly',False)]}),
        'allow_check' : fields.boolean('Allow Check Writing'), # attrs does not support '.' format and fields.relates get the value when v save the record
        'chk_seq' : fields.char("Check Number" , size=64, readonly=True),
        'chk_status' : fields.boolean("Check Status" ),
    }
    

    def _get_journal(self, cr, uid, context=None):
        '''
        Function to initialise the variable journal_id
        '''
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        invoice_pool = self.pool.get('account.invoice')
        if context.get('invoice_id', False):
            currency_id = invoice_pool.browse(cr, uid, context['invoice_id'], context=context).currency_id.id
            journal_id = journal_pool.search(cr, uid, [('currency', '=', currency_id)], limit=1)
            return journal_id and journal_id[0] or False
        
        if context.get('journal_id', False):
            return context.get('journal_id')
        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            return context.get('search_default_journal_id')

        ttype = context.get('type', 'bank')

        if ttype in ('payment', 'receipt'):
            ttype = 'bank'
        if context.get('write_check',False) :           
            res = journal_pool.search(cr, uid, [('allow_check_writing', '=', True)], limit=1)
        else :
            res = journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
        return res and res[0] or False
        
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        """ Inherited - add amount_in_word in return value dictionary 
            cr: cursor
            uid: user id
            ids: ids of account voucher
            partner_id: partner's id
            journal_id: journal's id
            price: price
            currency_id: id of currency using
            date: date
            context: context
        """
        if not context:
            context = {}
        default = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=context)
        if 'value' in default:
            amount = 'amount' in default['value'] and default['value']['amount'] or price

            #TODO : generic amount_to_text is not ready yet, otherwise language and currency can be passed accordingly
            currency_format =  self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_format
            if currency_format=='us':
                amount_in_word = amount_to_words(amount)
            else: 
                amount_in_word = amount_to_text(amount)
            
            default['value'].update({'amount_in_word':amount_in_word})
            
            if journal_id:
                allow_check_writing = self.pool.get('account.journal').browse(cr, uid, journal_id).allow_check_writing
                default['value'].update({'allow_check':allow_check_writing})
        return default

    def print_check(self, cr, uid, ids, context=None):
        '''
        Function to print check
        '''
        if not ids: return []
        
        check_layout = self.browse(cr, uid, ids[0], context=context).company_id.check_layout
        
        return {
            'type': 'ir.actions.report.xml', 
            'report_name':check_layout_report[check_layout],
            'datas': {
                    'model':'account.voucher',
                    'id': ids and ids[0] or False,
                    'ids': ids and ids or [],
                    'report_type': 'pdf'
                },
            'nodestroy': True
            }


    _defaults = {
        'journal_id':_get_journal,
        'chk_status':False
        }

account_voucher()


'''
Code provided by openerp
'''
class account_voucher_line(osv.osv):
   _inherit = 'account.voucher.line'

   def write(self, cr, user, ids, vals, context=None):
       '''
           Add invoice and description in payment modification line
       '''
       if type(ids) == type([]):
           move = self.browse(cr, user,ids[0]).move_line_id
       else:
           move = self.browse(cr, user,ids).move_line_id
       if move:
           invoice_ids = self.pool.get('account.invoice').search(cr,user,[('move_id','=',move.move_id.id)])
           if invoice_ids:
               invoice = self.pool.get('account.invoice').browse(cr, user,invoice_ids[0])
               vals['invoice_id'] = invoice.id
               vals['name'] = invoice.number
       return super(account_voucher_line, self).write(cr, user, ids, vals, context)

   def create(self, cr, user, vals, context=None):
       '''
           Add invoice and description in payment modification line
       '''
       if vals.has_key('move_line_id') and vals['move_line_id']:
           move = self.pool.get('account.move.line').browse(cr, user,vals['move_line_id'])
           if move and move.move_id:
               invoice_ids = self.pool.get('account.invoice').search(cr,user,[('move_id','=',move.move_id.id)])
               if invoice_ids:
                   invoice = self.pool.get('account.invoice').browse(cr, user,invoice_ids[0])
                   vals['invoice_id'] = invoice.id
                   vals['name'] = invoice.number
       return super(account_voucher_line, self).create(cr, user, vals, context)
   def _get_due_date(self, cr, uid, ids, context=None):
        '''
            Store function to identify the voucher lines that need recalculation of date_due in the case of any change on account move line
            Fixme: make sure that it return a list of voucher line id only   
        '''
        result = {}
        for line in self.pool.get('account.move.line').browse(cr, uid, ids, context=context):
#            result[line.invoice_id.id] = True        ##Changed by Jabir to fix error when clicking Post button from Customer Payment form. 2010/11/24
            result[line.invoice.id] = True
        return result.keys()

   _columns = {
       'invoice_id': fields.many2one('account.invoice', 'Invoice'),
       'date_due': fields.related('move_line_id','date_maturity', type='date', relation='account.move.line', string='Due Date', readonly=True , store={
                'account.voucher.line': (lambda self, cr, uid, ids, c={}: ids, ['move_line_id'], 20),
                'account.move.line': (_get_due_date, ['date_maturity'], 20),
            }),
       }
account_voucher_line()