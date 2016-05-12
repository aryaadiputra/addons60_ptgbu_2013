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
import netsvc
from osv import fields
from osv import osv
from tools.translate import _
def _combinations(iterable, r):
    '''
    @return: combination generator object

    Example
    combinations(’ABCD’, 2) --> AB AC AD BC BD CD
    combinations(range(4), 3) --> 012 013 023 123
    '''
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = range(r)
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)


class account_move_line(osv.osv):
    '''
        Show unreconciled amount on partial reconciled/none reconciled move line
    '''
    _inherit = 'account.move.line'
    def _unreconciled(self, cr, uid, ids, prop, unknow_none, context):
        '''
        Calculate Amount yet to reconcile
        '''
        res={}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.debit - line.credit
            if line.reconcile_partial_id:
                res[line.id] = 0
                for partial in line.reconcile_partial_id.line_partial_ids:
                    res[line.id] += partial.debit - partial.credit
            res[line.id] = abs(res[line.id])
        return res
    
    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        if type(ids)!=type([]):
            ids = [ids]
        return super(account_move_line, self).write(cr, uid, ids, vals, context=context, check=check, update_check=update_check)

    _columns = {
        'amount_unreconciled': fields.function(_unreconciled, method=True, string='Unreconciled Amount'),
    }
account_move_line()

class account_voucher(osv.osv):


    def default_get(self, cr, user, fields_list, context=None):
        """
        Returns default values for fields
        @param fields_list: list of fields, for which default values are required to be read
        @param context: context arguments, like lang, time zone

        @return: Returns a dict that contains default values for fields
        """
        values = super(account_voucher, self).default_get(cr, user, fields_list, context=context)
        if values.get('type') == 'payment':
            company = self.pool.get('res.users').browse(cr, user, user, context=context).company_id
            if company.def_supp_journal:
                values['journal_id'] = company.def_supp_journal.id
        return values


    def _find_exact_match(self, cr, uid, lines, amount, mark_pay=False, use_discount=False, context=False):
        '''
            Accept voucher lines as list of dict and amount to match
            return : update lines if it found an exact match
        '''
        total_amount = 0.0
        discount_available = {}
        total_discount_available = 0.0
        for line in lines:
            if mark_pay or line.pay == True:
                if use_discount:
                    discount_available[line.id] = 0.0
                    for discount_line in line.available_discounts:
                        discount_available[line.id] += discount_line.proposed_discount
                        total_discount_available += discount_line.proposed_discount
                    total_amount += line.amount_unreconciled - line.credit_used - (line._columns.has_key('writeoff_amount') and line.writeoff_amount)
                else:
                    total_amount += line.amount_unreconciled - line.credit_used - line.discount_used- (line._columns.has_key('writeoff_amount') and line.writeoff_amount)
        if abs(amount - total_amount) < 0.01 :
            '''
                Unchecking all the lines other than matched line
            '''
            line_ids = self.read(cr,uid,lines[0].voucher_id.id,['line_ids'])['line_ids']
            self.pool.get('account.voucher.line').write(cr,uid,line_ids,{'pay':False})
            for line in lines:
                if mark_pay or line.pay == True:
                    line.write({'amount':line.amount_unreconciled - line.credit_used - line.discount_used - (line._columns.has_key('writeoff_amount') and line.writeoff_amount), 'pay':True })
                else:
                    line.write({'amount':0.0, 'pay':False })
            return True
        if use_discount and total_amount>amount and  (total_amount - amount ) <=total_discount_available: #It is possible to match using Discount
            '''
                Unchecking all the lines other than matched line and uncheck all discount lines
            '''
            line_ids = self.read(cr,uid,lines[0].voucher_id.id,['line_ids'])['line_ids']
            self.pool.get('account.voucher.line').write(cr,uid,line_ids,{'pay':False})
            for line_id in line_ids:
                discount_ids = self.pool.get('account.voucher.line').read(cr,uid,line_id,['available_discounts'])['available_discounts']
                self.pool.get("account.voucher.line.discount_to_use").write(cr,uid,discount_ids,{'use_discount':False, 'discount_amount':0.0})
            discount_to_use = total_amount - amount
            for line in lines:
                if discount_to_use > 0.0:
                    for discount_line in line.available_discounts:
                        discount_line.write({'use_discount':True,'discount_amount':min(discount_to_use, discount_line.proposed_discount)})
                        discount_to_use = discount_to_use - min(discount_to_use, discount_line.proposed_discount)
                line = self.pool.get('account.voucher.line').browse(cr, uid, line.id,context=context)
                line.write({'amount':line.amount_unreconciled - line.credit_used - line.discount_used - (line._columns.has_key('writeoff_amount') and line.writeoff_amount), 'pay':True })
            return True
        if len(lines) > 1:
            for combination in _combinations(lines,len(lines)-1 ):
                if self._find_exact_match(cr, uid, combination, amount, mark_pay, context=False):
                    return True
        return False
    
    def calc_diff(self, cr, uid, ids, context={}):
        '''
            Called by calculate/re-calculate action.
            This method will update the credit lines on voucher lines.
            If the field "auto_match" marked, this method will run a matching routine
        '''
        res = {'nodestroy':True}
        amount_cash_discount = 0.0
        amount_interest = 0.0
        for vch in self.browse(cr, uid, ids):
            for line in vch.line_cr_ids:
                '''
                    Update the credit lines and discount lines so that matching routine can use the latest available credits and discounts
                '''
                line._update_credit_lines( context=context)
                line._update_discount_lines(context=context)
                
            if vch.auto_match:
                '''
                    Try the matching routine including the manual selection
                '''
                ret = self._find_exact_match(cr, uid, vch.line_cr_ids, vch.amount, mark_pay=False, use_discount=False, context=False)
                if not ret:
                    '''
                        Try to match considering all voucher lines
                    '''
                    ret = self._find_exact_match(cr, uid, vch.line_cr_ids, vch.amount, mark_pay=True, use_discount=False, context=False)
                if not ret:
                    '''
                        Try to match considering discount
                    '''
                    ret = self._find_exact_match(cr, uid, vch.line_cr_ids, vch.amount, mark_pay=True, use_discount=True, context=False)
        return res

    def onchange_date(self, cr, user, ids, partner_id, journal_id, price, currency_id, ttype, date, context={}):
        """
        @param date: latest value from user input for field date
        @param args: other arguments
        @param context: context arguments, like lang, time zone
        @return: Returns a dict which contains new values, and context
        """
        period_pool = self.pool.get('account.period')
        pids = period_pool.search(cr, user, [('date_start','<=',date), ('date_stop','>=',date)])
        if not pids:
            return {}
        return {
            'value':{
                'period_id':pids[0]
            }
        }

    def _update_discounts(self, lines, vch_date):
        # hook method for account_cash_discount_us module
        return True
        
    _inherit = 'account.voucher'
    _columns = {
        'number': fields.related('move_id', 'name', type="char", readonly=True, string='Number'),
        'auto_match':fields.boolean('Use Automatic Matching')
    }

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context={}):
        """price
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        '''
            function ported from account_voucher_jds module
            This function is redefined and do not use functionality provided by account_voucher module
            Possible issue is that the latest function from updated account_voucher module will have no effect if this module is installed
        '''
        if context is None:
            context = {}
        currency_pool = self.pool.get('res.currency')
        move_pool = self.pool.get('account.move')
        line_pool = self.pool.get('account.voucher.line')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        default = {
            'value':{'line_ids':[], 'line_dr_ids':[], 'line_cr_ids':[], 'pre_line': False, 'currency_id':currency_id, 'journal_id': False},
        }
        if partner_id and not journal_id:
            partner = partner_pool.browse(cr, uid, partner_id, context)
            if partner._columns.has_key('payment_meth_id') and partner.payment_meth_id:
                payment_mode_pool = self.pool.get('payment.mode')
                payment_meth = payment_mode_pool.browse(cr, uid, partner.payment_meth_id.id, context)
                if payment_meth:
                    default['value']['journal_id'] = payment_meth.journal.id
                    journal_id = payment_meth.journal.id
        if not journal_id:
            return {}
        context_multi_currency = context.copy()
        if date:
            context_multi_currency.update({'date': date})

        vals = self.onchange_journal(cr, uid, ids, journal_id, [], False, partner_id, context)
        vals = vals.get('value')
        currency_id = vals.get('currency_id', currency_id)

        if not partner_id:
            return default

        if not partner_id and ids:
            line_ids = line_pool.search(cr, uid, [('voucher_id','=',ids[0])])
            if line_ids:
                line_pool.unlink(cr, uid, line_ids)
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        account_id = False
        if journal.type in ('sale','sale_refund'):
            account_id = partner.property_account_receivable.id
        elif journal.type in ('purchase', 'purchase_refund','expense'):
            account_id = partner.property_account_payable.id
        elif journal.type in ('cash', 'bank'):
            account_id = journal.default_debit_account_id.id
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id

        if journal and not default['value']['currency_id']:
            default['value']['currency_id'] = journal.company_id.currency_id.id
        default['value']['account_id'] = account_id
        if journal.type not in ('cash', 'bank'):
            return default

        total_credit = 0.0
        total_debit = 0.0
        account_type = 'receivable'
        if ttype == 'payment':
            account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            account_type = 'receivable'

        if partner._columns.has_key('nat_acc_parent') and partner.nat_acc_parent:
            partner_ids = partner_pool.search(cr,uid,[('parent_id','child_of',[partner_id])])
        else:
            partner_ids = [partner_id]
        ids = move_line_pool.search(cr, uid, [('account_id.type','=', account_type), ('reconcile_id','=', False), ('partner_id','in',partner_ids)], context=context)
        ids.reverse()
        moves = move_line_pool.browse(cr, uid, ids)

        company_currency = journal.company_id.currency_id.id
        if company_currency != currency_id and ttype == 'payment':
            total_debit = currency_pool.compute(cr, uid, currency_id, company_currency, total_debit, context=context_multi_currency)
        elif company_currency != currency_id and ttype == 'receipt':
            total_credit = currency_pool.compute(cr, uid, currency_id, company_currency, total_credit, context=context_multi_currency)

        for line in moves:
            if line.credit and line.reconcile_partial_id and ttype == 'receipt':
                continue
            if line.debit and line.reconcile_partial_id and ttype == 'payment':
                continue
            total_credit += line.credit or 0.0
            total_debit += line.debit or 0.0

        for line in moves:
            if line.credit and line.reconcile_partial_id and ttype == 'receipt':
                continue
            if line.debit and line.reconcile_partial_id and ttype == 'payment':
                continue

            original_amount = line.credit or line.debit or 0.0
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original':currency_pool.compute(cr, uid, company_currency, currency_id, original_amount, context=context_multi_currency),
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled':currency_pool.compute(cr, uid, company_currency, currency_id, line.amount_unreconciled, context=context_multi_currency)
            }

            def calc_amount(line, total):
                return min(line.amount_unreconciled, total)

            if line.credit:
                amount = calc_amount(line, total_debit)
                rs['amount'] = currency_pool.compute(cr, uid, company_currency, currency_id, amount, context=context_multi_currency)
                total_debit -= amount
            else:
                amount = calc_amount(line, total_credit)
                rs['amount'] = currency_pool.compute(cr, uid, company_currency, currency_id, amount, context=context_multi_currency)
                total_credit -= amount

            default['value']['line_ids'].append(rs)
            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if ttype == 'payment' and len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif ttype == 'receipt' and len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
        for credit_line in default['value']['line_dr_ids']:
            credit_line['amount'] = 0.0
        for invoice_line in default['value']['line_cr_ids']:
            invoice_line['amount'] = 0.0
            invoice_line['amount_difference'] = invoice_line['amount_unreconciled']

        return default

    def calc_cash_discount(self, vch, line, amount=0):
        # hook method for cash discount
        return 0.0

    def calc_interest(self, vch, line, amount=0):
        # hook method for interest posting
        return 0.0

    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
            Function overridden from account voucher module
            account posting include amount after currency conversion 
            TODO :  Function need more analysis and testing
        '''

        def _get_payment_term_lines(term_id, amount):
            term_pool = self.pool.get('account.payment.term')
            if term_id and amount:
                terms = term_pool.compute(cr, uid, term_id, amount)
                return terms
            return False
        if not context:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        analytic_pool = self.pool.get('account.analytic.line')
        currency_pool = self.pool.get('res.currency')
        invoice_pool = self.pool.get('account.invoice')
        company_pool = self.pool.get('res.company')
        for vch in self.browse(cr, uid, ids):
            if vch.move_id:
                continue

            if 'force_name' in context and context['force_name']:
                name = context['force_name']
            elif vch.journal_id.sequence_id:
                name = self.pool.get('ir.sequence').get_id(cr, uid, vch.journal_id.sequence_id.id)
            else:
                raise osv.except_osv(_('Error !'), _('Please define a sequence on the journal !'))

            move = {
                'name' : name,
                'journal_id': vch.journal_id.id,
                'narration' : vch.narration,
                'date':vch.date,
                'ref':vch.reference,
                'period_id': vch.period_id and vch.period_id.id or False
            }
            move_id = move_pool.create(cr, uid, move)

            #create the first line manually
            company_currency = vch.journal_id.company_id.currency_id.id
            debit = 0.0
            credit = 0.0
            # TODO: is there any other alternative then the voucher type ??
            # -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt
            if vch.type in ('purchase', 'payment'):
                credit = currency_pool.compute(cr, uid, vch.currency_id.id, company_currency, vch.amount)
            elif vch.type in ('sale', 'receipt'):
                debit = currency_pool.compute(cr, uid, vch.currency_id.id, company_currency, vch.amount)
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            move_line = {
                'name':vch.name or '/',
                'debit':debit,
                'credit':credit,
                'account_id':vch.account_id.id,
                'move_id':move_id ,
                'journal_id':vch.journal_id.id,
                'period_id':vch.period_id.id,
                'partner_id':vch.partner_id.id,
                'currency_id':vch.currency_id.id,
                'amount_currency':vch.amount,
                'date':vch.date,
                'date_maturity':vch.date_due
            }

            if (debit == 0.0 or credit == 0.0 or debit+credit > 0) and (debit > 0.0 or credit > 0.0):
                master_line = move_line_pool.create(cr, uid, move_line)
            company = company_pool.browse(cr, uid, vch.company_id.id, context)
            rec_list_ids = []
            line_total = debit - credit
            if vch.type == 'sale':
                line_total = line_total - currency_pool.compute(cr, uid, vch.currency_id.id, company_currency, vch.tax_amount)
            elif vch.type == 'purchase':
                line_total = line_total + currency_pool.compute(cr, uid, vch.currency_id.id, company_currency, vch.tax_amount)

            writeoff_ids = []
            for line in vch.line_ids:
                if not line.amount:
                    skip_flag = True
                    if line.available_credits:
                        for av_credits in  line.available_credits:
                            if av_credits.use_credit and av_credits.discount_amount:
                                skip_flag=False
                    if skip_flag:
                        continue
                amount_cash_discount = 0.0#self.calc_cash_discount(line, line.amount)
                amount_writeoff = 0.0#calc_writeoff(line, amount_cash_discount)
                amount_interest = 0.0#calc_interest(line, amount_cash_discount + amount_writeoff)
                amount_currency = currency_pool.compute(cr, uid, vch.currency_id.id, company_currency, line.amount)
                amount = amount_currency
                move_line = {
                    'journal_id':vch.journal_id.id,
                    'period_id':vch.period_id.id,
                    'name':line.name and line.name or '/',
                    'account_id':line.account_id.id,
                    'move_id':move_id,
                    'partner_id':vch.partner_id.id,
                    'currency_id':vch.currency_id.id,
                    #Posting amount after currency conversion
                    'amount_currency':amount,
                    'analytic_account_id':line.account_analytic_id and line.account_analytic_id.id or False,
                    'quantity':1,
                    'credit':0.0,
                    'debit':0.0,
                    'date':vch.date
                }
                if line.invoice_id:
                    move_line['partner_id'] = line.invoice_id.partner_id.id
                if amount < 0:
                    amount = -amount
                    if line.type == 'dr':
                        line.type = 'cr'
                    else:
                        line.type = 'dr'

                if (line.type=='dr'):
                    line_total += amount
                    move_line['debit'] = amount
                else:
                    line_total -= (amount+line.credit_used)
                    move_line['credit'] = (amount+line.credit_used)

                if vch.tax_id and vch.type in ('sale', 'purchase'):
                    move_line.update({
                        'account_tax_id':vch.tax_id.id,
                    })
                
                if line_total < 0.01 and line_total > -0.01:
                    line_total = 0.0
                    
                master_line = move_line_pool.create(cr, uid, move_line)
                if line.move_line_id.id:
                    rec_ids = [master_line, line.move_line_id.id]
                    rec_list_ids.append(rec_ids)

                if line.invoice_id.id:
                    invoice = self.pool.get('account.invoice').browse(cr, uid, line.invoice_id.id)
                    types = {'out_invoice': -1, 'in_invoice': 1, 'out_refund': 1, 'in_refund': -1}
                    direction = types[invoice.type]

                '''
                    Post Discount Lines for supplier
                '''
                
                if line.type == 'dr' and line._columns.has_key('available_discounts') and line.available_discounts: # and line.cash_discount > 0.0:
                    for available_discounts in line.available_discounts:
                        if available_discounts.use_discount:
                            l1 = {
                                'journal_id':vch.journal_id.id,
                                'period_id':vch.period_id.id,
                                'debit': direction * available_discounts.discount_amount>0 and direction * available_discounts.discount_amount,
                                'credit': direction * available_discounts.discount_amount<0 and - direction * available_discounts.discount_amount,
                                'account_id': line.account_id.id,
                                'partner_id': line.move_line_id.partner_id.id, #line.partner_id.id,
                                'move_id':move_id,
                                'ref':'Cash Discount',
                                'name':line.name and line.name or '/',
                                'date': vch.date,
                                'currency_id':vch.currency_id.id,
                                'amount_currency':available_discounts.discount_amount and - direction * available_discounts.discount_amount or 0.0,
                                'company_id': line.company_id.id,
                            }
                            l2 = {
                                'journal_id':vch.journal_id.id,
                                'period_id':vch.period_id.id,
                                'debit': direction * available_discounts.discount_amount<0 and - direction * available_discounts.discount_amount,
                                'credit': direction * available_discounts.discount_amount>0 and direction * available_discounts.discount_amount,
                                'account_id': available_discounts.gl_account.id,
                                'partner_id': line.move_line_id.partner_id.id,
                                'move_id':move_id,
                                'ref':'Cash Discount',
                                'name':line.name and line.name or '/',
                                'date': vch.date,
                                'currency_id':vch.currency_id.id,
                                'amount_currency':available_discounts.discount_amount and - direction * available_discounts.discount_amount or 0.0,
                                'company_id': line.company_id.id,
                            }
                            name = invoice.number
                            l1['name'] = name
                            l2['name'] = name
                            move_lines = [l1,l2]
                            for move_line in move_lines:
                                master_line = move_line_pool.create(cr, uid, move_line)
                                if line.move_line_id.id and move_line['account_id'] == line.move_line_id.account_id.id:
                                    rec_ids = [master_line, line.move_line_id.id]
                                    rec_list_ids.append(rec_ids)

                
                
                '''
                    Post Discount Lines for customer
                '''
                
                
                if line.type == 'cr' and line._columns.has_key('available_discounts') and line.available_discounts: # and line.cash_discount > 0.0:
                    for available_discounts in line.available_discounts:
                        if available_discounts.use_discount:
                            l1 = {
                                'journal_id':vch.journal_id.id,
                                'period_id':vch.period_id.id,
                                'debit': direction * available_discounts.discount_amount>0 and direction * available_discounts.discount_amount,
                                'credit': direction * available_discounts.discount_amount<0 and - direction * available_discounts.discount_amount,
                                'account_id': line.account_id.id,
                                'partner_id': line.move_line_id.partner_id.id, #line.partner_id.id,
                                'move_id':move_id,
                                'ref':'Cash Discount',
                                'name':line.name and line.name or '/',
                                'date': vch.date,
                                'currency_id':vch.currency_id.id,
                                'amount_currency':available_discounts.discount_amount and - direction * available_discounts.discount_amount or 0.0,
                                'company_id': line.company_id.id,
                            }
                            l2 = {
                                'journal_id':vch.journal_id.id,
                                'period_id':vch.period_id.id,
                                'debit': direction * available_discounts.discount_amount<0 and - direction * available_discounts.discount_amount,
                                'credit': direction * available_discounts.discount_amount>0 and direction * available_discounts.discount_amount,
                                'account_id': available_discounts.gl_account.id,
                                'partner_id': line.move_line_id.partner_id.id,
                                'move_id':move_id,
                                'ref':'Cash Discount',
                                'name':line.name and line.name or '/',
                                'date': vch.date,
                                'currency_id':vch.currency_id.id,
                                'amount_currency':available_discounts.discount_amount and - direction * available_discounts.discount_amount or 0.0,
                                'company_id': line.company_id.id,
                            }
                            name = invoice.number
                            l1['name'] = name
                            l2['name'] = name
                            move_lines = [l1,l2]
                            for move_line in move_lines:
                                master_line = move_line_pool.create(cr, uid, move_line)
                                if line.move_line_id.id and move_line['account_id'] == line.move_line_id.account_id.id:
                                    rec_ids = [master_line, line.move_line_id.id]
                                    rec_list_ids.append(rec_ids)
                '''
                    Post Writeoff
                '''
                if line.type == 'cr' and line._columns.has_key('writeoff_ids') and line.writeoff_ids:
                    for writeoff in line.writeoff_ids:
                        l1 = {
                            'journal_id':vch.journal_id.id,
                            'period_id':vch.period_id.id,
                            'debit': direction * writeoff.writeoff_amount>0 and direction * writeoff.writeoff_amount,
                            'credit': direction * writeoff.writeoff_amount<0 and - direction * writeoff.writeoff_amount,
                            'account_id': line.account_id.id,
                            'partner_id': line.move_line_id.partner_id.id, #,
                            'move_id':move_id,
                            'ref':'Writeoff',
                            'name':line.name and line.name or '/',
                            'date': vch.date,
                            'currency_id':vch.currency_id.id,
                            'amount_currency':writeoff.writeoff_amount and - direction * writeoff.writeoff_amount or 0.0,
                            'company_id': line.company_id.id,
                        }
                        l2 = {
                            'journal_id':vch.journal_id.id,
                            'period_id':vch.period_id.id,
                            'debit': direction * writeoff.writeoff_amount<0 and - direction * writeoff.writeoff_amount,
                            'credit': direction * writeoff.writeoff_amount>0 and direction * writeoff.writeoff_amount,
                            'account_id': writeoff.gl_account.id,
                            'partner_id': line.partner_id.id,
                            'move_id':move_id,
                            'ref':'Writeoff',
                            'name':line.name and line.name or '/',
                            'date': vch.date,
                            'currency_id':vch.currency_id.id,
                            'amount_currency':writeoff.writeoff_amount and - direction * writeoff.writeoff_amount or 0.0,
                            'company_id': line.company_id.id,
                        }
                        name = invoice.number
                        l1['name'] = name
                        l2['name'] = name
                        move_lines = [l1,l2]
                        for move_line in move_lines:
                            master_line = move_line_pool.create(cr, uid, move_line)
                            if line.move_line_id.id and move_line['account_id'] == line.move_line_id.account_id.id:
                                rec_ids = [master_line, line.move_line_id.id]
                                rec_list_ids.append(rec_ids)

                if line.type == 'dr':
                    line.write({ 'pending_credits':0})

            diff = line_total
            if not self.pool.get('res.currency').is_zero(cr, uid, vch.currency_id, line_total):
                move_line = {
                    'name':name,
                    'account_id':False,
                    'move_id':move_id ,
                    'partner_id':vch.partner_id.id,
                    'date':vch.date,
                    'credit':diff>0 and diff or 0.0,
                    'debit':diff<0 and -diff or 0.0,
                }
                account_id = False
                if vch.type in ('sale', 'receipt'):
                    account_id = vch.partner_id.property_account_receivable.id
                else:
                    account_id = vch.partner_id.property_account_payable.id
                move_line['account_id'] = account_id
                move_line_id = move_line_pool.create(cr, uid, move_line)
#                if line.move_line_id.id:
#                    rec_ids = [move_line, line.move_line_id.id]
#                    rec_list_ids.append(rec_ids)

            self.write(cr, uid, [vch.id], {
                'move_id': move_id,
                'state':'posted'
            })
            move_pool.post(cr, uid, [move_id], context={})
            
            # let's see if we can incorporate this in the reconciliation
            #diff = 0
            if diff > 0.0:
                diff = line_total
                rec_ids = []
                debit_ids = []
                applied_amount = 0.0
                move = move_pool.browse(cr, uid, move_id, context={})
                for line in move.line_id:
                    if line.account_id.id == vch.journal_id.default_credit_account_id.id:
                        applied_amount += line.debit
                        if line.id and line.credit > 0.0:
                            if line.id not in rec_ids:
                                rec_ids.append(line.id)
                        if line.id and line.debit > 0.0:
                            if line.id not in debit_ids:
                                debit_ids.append(line.id)
                    if applied_amount == diff:
                        for vchcr in vch.line_cr_ids:
                            if vchcr.amount and vchcr.move_line_id.id not in rec_ids:
                                rec_ids.append(vchcr.move_line_id.id)
                        for vchdr in vch.line_dr_ids:
                            if vchdr.amount and vchdr.move_line_id.id not in debit_ids:
                                debit_ids.append(vchdr.move_line_id.id)
                        rec_list_ids = [rec_ids, debit_ids]
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    move_line_pool.reconcile_partial(cr, uid, rec_ids)
        return True

account_voucher()

class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'
    _order = "date_due"


    def _update_credit_lines(self,cr, uid, ids, context):
        '''
            Create or update the list of credit that can be used under each voucher line.
            To be called from the calculate/re-calculate action
        '''
        credits_used_pool = self.pool.get('account.voucher.line.credits_to_use')
        for line in self.browse(cr , uid, ids, context):
            credits_lines_used = [x.orginal_credit_line_id.id for x in line.available_credits]
            for credit_line in line.voucher_id.line_dr_ids :
                if credit_line.id not in credits_lines_used and line.invoice_id and line.invoice_id.payment_term:
                    # 
                    credits_used_pool.create(cr, uid, {
                                'voucher_line_id': line.id,
                                'orginal_credit_line_id':credit_line.id,
                                'use_credit': False,
                                'inv_credit': credit_line.move_line_id.id,
                                'discount_window_date': credit_line.date_original,
                                'orginal_amount': credit_line.amount_original,
                                'available_amount': credit_line.amount_unreconciled - credit_line.pending_credits,
                                'discount_amount': 0.0,
                                'gl_account' : credit_line.account_id.id,})
                else :
                    to_update_credit_line_ids = credits_used_pool.search(cr,uid,[('voucher_line_id','=',line.id),( 'orginal_credit_line_id','=',credit_line.id)], context=context)                    
                    if to_update_credit_line_ids:
                        credits_used_pool.write(cr, uid,to_update_credit_line_ids,{'available_amount': credit_line.amount_unreconciled-credit_line.pending_credits}, context=context)


    def write(self, cr, user, ids, vals, context=None):
        '''
            Add invoice and description in payment modification line
        '''
        if type(ids) == type([]):
            move = self.browse(cr, user,ids[0]).move_line_id
        else:
            move = self.browse(cr, user,ids).move_line_id
        if move:
            vals['invoice_id'] = move.invoice and move.invoice.id
            vals['name'] = move.invoice and move.invoice.number

        return super(account_voucher_line, self).write(cr, user, ids, vals, context)

    def create(self, cr, user, vals, context=None):
        '''
            Add invoice and description in payment modification line
        '''
        if vals.has_key('move_line_id') and vals['move_line_id']:
            move = self.pool.get('account.move.line').browse(cr, user,vals['move_line_id'])
            vals['invoice_id'] = move.invoice and move.invoice.id
            vals['name'] = move.invoice and move.invoice.number
        return super(account_voucher_line, self).create(cr, user, vals, context)

    def calc_amt(self, cr, uid, ids, context={}):
        '''
            Function to calculate Pending Credits Used
            can be removed : Not used anymore : verify first
        '''
        res = {}
        result = 0.0

        for id in ids:
            res[id] = result
        return res

    def _credits_calc(self, cr, uid, ids, name, args, context):
        '''
            Function to calculate Pending Credits Used
        '''
        credits_used_pool = self.pool.get('account.voucher.line.credits_to_use')
        res={}
        for line in self.browse(cr, uid, ids):
            credits_used_ids = credits_used_pool.search(cr, uid, [('orginal_credit_line_id','=',line.id)])
            res[line.id] = 0.0
            if line.voucher_id.state != 'draft':
                continue
            for credit_used in credits_used_pool.browse(cr, uid, credits_used_ids, context=context):
                if credit_used.use_credit:
                    res[line.id] += credit_used.discount_amount
        return res
    def _compute_credit_used(self, cr, uid, ids, name, args, context=None):
        '''
            Field function for credit_used
        '''
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = 0.0
            for credit_line in line.available_credits:
                if credit_line.use_credit :
                    res[line.id] +=  credit_line.discount_amount
        return res

    def _compute_balance(self, cr, uid, ids, name, args, context=None):
        '''
            Field function [multi] to calculate amount_original, amount_unreconciled and amount_difference
        '''
        currency_pool = self.pool.get('res.currency')
        rs_data = {}
        for line in self.browse(cr, uid, ids):
            ctx = context.copy()
            ctx.update({'date': line.voucher_id.date})
            res = {}
            company_currency = line.voucher_id.journal_id.company_id.currency_id.id
            voucher_currency = line.voucher_id.currency_id.id
            move_line = line.move_line_id or False
            if not move_line:
                res['amount_original'] = 0.0
                res['amount_unreconciled'] = 0.0

            elif move_line and move_line.credit > 0:
                res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.credit, context=ctx)
            else:
                res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.debit, context=ctx)

            if move_line:
                res['amount_unreconciled'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.amount_unreconciled - line.pending_credits , context=ctx)
                if line.amount > 0.0:
                    res['amount_difference'] = res['amount_unreconciled'] - line.amount - line.credit_used
                else:
                    res['amount_difference'] = 0.0
            rs_data[line.id] = res
        return rs_data

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
    
    def _compute_discount_used(self, cr, uid, ids, name, args, context=None):
        '''
            Field function to calculate discount_used
            Hook function : to be redefined on account_cash_discount_us 
        '''
        res = {}
        for id in ids:
            res[id] = 0.0
        return res
    def _calc_writeoff(self, cr, uid, ids, name, args, context):
        '''
            Field function to calculate writeoff_amount
            Hook function : to be redefined on account_voucher_writeoff_us 
        '''
        res={}
        for id in ids:
            res[id] = 0.0
        return res


    def _order_compute_credit_used(self, cr, uid, ids, context=None):
        """ 
            Store function - Field : credit_used, model : account.voucher.line.credits_to_use
        """
        operation_ids = []
        for credits_to_use in self.pool.get('account.voucher.line.credits_to_use').browse(cr,uid,ids,context=context):
            operation_ids.append(credits_to_use.voucher_line_id and credits_to_use.voucher_line_id.id)
        return operation_ids

    def _get_voucher_line_ids(self, cr, uid, ids, context=None):
        '''
            Store function - field : company_id, model :account.voucher
        '''
        result = []
        for vch_lines in self.pool.get('account.voucher').read(cr, uid, ids, ['line_ids'], context=context):
            result +=vch_lines['line_ids']
        return result
    
    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'account_id':fields.many2one('account.account','G/L Account', required=True),
        'amount':fields.float('Payment Amt', digits=(14,2), required=True),
        'date_due': fields.related('move_line_id','date_maturity', type='date', relation='account.move.line', string='Due Date', readonly=True , store={
                'account.voucher.line': (lambda self, cr, uid, ids, c={}: ids, ['move_line_id'], 20),
                'account.move.line': (_get_due_date, ['date_maturity'], 20),
            }),
        'amount_original': fields.function(_compute_balance, method=True, multi='dc', type='float', string='Original Amt', store=True, readonly=True),
        'amount_unreconciled': fields.function(_compute_balance, method=True, multi='dc', type='float', string='Amt Due', store=True, readonly=True),
        'company_id': fields.related('voucher_id','company_id',type='many2one', relation='res.company', string='Company', store={
                'account.voucher': (_get_voucher_line_ids, ['company_id'], 20),
            }),
        'credit_used': fields.function(_compute_credit_used, method=True, type='float', string='Credit Used',
                                       store={'account.voucher.line.credits_to_use':(_order_compute_credit_used,['use_credit','discount_amount'], 10)}, readonly=True),
        'amount_difference': fields.function(_compute_balance, method=True, multi='dc', type='float', string='Unpaid Amt', digits=(16, 2) ),
        'writeoff': fields.boolean("Writeoff"),
        'pay': fields.boolean("Pay", required=True),
        'pending_credits':fields.function(_credits_calc, method=True, string='Pending Credits Used', type='float'),
        'available_credits':fields.one2many('account.voucher.line.credits_to_use', 'voucher_line_id', 'Available credits'  ),
        'discount_used': fields.function(_compute_discount_used, method=True, type='float', string='Discount Used', store=False, readonly=True),
        'writeoff_amount':fields.function(_calc_writeoff, method=True, string='Write-off Amt', type='float', store=False,),
    }

    def recalculate_values(self, cr, uid, ids, context={}):
        '''
            Re-calculate button action
        '''
        if type(ids) == type([]):
            voucher_line = self.browse(cr,uid,ids[0])
        else:
            voucher_line = self.browse(cr,uid,ids)
        self.pool.get('account.voucher').calc_diff(cr, uid, [voucher_line.voucher_id.id])
        return True
    def clear_values(self, cr, uid, ids, context={}):
        '''
        Clear all selected discounts, credits and writeoffs and manually entered values
        '''
        voucher_line = self.browse(cr,uid,ids[0])
        if voucher_line._columns.has_key('writeoff_ids'):
            if voucher_line._columns.has_key('available_discounts'):
                for lines in self.read(cr,uid,ids,['available_credits','writeoff_ids','available_discounts']):
                    lines['writeoff_ids'] and self.pool.get('account.voucher.line.writeoff').unlink(cr,uid,lines['writeoff_ids'])
                    lines['available_credits'] and self.pool.get('account.voucher.line.credits_to_use').write(cr,uid,lines['available_credits'],
                                                                                                        {'use_credit':False, 'discount_amount':0.0})
                    lines['available_discounts'] and self.pool.get('account.voucher.line.discount_to_use').write(cr,uid,lines['available_discounts'],
                                                                                                        {'use_discount':False, 'discount_amount':0.0})
            else:
                for lines in self.read(cr,uid,ids,['available_credits','writeoff_ids']):
                    lines['writeoff_ids'] and self.pool.get('account.voucher.line.writeoff').unlink(cr,uid,lines['writeoff_ids'])
                    lines['available_credits'] and self.pool.get('account.voucher.line.credits_to_use').write(cr,uid,lines['available_credits'],
                                                                                                        {'use_credit':False, 'discount_amount':0.0})
        elif voucher_line._columns.has_key('available_discounts'):
            for lines in self.read(cr,uid,ids,['available_credits','available_discounts']):
                    lines['available_credits'] and self.pool.get('account.voucher.line.credits_to_use').write(cr,uid,lines['available_credits'],
                                                                                                            {'use_credit':False, 'discount_amount':0.0})
                    lines['available_discounts'] and self.pool.get('account.voucher.line.discount_to_use').write(cr,uid,lines['available_discounts'],
                                                                                                                 {'use_discount':False, 'discount_amount':0.0})
        else:
            for lines in self.read(cr,uid,ids,['available_credits']):
                lines['available_credits'] and self.pool.get('account.voucher.line.credits_to_use').write(cr,uid,lines['available_credits'],
                                                                                                    {'use_credit':False, 'discount_amount':0.0})
        return True

    def onchange_pay(self, cr, uid, ids, line_amount, pay, amount_unreconciled,par_cr_ids, par_amount, credit_used, discount_used=0, writeoff_amount=0, context={}):
        '''
        Function to automatically fill the values when the pay checkbox is selected
        '''
        ret = {}
        writeoff_amount = (not writeoff_amount and [0] or [writeoff_amount])[0]
        discount_used = (not discount_used and [0] or [discount_used])[0]
        credit_used = (not credit_used and [0] or [credit_used])[0]
        if pay:
            tot_amt = par_amount + line_amount
            for credit in par_cr_ids:
                if credit[2]['pay']:
                    tot_amt -= (credit[2]['amount'])
            if tot_amt < 0:
                ret['amount'] = 0.0
            else:
                amount_unreconciled -= (discount_used+writeoff_amount+credit_used)
                ret['amount'] = min(tot_amt,(amount_unreconciled<0) and 0 or amount_unreconciled)
        else:
            ret['amount'] = 0.0
        return {'value':ret}



account_voucher_line()

class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'

    def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id, next_number, context=None):
        '''
            TODO : Need careful testing of this function.
        '''
#        st_line = self.pool.get('account.bank.statement.line').browse(cr, uid, st_line_id, context=context)
#        if st_line.voucher_id:
#            res = self.pool.get('account.voucher').proforma_voucher(cr, uid, [st_line.voucher_id.id], context={'force_name': next_number})
#            return self.pool.get('account.move.line').write(cr, uid, [x.id for x in st_line.voucher_id.move_ids], {'statement_id': st_line.statement_id.id}, context=context)
#        return super(account_bank_statement, self).create_move_from_st_line(cr, uid, st_line, company_currency_id, next_number, context=context)
    
        voucher_obj = self.pool.get('account.voucher')
        wf_service = netsvc.LocalService("workflow")
        move_line_obj = self.pool.get('account.move.line')
        bank_st_line_obj = self.pool.get('account.bank.statement.line')
        st_line = bank_st_line_obj.browse(cr, uid, st_line_id, context=context)
        if st_line.voucher_id:
            voucher_obj.write(cr, uid, [st_line.voucher_id.id], {'number': next_number}, context=context)
            if st_line.voucher_id.state == 'cancel':
                voucher_obj.action_cancel_draft(cr, uid, [st_line.voucher_id.id], context=context)
            wf_service.trg_validate(uid, 'account.voucher', st_line.voucher_id.id, 'proforma_voucher', cr)

            v = voucher_obj.browse(cr, uid, st_line.voucher_id.id, context=context)
            bank_st_line_obj.write(cr, uid, [st_line_id], {
                'move_ids': [(4, v.move_id.id, False)]
            })

            return move_line_obj.write(cr, uid, [x.id for x in v.move_ids], {'statement_id': st_line.statement_id.id}, context=context)
        return super(account_bank_statement, self).create_move_from_st_line(cr, uid, st_line.id, company_currency_id, next_number, context=context)

account_bank_statement()

class account_voucher_line_credits_to_use(osv.osv):
    _name = "account.voucher.line.credits_to_use"
    _rec_name = 'inv_credit'

    def _credit_balance(self, cr, uid, ids, name, args, context=None):
        '''
        Function to calculate the value of variable Credit Balance
        '''
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.use_credit:
                res[line.id] = line.available_amount - line.discount_amount
            else:
                res[line.id] = line.available_amount
        return res

    _columns = {
        'voucher_line_id': fields.many2one('account.voucher.line', 'Account Voucher line', ondelete='cascade', readonly=True),
        'orginal_credit_line_id': fields.many2one('account.voucher.line', 'Account Voucher Credit Line', ondelete='cascade', readonly=True),
        'use_credit': fields.boolean('Use Credit',help='Used to indicate if credit should used against the invoice.', required=True),
        'inv_credit': fields.many2one('account.move.line', 'Invoice', help='Invoice of the credit', readonly=True),
        'discount_window_date': fields.date('Date',help='Date of the original credit', readonly=True),
        'orginal_amount': fields.float('Original Credit Amt', readonly=True),
        'available_amount': fields.float('Credit Amt Available', readonly=True),
        'discount_amount': fields.float('Amt to Use',help='Enter the amount of discount to be given.', required=True),
        'gl_account' : fields.many2one('account.account', 'G/L Account',help='Enter the General Ledger account number to record taking the cash discount.', required=True,readonly=True),
        'credit_bal': fields.function(_credit_balance, string='Credit Balance', method=True, type='float', store=False),
    }
    def onchage_use_credit(self, cr, uid, ids, use_credit, available_amount, amount_difference, context=None):
        '''
        Function to automatically fill or remove the discount amount when use credit checkbox checked or unchecked
        '''
        res = {}
        if use_credit:
            res['value'] = {'discount_amount': min(available_amount, amount_difference)}
        else:
            res['value'] = {'discount_amount': 0}
        return res
    def onchage_discount_amount(self, cr, uid, ids, available_amount, discount_amount, context=None):
        '''
        Function to validate the discount amount
        '''
        res = {}
        if discount_amount < 0:
            res['value'] = {'discount_amount': 0, 'use_credit':False }
            res['warning'] = {'title': 'Credit not in the limit', 'message': 'Credit should not be a negative value.'}
            return res
        if discount_amount > available_amount:
            res['value'] = {'discount_amount': available_amount, 'use_credit':True }
            res['warning'] = {'title': 'Credit not in the limit', 'message': 'Please adjust the Credit Amt value to be less than or equal the Credit Available.'}
            return res
        if discount_amount == 0.0:
            res['value'] = { 'use_credit':False }
        else:
            res['value'] = { 'use_credit':True }
        return res
account_voucher_line_credits_to_use()

'''
    Hook for account_voucher_writeoff_us
'''
class res_company(osv.osv):
    '''
        New field to keep the write-off account configuration on company
        This Write-off account will be used on Account voucher.
    '''
    _name = 'res.company'
    _inherit = 'res.company'
    _columns = {
        'def_supp_journal': fields.many2one('account.journal','Default Supplier Payment Method',readonly=False),
        'writeoff_account': fields.many2one('account.account', 'Writeoff Account', domain=[('type','!=','view'),('type','!=','consolidation')],
                                            help="This is the designated write-off gl account that will be used when writing off remaining amounts in customer payment."),
    }
res_company()
