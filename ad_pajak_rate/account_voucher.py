from osv import fields, osv
import time
from tools.translate import _

class account_voucher(osv.osv):
            
    def onchange_amount_total(self, cr, uid, ids, line_dr_ids, amount, context=None):
        total_amount = 0.0
        for x in line_dr_ids:
            amount_line = x[2]['amount']
            total_amount += amount_line
         
        return {
            'value' : {'amount' : total_amount}
        }
    
    _inherit = "account.voucher"
    
    _columns = {
                
                }
    
    
    def onchange_partner_id2(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        print "0okk0okk"
        """price
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        if context is None:
            context = {}
        if not journal_id:
            return {}
        context_multi_currency = context.copy()
        if date:
            context_multi_currency.update({'date': date})

        line_pool = self.pool.get('account.voucher.line')
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')

        vals = self.onchange_journal(cr, uid, ids, journal_id, [], False, partner_id, context)
        vals = vals.get('value')
        currency_id = vals.get('currency_id', currency_id)
        default = {
            'value':{'line_ids':[], 'line_dr_ids':[], 'line_cr_ids':[], 'pre_line': False, 'currency_id':currency_id},
                }

        if not partner_id:
            return default

        if not partner_id and ids:
            line_ids = line_pool.search(cr, uid, [('voucher_id', '=', ids[0])])
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
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id

        default['value']['account_id'] = account_id

        if journal.type not in ('cash', 'bank'):
            return default
        #print "price",price
        total_credit = 0.0
        total_debit = 0.0
        account_type = 'receivable'
        if ttype == 'payment':
            account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            account_type = 'receivable'

        if not context.get('move_line_ids', False):
            domain = [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)]
            if context.get('invoice_id', False):
                domain.append(('invoice', '=', context['invoice_id']))
            ids = move_line_pool.search(cr, uid, domain, context=context)
        else:
            ids = context['move_line_ids']
        ids.reverse()
        moves = move_line_pool.browse(cr, uid, ids, context=context)
        move_line_found = False
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        
        #===================EDITED 18 sept 2012=================================
        invoice_pool = self.pool.get('account.invoice')
        if invoice_id:
            inv = invoice_pool.browse(cr, uid, [invoice_id])[0]
        #=======================================================================
        
        if company_currency != currency_id and ttype == 'payment':
            total_debit = currency_pool.compute(cr, uid, currency_id, company_currency, total_debit, context=context_multi_currency)
        elif company_currency != currency_id and ttype == 'receipt':
            total_credit = currency_pool.compute(cr, uid, currency_id, company_currency, total_credit, context=context_multi_currency)

        for line in moves:
            if line.credit and line.reconcile_partial_id and ttype == 'receipt':
                continue
            if line.debit and line.reconcile_partial_id and ttype == 'payment':
                continue
            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_line_found = line.id
                    break
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_line_found = line.id
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit or 0.0
                total_debit += line.debit or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_line_found = line.id
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0
#        print "total_debit",total_debit
#        print "total_credit",total_credit
        for line in moves:
            if line.credit and line.reconcile_partial_id and ttype == 'receipt':
                continue
            if line.debit and line.reconcile_partial_id and ttype == 'payment':
                continue
            original_amount = line.credit or line.debit or 0.0
            
            #################################################
            inv_ids = self.pool.get('account.invoice').search(cr, uid, [('number','=',line.move_id.name)])
            in_id = in_no = in_or = False
            if inv_ids:
                inv = self.pool.get('account.invoice').browse(cr, uid, inv_ids)[0]
                in_id = inv.id
                in_no = inv.number
                in_or = inv.origin
                in_dp = inv.amount_dp
                in_cur = inv.currency_id.id
                
            #print 'in_id', in_no, in_id
            #################################################
            
            amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
            #print "amount_unreconciled=============>>", amount_unreconciled
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount': (move_line_found == line.id) and min(price, amount_unreconciled) or 0.0,
                'amount_original': currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, line.currency_id and abs(line.amount_currency) or original_amount, context=context_multi_currency),
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
                'invoice_id' : in_id,
                'amount_dp' : in_dp,
                'currency_id' : in_cur,
                
            }
            
            if not move_line_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount
                        
            print "aaaaaaaaaaaaa", rs['amount']

            default['value']['line_ids'].append(rs)
            #default['value']['move_id']['amount'].append(x)
            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if ttype == 'payment' and len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif ttype == 'receipt' and len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
                
            #print "default['value']['line_dr_ids'] :::", default['value']['line_dr_ids']
            #print "default['value']['line_cr_ids'] :::", default['value']['line_cr_ids']
            # default['value']['amount'] = 99999
            
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, in_dp)
        print "default", default['value']['writeoff_amount']
        return default['value']['writeoff_amount']
    
    def _compute_writeoff_amount(self, cr, uid, line_dr_ids, line_cr_ids, amount, in_dp=0):
#        print "in_dp ==============>>", in_dp
#        print "line_dr_ids ::", line_dr_ids
#        
#        
#        print "_compute_writeoff_amount"
#        print "amount :", amount
        debit = credit = 0.0
        for l in line_dr_ids:
            debit += l['amount']
            #print "debit += l['amount'] :::", debit
        for l in line_cr_ids:
            credit += l['amount']
            #print "credit += l['amount'] :::", credit
        #print "abs(amount - abs(credit - debit)) ================>>", abs(credit - debit) + in_dp
        #return abs(amount - abs(credit - debit))
        return abs(amount - (abs(credit - debit) + in_dp))
    
    def onchange_price2(self, cr, uid, ids, line_dr_ids, partner_id=False, context=None):
        
        res = {
            'amount': False,
            }
        total = 0.0
        
        for line in line_dr_ids:
            line_amount = 0.0
            #line_amount = line[8]
            line_amount = line[2] and line[2].get('amount',0.0) or 0.0
            #print "line_amount :::", line_amount
            total += line_amount
        res.update({
            'amount':total,
        })
        return {
            'value':res
        }

        
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        
        """price
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        print "xxxxxxxxxxxx123456"
        print  ids,partner_id, journal_id, price, currency_id, ttype, date
        if context is None:
            context = {}
        if not journal_id:
            return {}
        context_multi_currency = context.copy()
        if date:
            context_multi_currency.update({'date': date})

        line_pool = self.pool.get('account.voucher.line')
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')

        vals = self.onchange_journal(cr, uid, ids, journal_id, [], False, partner_id, context)
        vals = vals.get('value')
        currency_id = vals.get('currency_id', currency_id)
        default = {
            'value':{'line_ids':[], 'line_dr_ids':[], 'line_cr_ids':[], 'pre_line': False, 'currency_id':currency_id},
                }

        if not partner_id:
            return default

        if not partner_id and ids:
            line_ids = line_pool.search(cr, uid, [('voucher_id', '=', ids[0])])
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
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id

        default['value']['account_id'] = account_id

        if journal.type not in ('cash', 'bank'):
            return default
        #print "price",price
        total_credit = 0.0
        total_debit = 0.0
        account_type = 'receivable'
        if ttype == 'payment':
            account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            account_type = 'receivable'

        if not context.get('move_line_ids', False):
            print "x1"
            domain = [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)]
            if context.get('invoice_id', False):
                print "y1"
                domain.append(('invoice', '=', context['invoice_id']))
            print "CONTEXT------------------>>", context
            ids = move_line_pool.search(cr, uid, domain, context=context)
        else:
            print "x2"
            ids = context['move_line_ids']
        ids.reverse()
        moves = move_line_pool.browse(cr, uid, ids, context=context)
        move_line_found = False
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        
        #=======================================================================
        invoice_pool = self.pool.get('account.invoice')
        print "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",invoice_id
        if invoice_id:    
            inv = invoice_pool.browse(cr, uid, [invoice_id])[0]
        #=======================================================================
        
        if company_currency != currency_id and ttype == 'payment':
            #print "total_debit",total_debit,context_multi_currency,moves[0].amount_currency
#            total_tax = 0
#            if inv.with_tax_rate:
#                total_debit = currency_pool.compute(cr, uid, currency_id, company_currency, total_debit-inv.amount_ppn, context=context_multi_currency)
#                total_tax = currency_pool.compute_pajak_rate(cr, uid, currency_id, company_currency, inv.amount_ppn, context={'date': date or time.strftime('%Y-%m-%d')})
#            else:
#                total_debit = currency_pool.compute(cr, uid, currency_id, company_currency, total_debit, context=context_multi_currency)
#            total_debit = total_debit + total_tax
            #print "xxxxxxx",total_debit,total_tax
            total_debit = currency_pool.compute(cr, uid, currency_id, company_currency, total_debit, context=context_multi_currency)
        elif company_currency != currency_id and ttype == 'receipt':
            total_credit = currency_pool.compute(cr, uid, currency_id, company_currency, total_credit, context=context_multi_currency)

        for line in moves:
            if line.credit and line.reconcile_partial_id and ttype == 'receipt':
                continue
            if line.debit and line.reconcile_partial_id and ttype == 'payment':
                continue
            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_line_found = line.id
                    break
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_line_found = line.id
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit or 0.0
                total_debit += line.debit or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_line_found = line.id
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0
#        print "total_debit",total_debit
#        print "total_credit",total_credit
        print "MOVES", moves
        for line in moves:
            if line.credit and line.reconcile_partial_id and ttype == 'receipt':
                continue
            if line.debit and line.reconcile_partial_id and ttype == 'payment':
                continue
            original_amount = line.credit or line.debit or 0.0
            
            #################################################
            
            print "line.move_id.name", line.move_id.name
            #inv_ids = self.pool.get('account.invoice').search(cr, uid, [('number','=',line.move_id.name),('state','=','open')])
            inv_ids = self.pool.get('account.invoice').search(cr, uid, [('number','=',line.move_id.name),('state','=','open')])
            in_id = in_no = in_or = False
            if inv_ids:
                inv         = self.pool.get('account.invoice').browse(cr, uid, inv_ids)[0]
                in_id       = inv.id
                in_no       = inv.number
                in_or       = inv.origin
                in_dp       = inv.amount_dp
                in_cur      = inv.currency_id.id
                in_dp_id    = inv.downpayment_id.id
                #################Tester Multi Companies##################
                in_dp       = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(in_dp), context=context_multi_currency)
                ####################################
            #print 'in_id', in_no, in_id
            #################Filter SP##################
            else:
                continue
            #################################################
            
            amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
            amount_original = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, line.currency_id and abs(line.amount_currency) or original_amount, context=context_multi_currency)
            total_tax = 0
            if company_currency == currency_id and inv.with_tax_rate:
                total_tax = currency_pool.compute_pajak_rate(cr, uid, line.currency_id.id, company_currency, inv.amount_ppn, context={'date': date or time.strftime('%Y-%m-%d')})
                amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency-inv.amount_ppn), context=context_multi_currency) + total_tax
                amount_original = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, line.currency_id and abs(line.amount_currency+inv.amount_ppn) or original_amount, context=context_multi_currency) + total_tax
            #print "amount_unreconciled22222222=============>>", amount_unreconciled,total_tax,amount_original
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount': (move_line_found == line.id) and min(price, amount_unreconciled) or 0.0,
                'amount_original': amount_original,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
                'invoice_id' : in_id,
                #####################################
                'amount_dp' : in_dp,
                'downpayment_id' : in_dp_id,
                'amount_dp_original' : inv.amount_dp,
                #####################################
                'currency_id' : in_cur,
            }
#            x = {
#                'amount':3333333,
#                 }
            if not move_line_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount
            
            default['value']['line_ids'].append(rs)
            #default['value']['move_id']['amount'].append(x)
            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if ttype == 'payment' and len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif ttype == 'receipt' and len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
                
            #print "default['value']['line_dr_ids'] :::", default['value']['line_dr_ids']
            #print "default['value']['line_cr_ids'] :::", default['value']['line_cr_ids']
            # default['value']['amount'] = 99999
            
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price)
        #print "default", default['value']['writeoff_amount']
        return default
    
    
    def action_move_line_create(self, cr, uid, ids, context=None):
        print "action_move_line_create pajak rate"
        def _get_payment_term_lines(term_id, amount):
            term_pool = self.pool.get('account.payment.term')
            if term_id and amount:
                terms = term_pool.compute(cr, uid, term_id, amount)
                return terms
            return False
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        currency_pool = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        seq_obj = self.pool.get('ir.sequence')
        
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.move_id:
                continue
            context_multi_currency = context.copy()
            context_multi_currency.update({'date': inv.date})
            
            #print "inv",inv.line_ids[0]
            
            if inv.number:
                name = inv.number
            elif inv.journal_id.sequence_id:
                name = seq_obj.get_id(cr, uid, inv.journal_id.sequence_id.id)
            if not name:
                raise osv.except_osv(_('Error !'), _('Please define a sequence on the journal and make sure it is activated !'))
            if not inv.reference:
                ref = name.replace('/','')
            else:
                ref = inv.reference

            move = {
                'name': name,
                'journal_id': inv.journal_id.id,
                'narration': inv.narration,
                'date': inv.date,
                'ref': ref,
                'period_id': inv.period_id and inv.period_id.id or False
            }
            
            move_id = move_pool.create(cr, uid, move)
            
            #create the first line manually
            company_currency = inv.journal_id.company_id.currency_id.id
            current_currency = inv.currency_id.id
            debit = 0.0
            credit = 0.0
            # TODO: is there any other alternative then the voucher type ??
            # -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt
            if inv.type in ('purchase', 'payment'):
                credit = currency_pool.compute(cr, uid, current_currency, company_currency, inv.amount, context=context_multi_currency)
                #print "inv.amount",inv.amount
            elif inv.type in ('sale', 'receipt'):
                debit = currency_pool.compute(cr, uid, current_currency, company_currency, inv.amount, context=context_multi_currency)
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            sign = debit - credit < 0 and -1 or 1
            #create the first line of the voucher
            #print "Debit ::", debit
            #print "Credit ::", credit
            
            move_line = {
                'name': inv.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': inv.account_id.id,
                'move_id': move_id,
                'journal_id': inv.journal_id.id,
                'period_id': inv.period_id.id,
                'partner_id': inv.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * inv.amount or 0.0,
                'date': inv.date,
                'date_maturity': inv.date_due
            }
            print "xxxx1xxxx",move_line
            if move_line['credit'] > 0.0 or move_line['debit'] > 0.0:
                move_line_pool.create(cr, uid, move_line)
            rec_list_ids = []
            line_total = debit - credit
            if inv.type == 'sale':
                line_total = line_total - currency_pool.compute(cr, uid, inv.currency_id.id, company_currency, inv.tax_amount, context=context_multi_currency)
            elif inv.type == 'purchase':
                line_total = line_total + currency_pool.compute(cr, uid, inv.currency_id.id, company_currency, inv.tax_amount, context=context_multi_currency)
            
            
            check_amount_temp = 0.0
            for line in inv.line_ids:
                #create one move line per voucher line where amount is not 0.0
                #print "line.move_line_id",line.move_line_id.move_id.labeled_tax_amount
#                if not line.amount:
#                    continue
                ###################Agar Amount bs Nol########################
                if not line.amount and not line.is_pay:
                    continue
                ##############################################
                #############Cek Nilai Pembayaran##############
                check_amount_temp += line.amount
                #without_writeoff
                print "check_amount_temp------------------------->>", check_amount_temp, line.voucher_id.payment_option, line.voucher_id.amount
                ###############################################
                #we check if the voucher line is fully paid or not and create a move line to balance the payment and initial invoice if needed
                print "amount$$$$$$$", line.untax_amount ,'vs', line.amount, "DP", line.amount_dp
                ###########################DOWNPAYMENT###############################
                #if line.amount == line.amount_unreconciled:
                context_multi_currency_ap = context.copy()
                context_multi_currency_ap.update({'date': line.date_original})
                ##########################################################
                if line.amount == line.amount_unreconciled:
                    amount = line.move_line_id.amount_residual #residual amount in company currency
                    print "amount if", amount
                else:
                    print "context_multi_currency", context_multi_currency
                    print "context_multi_currency_ap", context_multi_currency_ap
                    print "line.untax_amount", line.untax_amount
                    print "line.amount", line.amount
                    print "aaa", current_currency, company_currency
                    #amount = currency_pool.compute(cr, uid, current_currency, company_currency, line.untax_amount or line.amount, context=context_multi_currency)
                    amount = currency_pool.compute(cr, uid, current_currency, company_currency, line.untax_amount or line.amount, context=context_multi_currency_ap)
                    
                    print "amount else", amount
                move_line = {
                    'journal_id': inv.journal_id.id,
                    'period_id': inv.period_id.id,
                    'name': line.name and line.name or '/',
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': inv.partner_id.id,
                    'currency_id': company_currency <> current_currency and current_currency or False,
                    'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': inv.date
                }
                
                ########################Buat DP DI REMOVE UTK DP PENGURANG AP############################
                amount_dp = 0.0
#                if line.downpayment_id:
#                    #print "amount_dp @@@::", amount_dp
#                    #print "line.currency_id ::", line.currency_id, "line.currency_id.id :::", line.currency_id.id, "company ::", company_currency, line.currency_id.id
#                    amount_dp = currency_pool.compute(cr, uid, current_currency or company_currency, company_currency, abs(line.amount_dp), context=context_multi_currency)
#                    downpayment_account_id = line.downpayment_id.dp_line[0].account_id.id
#                    #print "downpayment_account_id===================", downpayment_account_id
#                    #amount_dp = line.amount_dp
#                    #print "line.amount_dp112233", line.amount_dp
#                    #print "amount_dp Multi Currencies :::------->>", amount_dp
#                    #print "line.downpayment_id",line.downpayment_id
#                    move_line2 = {
#                        'name': '/',
#                        'debit': 0.0,
#                        #'credit': line.amount_dp,
#                        'credit': amount_dp,
#                        'account_id': downpayment_account_id,
#                        'move_id': move_id,
#                        'journal_id': inv.journal_id.id,
#                        'period_id': inv.period_id.id,
#                        'partner_id': inv.partner_id.id,
#                        'currency_id': company_currency <> current_currency and  current_currency or False,
#                        'amount_currency': company_currency <> current_currency and sign * inv.amount or 0.0,
#                        'date': inv.date,
#                        'date_maturity': inv.date_due
#                    }
#                    #print "xxxx2xxxx",move_line2
#                    #print "move_line['debit']123-------------------->>", move_line2['debit']
#                    #print "move_line['credit']123-------------------->>", move_line2['credit']
#                    ###########################Agar Debit & Credit 0 tidak Muncul#####
#                    #move_line_pool.create(cr, uid, move_line2)
#                    if move_line2['credit'] > 0.0 or move_line2['debit'] > 0.0:
#                        move_line_pool.create(cr, uid, move_line2)
#                    ############################################################
#                    #print "current_currency :::::%%%", current_currency
#                    amount_dp_used_multi = currency_pool.compute(cr, uid, current_currency or company_currency, line.currency_id.id, abs(line.amount_dp), context=context_multi_currency)
#                    #print "amount_dp_used_multi", amount_dp_used_multi
#                    downpayment_used = line.downpayment_id.downpayment_used + amount_dp_used_multi
#                    self.pool.get('downpayment').write(cr, uid, line.downpayment_id.id, {'downpayment_used':downpayment_used})
                ####################################################
                
                if amount < 0:
                    amount = -amount
                    if line.type == 'dr':
                        line.type = 'cr'
                    else:
                        line.type = 'dr'

                if (line.type=='dr'):
                    print "masuk11"
                    print "amount :::11", amount
                    line_total += amount
                    ############################################
                    #move_line['debit'] = amount + line.amount_dp
                    #print "amount vs amount_dp :::::", amount,"Vs" ,amount_dp
                    ####################Error GL#######################
                    #move_line['debit'] = amount + amount_dp
                    ################DP PENGURANG AP###################
                    move_line['debit'] = amount
                    #move_line['debit'] = amount
                    ############################################
                    ############################################
                    #move_line['debit'] = amount
                    print "move_line['debit']", move_line['debit']
                else:
                    line_total -= amount
                    move_line['credit'] = amount
                    print "move_line['credit']", move_line['credit']

                if inv.tax_id and inv.type in ('sale', 'purchase'):
                    move_line.update({
                        'account_tax_id': inv.tax_id.id,
                    })
                if move_line.get('account_tax_id', False):
                    tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                    if not (tax_data.base_code_id and tax_data.tax_code_id):
                        raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))
                sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                move_line['amount_currency'] = company_currency <> current_currency and sign * line.amount or 0.0
               # print "xxxx2xxxx",move_line
                voucher_line = move_line_pool.create(cr, uid, move_line)
                if line.move_line_id.id:
                    rec_ids = [voucher_line, line.move_line_id.id]
                    rec_list_ids.append(rec_ids)
            
#            #----------------------tambah disini buat gbu-------------
            #print "pppppppppppppppp"
            diff_adm = inv.adm_amount
            if inv.payment_adm == 'transfer' or inv.payment_adm == 'cheque':
                debit_adm = currency_pool.compute(cr, uid, current_currency, company_currency, diff_adm, context=context_multi_currency)
                credit_adm = currency_pool.compute(cr, uid, current_currency, company_currency, diff_adm, context=context_multi_currency)
                sign_adm = debit_adm - credit_adm < 0 and -1 or 1
                if inv.payment_adm == 'transfer':
                    cost_name = inv.adm_comment
                else:
                    cost_name = 'Cheque Fee'
                    
                move_line_adm_c = {
                    'name': cost_name,
                    'account_id': inv.account_id.id,
                    'move_id': move_id,
                    #'partner_id': inv.partner_id.id,
                    'date': inv.date,
                    'debit': 0,# < 0 and -diff or 0.0,
                    'credit': credit_adm,#diff > 0 and diff or 0.0,
                    'currency_id': company_currency <> current_currency and current_currency or False,
                    'amount_currency': company_currency <> current_currency and sign_adm * -diff_adm or 0.0,
                }
                account_id = inv.adm_acc_id.id
                move_line_adm_d = {
                    'name': cost_name,
                    'account_id': account_id,
                    'move_id': move_id,
                    #'partner_id': inv.partner_id.id,
                    'date': inv.date,
                    'debit': debit_adm,# < 0 and -diff or 0.0,
                    'credit': 0,#diff > 0 and diff or 0.0,
                    'currency_id': company_currency <> current_currency and current_currency or False,
                    'amount_currency': company_currency <> current_currency and sign_adm * diff_adm or 0.0,
                }
                #print "xxxx3xxxx",move_line_adm_c
                #print "xxxx4xxxx",move_line_adm_d
                if diff_adm != 0:
                    move_line_pool.create(cr, uid, move_line_adm_c)
                    move_line_pool.create(cr, uid, move_line_adm_d)
                    
            ############Pengecekan Amount#############
            if check_amount_temp <> line.voucher_id.amount and line.voucher_id.payment_option == 'without_writeoff':
                raise osv.except_osv(_('Error !'), _('Please Check Your Payment Amount !'))
            ##########################################
            #------------------------------------------------------
            print "line_total222", line_total
            inv_currency_id = inv.currency_id or inv.journal_id.currency or inv.journal_id.company_id.currency_id
            if not currency_pool.is_zero(cr, uid, inv_currency_id, line_total):
                print "line_total ::::", line_total
                diff = line_total
                account_id = False
                if inv.payment_option == 'with_writeoff':
                    account_id = inv.writeoff_acc_id.id
                elif inv.type in ('sale', 'receipt'):
                    account_id = inv.partner_id.property_account_receivable.id
                else:
                    ##################Ubah Untuk G/L############################
                    #account_id = inv.partner_id.property_account_payable.id
                    account_id = inv.company_id.gl_account_id.id or inv.partner_id.property_account_payable.id
                    #######################################################
                move_line = {
                    'name': name,
                    'account_id': account_id,
                    'move_id': move_id,
                    'partner_id': inv.partner_id.id,
                    'date': inv.date,
                    'credit': diff > 0 and diff or 0.0,
                    'debit': diff < 0 and -diff or 0.0,
                    #'amount_currency': company_currency <> current_currency and currency_pool.compute(cr, uid, company_currency, current_currency, diff * -1, context=context_multi_currency) or 0.0,
                    #'currency_id': company_currency <> current_currency and current_currency or False,
                }
                move_line_pool.create(cr, uid, move_line)
            self.write(cr, uid, [inv.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            ###Remove Auto Post###
            move_pool.post(cr, uid, [move_id], context={})
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    move_line_pool.reconcile_partial(cr, uid, rec_ids)
        return True
    
account_voucher()

class account_voucher_line(osv.osv):
    _inherit = "account.voucher.line"
    _description = 'Voucher Lines'
    _order = "move_line_id"
    
    def _compute_balance(self, cr, uid, ids, name, args, context=None):
        print "_compute_balance"
        currency_pool = self.pool.get('res.currency')
        rs_data = {}
        for line in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            ctx.update({'date': line.voucher_id.date})
            res = {}
            company_currency = line.voucher_id.journal_id.company_id.currency_id.id
            voucher_currency = line.voucher_id.currency_id.id
            move_line = line.move_line_id or False

            if not move_line:
                res['amount_original'] = 0.0
                res['amount_unreconciled'] = 0.0

            elif move_line.currency_id:
                res['amount_original'] = currency_pool.compute(cr, uid, move_line.currency_id.id, voucher_currency, move_line.amount_currency, context=ctx)
            elif move_line and move_line.credit > 0:
                res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.credit, context=ctx)
            else:
                res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.debit, context=ctx)

            if move_line:
                res['amount_unreconciled'] = currency_pool.compute(cr, uid, move_line.currency_id and move_line.currency_id.id or company_currency, voucher_currency, abs(move_line.amount_residual_currency), context=ctx)
            rs_data[line.id] = res
        return rs_data
    
    _columns = {
        'is_pay':fields.boolean("Full Payment",readonly=False ,states={'draft':[('readonly',True)]}),
                }
    def onchange_pay(self, cr, uid, ids, line_amount, pay, amount_unreconciled,par_cr_ids, par_amount, credit_used, discount_used=0, writeoff_amount=0, amount_dp=0, context={}):
        print "Amount DP :::", amount_dp, pay
        '''
        Function to automatically fill the values when the pay checkbox is selected
        '''
        
        #self.pool.get('account.voucher').onchange_price(cr, uid, ids, )
        
        x = {}
        ret = {}
        writeoff_amount = (not writeoff_amount and [0] or [writeoff_amount])[0]
        discount_used = (not discount_used and [0] or [discount_used])[0]
        credit_used = (not credit_used and [0] or [credit_used])[0]
#        
#        default ={}
#        default['value']['amount'] = 99999
#        
#        default = {
#            'value':{},
#                }
        
        if pay:
            tot_amt = par_amount + line_amount
            print "tot_amt----", tot_amt
            print "par_cr_ids---", par_cr_ids
            for credit in par_cr_ids:
                print "fffffff", credit
                try:
                    if credit[2]['pay']:
                        print "sinixxxx"
                        tot_amt -= (credit[2]['amount'])
                        print "wwwwww", (credit[2]['voucher_id'])
                        print "zzzzzzzzzzz", (credit[2]['amount'])
                        print "TOT2", tot_amt
                
                except:
                    pass
                
            if tot_amt < 0:
                ret['amount'] = 0.0
                #ret['voucher_id']['amount'] = 887777777777
            else:
                amount_unreconciled -= (discount_used+writeoff_amount+credit_used)
                #ret['amount'] = min(tot_amt,(amount_unreconciled<0) and 0 or amount_unreconciled)
                #################REmove Untuk DP pengurang AP ###################
                #ret['amount'] = amount_unreconciled - amount_dp
                ret['amount'] = amount_unreconciled
                #ret['voucher_id'].amount = 12
        else:
            ret['amount'] = 0.0
#        x['move_id']['amount'] = 1111
#        print "xxx:::", x
#        print "RET :::",ret
        return {'value':ret}
    
#    def onchange_pay(self, cr, uid, ids, line_amount, pay, amount_unreconciled,par_cr_ids, par_amount, credit_used, discount_used=0, writeoff_amount=0, context={}):
#        #print "Amount DP ::", amount_dp
#        '''
#        Function to automatically fill the values when the pay checkbox is selected
#        '''
#        ret = {}
#        writeoff_amount = (not writeoff_amount and [0] or [writeoff_amount])[0],
#        discount_used = (not discount_used and [0] or [discount_used])[0]
#        credit_used = (not credit_used and [0] or [credit_used])[0]
#        if pay:
#            ###############ASLI##################
#            tot_amt = par_amount + line_amount
#            for credit in par_cr_ids:
#                if credit[2]['pay']:
#                    tot_amt -= (credit[2]['amount'])
#            if tot_amt < 0:
#                ret['amount'] = 0.0
#            #####################################
#            
#            else:
#                amount_to_pay = 0.0
#                amount_unreconciled -= (discount_used+writeoff_amount+credit_used)
#                ret['amount'] = min(tot_amt,(amount_unreconciled<0) and 0 or amount_unreconciled)
#                amount_to_pay = ret['amount']
#                print "amount_to_pay :", amount_to_pay
#                
#                for y in self.browse(cr, uid ,ids):
#                    print "IDS ::::====>>", ids
#                    y.amount
#                 
#                #self.pool.get('account.voucher').onchange_amount(cr, uid, ids, amount_to_pay)
#        else:
#            ret['amount'] = 0.0
#        return {'value':ret}
    
account_voucher_line()