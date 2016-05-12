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

from collections import defaultdict
from mx.DateTime import RelativeDateTime
from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import mx.DateTime
from amount_to_words import amount_to_words
from tools.amount_to_text_en import amount_to_text

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


class account_payment_term(osv.osv):
    _name = "account.payment.term"
    _inherit = "account.payment.term"
    _columns = {
        'cash_discount_ids': fields.one2many('account.cash.discount', 'payment_id', 'Cash Discounts'),
    }
    def get_discounts(self, cr, uid, id, base_date, context={}):
        """
        return the list of (date,percentage) ordered by date for the
        payment term with the corresponding id. return [] if no cash
        discount are defined. base_date is the date from where the
        discounts are computed.
        """
        res=[]
        for pt in self.browse(cr, uid, id, context):
        
            if not pt.cash_discount_ids:
                continue
    
            for d in pt.cash_discount_ids:
                res.append(
                    ((mx.DateTime.strptime(base_date,'%Y-%m-%d') +\
                      RelativeDateTime(days=d.delay)).strftime("%Y-%m-%d"),
                     d.discount)
                    )

        res.sort(cmp=lambda x,y: cmp(x[0],y[0]))
        return res
account_payment_term()

class account_invoice(osv.osv):
    '''
        Add discount calculation to invoice
    '''
    _inherit = 'account.invoice'

    def _get_discount(self, cr, uid,  ids, field_name, args, context={}):
        '''
        Calculate the value of variable date_discount (Discount Date) and amount_discounted (Discounted Total)
        '''

        if context is None:
            context = {}
        for invoice in self.browse(cr, uid, ids, context):
            res = defaultdict(list)
            res[invoice.id] = {
                'date_discount': invoice.date_due,
                'amount_discounted': invoice.amount_total
            }
            if not invoice.date_invoice:
                invoice_date = mx.DateTime.today().strftime("%Y-%m-%d")
                self.write(cr, uid, [invoice.id], {'date_invoice': invoice_date}, context)
            else:
                invoice_date = invoice.date_invoice
            discounts = invoice.payment_term and invoice.payment_term.get_discounts(invoice_date, context=context)
            if discounts:
                line_obj = self.pool.get('account.invoice.line')
                discount_total = 0.0
                non_discount_total = 0.0
                for line in invoice.invoice_line:
                    if line.cash_discount:
                        discount_total += line.price_subtotal
                        line_cash_discount =  round((1.0 - discounts[0][1]) * line.price_subtotal)
                        line_obj.write(cr, uid, line.id, {'cash_discount': line_cash_discount}, context)
                    else:
                        non_discount_total += line.price_subtotal
                        line_obj.write(cr, uid, line.id, {'cash_discount': 0.0}, context)
                # assume taxes are never discountable
                non_discount_total += invoice.amount_tax
                # There may be more than one - return the earliest
                res[invoice.id] = {
                    'date_discount': discounts[0][0],
                    'amount_discounted': round(((1.0 - discounts[0][1]) * discount_total) + non_discount_total,2)
                }
            return defaultdict(type([]),res)

    _columns = {
        'date_discount': fields.function(_get_discount, method=True, type='date', string='Discount Date', multi='all'),
        'amount_discounted': fields.function(_get_discount, method=True, type='float', digits_compute=dp.get_precision('Account'), string='Discounted Total',
            multi='all'),
    }
account_invoice()

class account_invoice_pay_writeoff(osv.osv_memory):
    """
    Opens the write off amount pay form.
    """
    _name = "account.invoice.pay.writeoff"
    _description = "Pay Invoice  "
    _columns = {
        'writeoff_acc_id': fields.many2one('account.account', 'Write-Off account', required=True),
        'writeoff_journal_id': fields.many2one('account.journal', 'Write-Off journal', required=True),
        'comment': fields.char('Comment', size=64, required=True),
        'analytic_id': fields.many2one('account.analytic.account','Analytic Account'),
        }
    _defaults = {
        'comment': 'Write-Off',
        }

account_invoice_pay_writeoff()

class account_invoice_pay(osv.osv_memory):
    """
    Generate pay invoice wizard, user can make partial or full payment for invoice.
    """
    _name = "account.invoice.pay"
    _description = "Pay Invoice  "
    _columns = {
        'amount': fields.float('Amount paid', required=True, digits_compute = dp.get_precision('Account')),
        'name': fields.char('Entry Name', size=64, required=True),
        'date': fields.date('Date payment', required=True),
        'journal_id': fields.many2one('account.journal', 'Journal/Payment Mode', required=True, domain=[('type','=','cash')]),
        'period_id': fields.many2one('account.period', 'Period', required=True),
        }

    def view_init(self, cr, uid, ids, context=None):
        invoice = self.pool.get('account.invoice').browse(cr, uid, context['active_id'], context=context)
        if invoice.state in ['draft', 'proforma2', 'cancel']:
            raise osv.except_osv(_('Error !'), _('Can not pay draft/proforma/cancel invoice.'))
        pass

    def _get_period(self, cr, uid, context=None):
        '''
        Initialise Period
        '''
        ids = self.pool.get('account.period').find(cr, uid, context=context)
        period_id = False
        if len(ids):
            period_id = ids[0]
        return period_id

    def _get_amount(self, cr, uid, context=None):
        '''
        Get default value of Amount paid
        '''
        return self.pool.get('account.invoice').browse(cr, uid, context['active_id'], context=context).residual

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'period_id': _get_period,
        'amount': _get_amount,
        }
account_invoice_pay()

class account_voucher(osv.osv):
    _name = 'account.voucher'
    _inherit = 'account.voucher'
    def calc_supp_diff(self, cr, uid, ids, context={}):
        '''
            Called by calculate/re-calculate action.
            This method will update the credit lines on voucher lines.
            If the field "auto_match" marked, this method will run a matching routine
        '''
        res = {'nodestroy':True}
        amount_cash_discount = 0.0
        amount_interest = 0.0
        
        for vch in self.browse(cr, uid, ids):
            for line in vch.line_dr_ids:
                '''
                    Update the credit lines and discount lines so that matching routine can use the latest available credits and discounts
                '''
#                line._update_debit_lines( context=context)
                line._update_supp_discount_lines(context=context)

#            if vch.auto_match:
#                '''
#                    Try the matching routine including the manual selection
#                '''
#                ret = self._find_exact_match(cr, uid, vch.line_cr_ids, vch.amount, mark_pay=False, use_discount=False, context=False)
#                if not ret:
#                    '''
#                        Try to match considering all voucher lines
#                    '''
#                    ret = self._find_exact_match(cr, uid, vch.line_cr_ids, vch.amount, mark_pay=True, use_discount=False, context=False)
#                if not ret:
#                    '''
#                        Try to match considering discount
#                    '''
#                    ret = self._find_exact_match(cr, uid, vch.line_cr_ids, vch.amount, mark_pay=True, use_discount=True, context=False)
            
        return res

    def _update_discounts(self, lines, vch_date):
        date_discount = False
        amount_discount = False
        for line in lines:
            if 'date_discount' in line:
                date_discount = line['date_discount']
                amount_discounted = line['amount_discounted']
            else:
                return
            if line['amount'] >= line['amount_unreconciled']:
                amount_discount = 0.0
            elif vch_date <= date_discount and line['amount'] <= line['amount_unreconciled'] and line['amount'] >= amount_discounted:
                amount_discount = max(line['amount_unreconciled'] - amount_discounted, 0.0)
            elif vch_date <= date_discount and line['amount'] < amount_discounted:
                amount_discount = max(line['amount_unreconciled'] - amount_discounted, 0.0)
            line['cash_discount'] = amount_discount
            line['amount_difference'] = line['amount_unreconciled'] - line['amount'] - amount_discount


    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context={}):
        '''
        Function to update fields in customer payment form on changing customer
        '''
        if context is None:
            context = {}
        currency_pool = self.pool.get('res.currency')
        journal_pool = self.pool.get('account.journal')
        invoice_pool = self.pool.get('account.invoice')
        line_pool = self.pool.get('account.voucher.line')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        company_currency = False

        default = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context={})
        if not partner_id:
            return default
        # we have to clear out lines, because new lines will be created by the change
        if partner_id and not journal_id:
            partner = partner_pool.browse(cr, uid, partner_id, context)
            if partner._columns.has_key('payment_meth_id') and partner.payment_meth_id:
                payment_mode_pool = self.pool.get('payment.mode')
                payment_meth = payment_mode_pool.browse(cr, uid, partner.payment_meth_id.id, context)
                if payment_meth:
                    default['value']['journal_id'] = payment_meth.journal.id
                    journal_id = payment_meth.journal.id
        if ids:
            line_ids = line_pool.search(cr, uid, [('voucher_id','=',ids[0])])
            if line_ids:
                line_pool.unlink(cr, uid, line_ids)
        if journal_id:
            journal = journal_pool.browse(cr, uid, journal_id)
            company_currency = journal.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        vch_date = False
        for vch in self.browse(cr, uid, ids):
            vch_date = vch.date
        if default and 'value' in default and 'line_cr_ids' in default['value']:
            for line in default['value']['line_cr_ids']:
                invoice_id = invoice_pool.search(cr, uid, [('number', '=', line['name'])])
                if invoice_id:
                    line['invoice_id'] = invoice_id[0]
                    invoice = invoice_pool.browse(cr, uid, invoice_id[0], )
                    date_discount = invoice.date_discount
                    amount_discounted = invoice.amount_discounted
                    line['date_discount'] = date_discount
                    line['amount_discounted'] = amount_discounted
                else:
                    line['date_discount'] = False
                    line['amount_discounted'] = 0.0
                line['amount'] = 0.0
                total_credit += line['type'] == 'cr' and line['amount_unreconciled'] or 0.0
                total_debit += line['type'] == 'dr' and line['amount_unreconciled'] or 0.0
            # first, see if we can find an invoice matching the amount to be applied
            found = False
            def calc_amount(line, total):
                return min(line['amount_unreconciled'], total)
            lines = default['value']['line_cr_ids']
            if len(lines) == 0:
                 return default
#                return False
            # if only one, assign it
            if len(lines) == 1:
                for line in lines:
                    if line['type'] == 'cr':
                        amount = price
                        line['amount'] = currency_pool.compute(cr, uid, company_currency, currency_id, amount) or amount
                        total_credit -= amount
                        found = True
                        break
                    else:
                        amount = price
                        line['amount'] = currency_pool.compute(cr, uid, company_currency, currency_id, amount) or amount
                        total_debit -= amount
                        found = True
                        break
                self._update_discounts(lines, vch_date)
            if not found:
                for line in lines:
                    if line['amount_unreconciled'] == price:
                        if line['type'] == 'cr':
                            amount = calc_amount(line, total_credit)
                            line['amount'] = currency_pool.compute(cr, uid, company_currency, currency_id, amount) or amount
                            total_credit -= amount
                            found = True
                            break
                        else:
                            amount = calc_amount(line, total_debit)
                            line['amount'] = currency_pool.compute(cr, uid, company_currency, currency_id, amount) or amount
                            total_debit -= amount
                            found = True
                            break
            if not found:
                # see if we can find a combination that matches
                def search(lines, price):
                    for i in range(0, len(lines)):
                        if lines[i]['amount_unreconciled'] == price:
                            return [lines[i]]
                    for i in range(0, len(lines)):
                        for j in range(i + 1, len(lines)):
                            if lines[i]['amount_unreconciled'] + lines[j]['amount_unreconciled'] == price:
                                return [lines[i],lines[j]]
                    for i in range(0, len(lines)):
                        for j in range(i + 1, len(lines)):
                            for k in range(j + 1, len(lines)):
                                if lines[i]['amount_unreconciled'] + lines[j]['amount_unreconciled'] + lines[k]['amount_unreconciled']== price:
                                    return [lines[i],lines[j],lines[k]]
                line_ids = search(lines, price)

                if line_ids: # and sum == price:
                    for line in line_ids:
                        if line['type'] == 'cr':
                            amount = calc_amount(line, line['amount_unreconciled'])
                            line['amount'] = currency_pool.compute(cr, uid, company_currency, currency_id, amount)
                            total_debit -= amount
                            found = True
                        else:
                            amount = calc_amount(line, line['amount_unreconciled'])
                            line['amount'] = currency_pool.compute(cr, uid, company_currency, currency_id, amount)
                            total_credit -= amount
                            found = True
            if not found:
                # see if we can find a match using discounted amount
                def search2(lines, price):
                    for i in range(0, len(lines)):
                        if min(lines[i]['amount_unreconciled'],lines[i]['amount_discounted']) == price:
                            return [lines[i]]
                    for i in range(0, len(lines)):
                        for j in range(i + 1, len(lines)):
                            if min(lines[i]['amount_unreconciled'],lines[i]['amount_discounted']) + min(lines[j]['amount_unreconciled'],lines[j]['amount_discounted']) == price:
                                return [lines[i],lines[j]]
                    for i in range(0, len(lines)):
                        for j in range(i + 1, len(lines)):
                            for k in range(j + 1, len(lines)):
                                if min(lines[i]['amount_unreconciled'],lines[i]['amount_discounted']) + min(lines[j]['amount_unreconciled'],lines[j]['amount_discounted']) + min(lines[k]['amount_unreconciled'],lines[k]['amount_discounted']) == price:
                                    return [lines[i],lines[j],lines[k]]
                line_ids = search(lines, price)
                lines = default['value']['line_cr_ids']
                line_ids = search2(lines, price)
                if line_ids:
                    for line in line_ids:
                        if line['type'] == 'cr':
                            amount = calc_amount(line, min(line['amount_unreconciled'],line['amount_discounted']))
                            line['amount'] = currency_pool.compute(cr, uid, company_currency, currency_id, min(line['amount_unreconciled'],line['amount_discounted']))
                            total_debit -= amount
                            found = True
                        else:
                            amount = calc_amount(line, min(line['amount_unreconciled'],line['amount_discounted']))
                            line['amount'] = currency_pool.compute(cr, uid, company_currency, currency_id, min(line['amount_unreconciled'],line['amount_discounted']))
                            total_credit -= amount
                            found = True
                lines = default['value']['line_cr_ids']
        '''
            FIXME : removing amount from line_dr_ids (Credits on customer payment form) line.
                    and amount from line_cr_ids (Invoice and outstanding transactions on customer payment form) line
                    I do not think this this is a good solution. But it works.
                    The whole "onchange_partner_id" function need a re-thinking (may have to rewrite it completely instead of calling super ).
        '''
        if default:
            for credit_line in default['value'].get('line_dr_ids',[]):
                credit_line['amount'] = 0.0
            for invoce_line in default['value'].get('line_cr_ids',[]):
                invoce_line['amount'] = 0.0
                invoce_line['amount_difference'] = invoce_line['amount_unreconciled']
        return default

    def calc_cash_discount(self, cr, uid, ids, vch, line, context={}):
        '''
            Calculate discount per line
        '''
        total_allocated = 0.0
        for line in vch.line_ids:
            total_allocated += line.amount
        context.update({'total_allocated': total_allocated, 'total_amount': vch.date})
        amount_discount = 0.0
        if line.amount >= line.amount_unreconciled or line.amount < 0.01 :
            amount_discount = 0.0
        elif line.amount >= line.amount_discounted and vch.date <= line.date_discount:
            amount_discount = line.amount_unreconciled - line.amount_discounted
        return amount_discount


    def onchange_amount(self, cr, uid, ids, amount, context={}):
        if not context:
            context = {}
        result = {}
        currency_format =  self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_format
        if currency_format=='us':
                amount_in_words = amount_to_words(amount)
        else: amount_in_words = amount_to_text(amount)
        result['amount_in_word']=amount_in_words
        return {'value':result}
account_voucher()

class account_voucher_line(osv.osv):
    _name = 'account.voucher.line'
    _inherit = 'account.voucher.line'
    def onchange_supp_pay(self, cr, uid, ids, line_amount, pay, amount_unreconciled,par_cr_ids, par_amount, credit_used, discount_used, writeoff_amount=0, context={}):
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
                if credit[2].get('pay'):
                    tot_amt -= (credit[2]['amount'])
            if tot_amt < 0:
                ret['amount'] = 0.0
            else:
                amount_unreconciled -= (discount_used+writeoff_amount+credit_used)
                ret['amount'] = min(tot_amt,(amount_unreconciled<0) and 0 or amount_unreconciled)
        else:
            ret['amount'] = 0.0
        return {'value':ret}
    def recalculate_supp_values(self, cr, uid, ids, context={}):
        '''
            Re-calculate button action
        '''
        if type(ids) == type([]):
            voucher_line = self.browse(cr,uid,ids[0])
        else:
            voucher_line = self.browse(cr,uid,ids)
        if voucher_line.discount_used:
            print "discount_useddiscount_useddiscount_useddiscount_useddiscount_useddiscount_useddiscount_useddiscount_useddiscount_useddiscount_used"
            self.write(cr,uid,ids,{'amount':voucher_line.amount_unreconciled - voucher_line.discount_used})
        self.pool.get('account.voucher').calc_supp_diff(cr, uid, [voucher_line.voucher_id.id])
        return True



    def _update_credit_lines(self,cr, uid, ids, context):
        '''
        Function to update the credit lines in payment lines
        '''
        credits_used_pool = self.pool.get('account.voucher.line.credits_to_use')
        for line in self.browse(cr , uid, ids, context):
            credits_lines_used = [x.orginal_credit_line_id.id for x in line.available_credits]
            for credit_line in line.voucher_id.line_dr_ids :
                if credit_line.id not in credits_lines_used and line.invoice_id and line.invoice_id.payment_term:
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

    def _update_discount_lines(self,cr, uid, ids, context):
        '''
        Function to update the discount lines in payment lines
        '''

        discount_used_pool = self.pool.get('account.voucher.line.discount_to_use')
        user_pool = self.pool.get('res.users')
        user = user_pool.browse(cr, uid, uid, context)
        for line in self.browse(cr , uid, ids, context):
            if line.invoice_id:
                if not line.invoice_id.date_discount or not line.voucher_id.date or  line.voucher_id.date > line.invoice_id.date_discount:
                    '''
                        customer is not eligible for the discount
                    '''
                    continue
                
                discount = line.invoice_id.amount_total  - line.invoice_id.amount_discounted
                date_discount = line.invoice_id.date_discount
                discount_found = False
                for discount_line in line.available_discounts:
                    #if abs(discount - discount_line.proposed_discount) < 0.01 and line.invoice_id.payment_term.id == discount_line.inv_payment_terms.id:
                    if line.invoice_id.payment_term.id == discount_line.inv_payment_terms.id:
                        discount_found = True
                        continue
                if not discount_found and user.company_id.sales_discount_account:
                    '''
                    TODO : calculate/findout the discount_window_date (The last day of the discount window. To receive discounts payments must be paid on or before this date.)
                    '''
                    discount_used_pool.create(cr, uid, {
                                'voucher_line_id': line.id,
                                'use_discount': False,
                                'inv_payment_terms':line.invoice_id.payment_term.id ,
                                'discount_window_date': date_discount,
                                'proposed_discount': discount,
                                'discount_amount': 0.0,
                                'gl_account':user.company_id.sales_discount_account.id
                                }, context=context)

    def _update_supp_discount_lines(self,cr, uid, ids, context):
        '''
        Function to update the discount lines in payment lines
        '''

        discount_used_pool = self.pool.get('account.voucher.line.discount_to_use')
        user_pool = self.pool.get('res.users')
        user = user_pool.browse(cr, uid, uid, context)
        for line in self.browse(cr , uid, ids, context):
            if line.invoice_id:
                if not line.invoice_id.date_discount or not line.voucher_id.date or  line.voucher_id.date > line.invoice_id.date_discount:
                    '''
                        customer is not eligible for the discount
                    '''
                    continue
                
                discount = line.invoice_id.amount_total  - line.invoice_id.amount_discounted
                date_discount = line.invoice_id.date_discount
                discount_found = False
                for discount_line in line.available_discounts:
                    #if abs(discount - discount_line.proposed_discount) < 0.01 and line.invoice_id.payment_term.id == discount_line.inv_payment_terms.id:
                    if line.invoice_id.payment_term.id == discount_line.inv_payment_terms.id:
                        discount_found = True
                        continue
                if not discount_found and user.company_id.purchase_discount_account:
                    '''
                    TODO : calculate/findout the discount_window_date (The last day of the discount window. To receive discounts payments must be paid on or before this date.)
                    '''
                    discount_used_pool.create(cr, uid, {
                                'voucher_line_id': line.id,
                                'use_discount': False,
                                'inv_payment_terms':line.invoice_id.payment_term.id ,
                                'discount_window_date': date_discount,
                                'proposed_discount': discount,
                                'discount_amount': 0.0,
                                'gl_account':user.company_id.purchase_discount_account.id
                                }, context=context)


    def _compute_discount_used(self, cr, uid, ids, name, args, context=None):
        '''
        Function to calculate the value of variable discount used
        '''
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = 0.0
            for discount_line in line.available_discounts:
                if discount_line.use_discount :
                    res[line.id] +=  discount_line.discount_amount
        return res

    def _compute_balance(self, cr, uid, ids, name, args, context=None):
        '''
        Function to calculate the value of variables Cash Discount, Interest and Amt Due
        '''
        currency_pool = self.pool.get('res.currency')
        rs_data = super(account_voucher_line, self)._compute_balance(cr, uid, ids, name, args, context)
        for line in self.browse(cr, uid, ids):
            amount_cash_discount = self.calc_cash_discount(cr, uid, ids, vch, line)
            amount_interest = self.calc_interest(vch, line, line.amount)
            amount_unreconciled = 0.0
            move_line = line.move_line_id or False
            if move_line:
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.amount_unreconciled - amount_cash_discount - line.writeoff)
            rs_data[line.id] = {'cash_discount': amount_cash_discount, 'interest': amount_interest, 'amount_unreconciled': amount_unreconciled}
        return rs_data

    def _get_discount(self, cr, uid,  ids, field_name, args, context={}):
        """
        Function to calculate the value of variable date_discount,amount_discounted,cash_discount,amount_difference
        return the values as dictionary
        """

        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        move_line_obj = self.pool.get('account.move.line')
        voucher_line = self.browse(cr, uid, ids)
        vch = self.pool.get('account.voucher').browse(cr, uid, voucher_line[0].voucher_id.id)
        res = {}
        for line in voucher_line:
            if line.type == 'dr':
                res[line.id] = {
                    'date_discount': '',
                    'amount_discounted': line.amount,
                    'cash_discount': 0.0,
                    'amount_difference': line.amount_unreconciled - line.amount ,
                }
                continue
            print "===========",line.move_line_id.id
            move_line = move_line_obj.browse(cr, uid, line.move_line_id.id)
            invoice_number = move_line.name or move_line.ref
            invoice_id = False
            if invoice_number and invoice_number != '/':
                invoice_id = invoice_obj.search(cr, uid, [('number', '=', str(invoice_number))])
            if not invoice_id:
                move = self.pool.get('account.move').browse(cr, uid, move_line.move_id.id)
                if move:
                    invoice_number = move.name or move.ref
                    if invoice_number and invoice_number != '/':
                        invoice_id = invoice_obj.search(cr, uid, [('number', '=', str(invoice_number))])
            if invoice_id:
                for invoice in invoice_obj.browse(cr, uid, invoice_id, context):
                    date_discount = invoice.date_due
                    amount_discounted = invoice.amount_total
                    res[line.id] = {
                        'date_discount': invoice.date_due,
                        'amount_discounted': invoice.amount_total
                    }
                    if not invoice.date_invoice:
                        invoice_date = mx.DateTime.today().strftime("%Y-%m-%d")
                        self.write(cr, uid, [invoice.id], {'date_invoice': invoice_date}, context)
                    else:
                        invoice_date = invoice.date_invoice
                    discounts = invoice.payment_term and invoice.payment_term.get_discounts(invoice_date, context=context) or False
                    if discounts:
                        line_obj = self.pool.get('account.invoice.line')
                        discount_total = 0.0
                        non_discount_total = 0.0
                        for invline in invoice.invoice_line:
                            if invline.cash_discount:
                                discount_total += invline.price_subtotal
                                line_cash_discount =  round((1.0 - discounts[0][1]) * invline.price_subtotal)
                                line_obj.write(cr, uid, invline.id, {'cash_discount': line_cash_discount}, context)
                            else:
                                non_discount_total += invline.price_subtotal
                                line_obj.write(cr, uid, invline.id, {'cash_discount': 0.0}, context)
                        # assume taxes are never discountable
                        non_discount_total += invoice.amount_tax
                        # There may be more than one - return the earliest
                        date_discount = discounts[0][0]
                        amount_discounted = round(((1.0 - discounts[0][1]) * discount_total) + non_discount_total,2)
                amount_discount = 0.0
                if line.amount >= line.amount_unreconciled or line.amount < 0.01:
                    amount_discount = 0.0
                elif vch.date <= date_discount and line.amount <= line.amount_unreconciled:
                    amount_discount = max(line.amount_unreconciled - amount_discounted, 0.0)
                elif vch.date <= date_discount and line.amount < amount_discounted:
                    amount_discount = max(line.amount_unreconciled - amount_discounted,0.0)
                else:
                    amount_discount = 0.0

                res[line.id] = {
                    'date_discount': date_discount,
                    'amount_discounted': amount_discounted,
                    'cash_discount': amount_discount,
                    'amount_difference': line.amount_unreconciled - line.amount - line.credit_used - line.discount_used - (line._columns.has_key('writeoff_amount') and line['writeoff_amount']),#- amount_discount
                }
        return  defaultdict(type([]),res)
    def _get_supp_discount(self, cr, uid,  ids, field_name, args, context={}):
        """
        Function to calculate the value of variable date_discount,amount_discounted,cash_discount,amount_difference
        return the values as dictionary
        """

        if context is None:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        move_line_obj = self.pool.get('account.move.line')
        voucher_line = self.browse(cr, uid, ids)
        vch = self.pool.get('account.voucher').browse(cr, uid, voucher_line[0].voucher_id.id)
        res = {}
        for line in voucher_line:
            if line.type == 'cr':
                res[line.id] = {
                    'date_discount': '',
                    'amount_discounted': line.amount,
                    'cash_discount': 0.0,
                    'supp_amount_difference': line.amount_unreconciled - line.amount ,
                    'discount' : False
                }
                continue
            move_line = move_line_obj.browse(cr, uid, line.move_line_id.id)
            invoice_number = move_line.name or move_line.ref
            invoice_id = False
            if invoice_number and invoice_number != '/':
                invoice_id = invoice_obj.search(cr, uid, [('number', '=', str(invoice_number))])
            if not invoice_id:
                move = self.pool.get('account.move').browse(cr, uid, move_line.move_id.id)
                if move:
                    invoice_number = move.name or move.ref
                    if invoice_number and invoice_number != '/':
                        invoice_id = invoice_obj.search(cr, uid, [('number', '=', str(invoice_number))])
            if invoice_id:
                for invoice in invoice_obj.browse(cr, uid, invoice_id, context):
                    date_discount = invoice.date_due
                    amount_discounted = invoice.amount_total
                    res[line.id] = {
                        'date_discount': invoice.date_due,
                        'supp_amount_difference': invoice.amount_total
                    }
                    if not invoice.date_invoice:
                        invoice_date = mx.DateTime.today().strftime("%Y-%m-%d")
                        self.write(cr, uid, [invoice.id], {'date_invoice': invoice_date}, context)
                    else:
                        invoice_date = invoice.date_invoice
                    discounts = invoice.payment_term and invoice.payment_term.get_discounts(invoice_date, context=context) or False
                    if discounts:
                        line_obj = self.pool.get('account.invoice.line')
                        discount_total = 0.0
                        non_discount_total = 0.0
                        for invline in invoice.invoice_line:
                            if invline.cash_discount:
                                discount_total += invline.price_subtotal
                                line_cash_discount =  round((1.0 - discounts[0][1]) * invline.price_subtotal)
                                line_obj.write(cr, uid, invline.id, {'cash_discount': line_cash_discount}, context)
                            else:
                                non_discount_total += invline.price_subtotal
                                line_obj.write(cr, uid, invline.id, {'cash_discount': 0.0}, context)
                        # assume taxes are never discountable
                        non_discount_total += invoice.amount_tax
                        # There may be more than one - return the earliest
                        date_discount = discounts[0][0]
                        amount_discounted = round(((1.0 - discounts[0][1]) * discount_total) + non_discount_total,2)
                amount_discount = 0.0
                if line.amount >= line.amount_unreconciled or line.amount < 0.01:
                    amount_discount = 0.0
                elif vch.date <= date_discount and line.amount <= line.amount_unreconciled:
                    amount_discount = max(line.amount_unreconciled - amount_discounted, 0.0)
                elif vch.date <= date_discount and line.amount < amount_discounted:
                    amount_discount = max(line.amount_unreconciled - amount_discounted,0.0)
                else:
                    amount_discount = 0.0
                discount=False
                if line.available_discounts:
#                if line.discount_used:
                    discount=True
                res[line.id] = {
                    'date_discount': date_discount,
                    'amount_discounted': amount_discounted,
                    'cash_discount': amount_discount,
                    'supp_amount_difference': line.amount_unreconciled - line.amount - line.credit_used - line.discount_used - (line._columns.has_key('writeoff_amount') and line['writeoff_amount']),#- amount_discount
                    'discount':discount
                }
        return  defaultdict(type([]),res)


    _columns = {
        'date_discount': fields.function(_get_discount, method=True, type='date', string='Discount Date',
            multi='all'),
        'amount_discounted': fields.function(_get_discount, method=True, type='float', digits_compute=dp.get_precision('Account'), string='Discounted Total',
            multi='all'),
        'cash_discount': fields.function(_get_discount, method=True, type='float', multi="all", digits_compute=dp.get_precision('Account'), string='Cash Discount',sequence=20),
        'amount_difference': fields.function(_get_discount, method=True, multi='all', type='float', string='Unpaid Amt', digits=(16, 2) ),
        'supp_amount_difference': fields.function(_get_supp_discount, method=True, multi='all', type='float', string='Unpaid Amt', digits=(16, 2) ),
        'interest': fields.float(string='Interest', digits=(16,2)),

        #'discount_used':fields.float('Discount used', readonly=True),
        'discount_used': fields.function(_compute_discount_used, method=True, type='float', string='Discount Used', store=False, readonly=True,sequence=10),
        'available_discounts':fields.one2many('account.voucher.line.discount_to_use', 'voucher_line_id', 'Available Discounts'  ),
        'discount': fields.function(_get_supp_discount, method=True, multi='all', type='boolean', string='Discount',  readonly=True, sequence=20)
    }
    def clear_values(self, cr, uid, ids, context={}):
        '''
        Clear the selected credits, discounts and writeoffs from voucher line
        '''
        voucher_line = self.browse(cr,uid,ids[0])
        if voucher_line._columns.has_key('writeoff_ids'):
            for lines in self.read(cr,uid,ids,['available_credits','writeoff_ids','available_discounts']):
                lines['writeoff_ids'] and self.pool.get('account.voucher.line.writeoff').unlink(cr,uid,lines['writeoff_ids'])
                lines['available_credits'] and self.pool.get('account.voucher.line.credits_to_use').write(cr,uid,lines['available_credits'],{
                                                                                                                            'use_credit':False,
                                                                                                                            'discount_amount':0.0})
                lines['available_discounts'] and self.pool.get('account.voucher.line.discount_to_use').write(cr,uid,lines['available_discounts'],{
                                                                                                                            'use_discount':False,
                                                                                                                        'discount_amount':0.0})
        else:
            for lines in self.read(cr,uid,ids,['available_credits','writeoff_ids','available_discounts']):
                lines['available_credits'] and self.pool.get('account.voucher.line.credits_to_use').write(cr,uid,lines['available_credits'],{
                                                                                                                            'use_credit':False,
                                                                                                                            'discount_amount':0.0})
                lines['available_discounts'] and self.pool.get('account.voucher.line.discount_to_use').write(cr,uid,lines['available_discounts'],{
                                                                                                                            'use_discount':False,
                                                                                                                        'discount_amount':0.0})
        return True
account_voucher_line()

class product_product(osv.osv):
    '''
        Add new account configuration fields to product
    '''
    _name = "product.product"
    _inherit = 'product.product'
    _columns = {
        'cash_discount': fields.boolean('Cash Discount?'),
        'purchase_discount_account': fields.many2one('account.account', 'Purchase Discount Account', domain=[('user_type','=','COGS')]),
        'sales_discount_account': fields.many2one('account.account', 'Sales Discount Account', domain=[('type','!=','view'),('type','!=','consolidation'),('user_type','ilike','income')]),
        'purchase_discount_journal': fields.many2one('account.journal', 'Purchase Discount Journal', domain=[('type','!=','view'),('type','!=','consolidation'),('type','=','purchase')]),
        'sales_discount_journal': fields.many2one('account.journal', 'Sales Discount Journal', domain=[('type','=','sale')]),
    }
    _defaults = {
        'cash_discount' : lambda *a : True,
    }
product_product()

class account_invoice_line(osv.osv):
    '''
        option to disable discount calculation per invoice line
    '''
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'
    _columns = {
        'cash_discount': fields.boolean('Cash Discount?'),
    }
    _defaults = {
        'cash_discount' : lambda *a : True,
    }
    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, address_invoice_id=False, currency_id=False, context=None):
        '''
            check if the discount is applicable to newly selected product
        '''
        result = {}
        result = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id, fposition_id, price_unit, address_invoice_id, currency_id, context)
        if product:
            res = self.pool.get('product.product').browse(cr, uid, product, context=context)
            result['value']['cash_discount'] = res.cash_discount
        else:
            result['value']['cash_discount'] = True
        return result
account_invoice_line()

class res_company(osv.osv):
    '''
        New account configuration fields on copmany form
    '''
    _name = 'res.company'
    _inherit = 'res.company'
    _columns = {
        'purchase_discount_account': fields.many2one('account.account', 'Purchase Discount Account', domain=[('user_type','=','COGS'),('type','!=','view'),('type','!=','consolidation')]),
        'sales_discount_account': fields.many2one('account.account', 'Sales Discount Account', domain=[('user_type','=','Income'),('type','!=','view'),('type','!=','consolidation')]),
        'purchase_discount_journal': fields.many2one('account.journal', 'Purchase Discount Journal', domain=[('type','=','purchase')]),
        'sales_discount_journal': fields.many2one('account.journal', 'Sales Discount Journal', domain=[('type','=','sale')]),
    }
res_company()

class account_voucher_line_discount_to_use(osv.osv):
    '''
        Dynamically generated discount lines that are applicable per voucher line
    '''
    _name = "account.voucher.line.discount_to_use"
    _rec_name = 'inv_credit'
    _columns = {
        'voucher_line_id': fields.many2one('account.voucher.line', 'Account Voucher Line', ondelete='cascade', readonly=True),
        'use_discount': fields.boolean('Use Discount',help='Used to indicate if the cash discount should be used/taken when calculating payment.', required=True),
        'inv_payment_terms': fields.many2one('account.payment.term', 'Invoice Payment Terms', help='Payments terms description', ),
        'discount_window_date': fields.date('Discount Window Date',help='The last day of the discount window. To receive discounts payments must be paid on or before this date.'),


        'proposed_discount': fields.float('Proposed Discount',help='This is the proposed full discount based on the Invoice Payment Terms and the Original Amount.', readonly=True),
        'discount_amount': fields.float('Discount Amt',help='Enter the amount of discount to be given.', required=True),
        'gl_account' : fields.many2one('account.account', 'G/L Account',help='Enter the General Ledger account number to record taking the cash discount.', required=True),
    }
    def onchage_use_discount(self, cr, uid, ids, use_discount, proposed_discount, context=None):
        '''
        Fill the value with proposed discount when use discount check box is clicked and remove the value when use discount is unchecked
        '''
        res = {}
        if use_discount:
            res['value'] = {'discount_amount': proposed_discount}
        else:
            res['value'] = {'discount_amount': 0}
        return res
    def onchage_discount_amount(self, cr, uid, ids, proposed_discount, discount_amount, context=None):
        '''
        Function to check discount amount entered in discount line of payment line
        '''
        res = {}
        if discount_amount < 0:
            res['value'] = {'discount_amount': 0, 'use_discount':False }
            res['warning'] = {'title': 'Discount not in the limit', 'message': 'Discount should not be a negative value.'}
            return res
        if discount_amount > proposed_discount:
            res['value'] = {'discount_amount': proposed_discount, 'use_discount':True }
            res['warning'] = {'title': 'Discount not in the limit', 'message': 'Please adjust the Discount Amt value to be less than or equal the Proposed Discount.'}
            return res
        if discount_amount == 0.0:
            res['value'] = { 'use_discount':False }
        else:
            res['value'] = { 'use_discount':True }
        return res
account_voucher_line_discount_to_use()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

