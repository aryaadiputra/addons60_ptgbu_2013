import time
from lxml import etree

import netsvc
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _

class account_voucher(osv.osv):
    _inherit = "account.voucher"
        
    _columns = {
        'payment_adm': fields.selection([
            ('cash','Cash'),
            ('free_transfer','Non Payment Administration Transfer'),
            ('transfer','Transfer'),
            ('cheque','Cheque'),
            ],'Payment Adm', readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'adm_acc_id': fields.many2one('account.account', 'Account Adm', readonly=True, states={'draft': [('readonly', False)]}),
        'adm_comment': fields.char('Comment Adm', size=128, required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'adm_amount': fields.float('Amount Adm', readonly=True, states={'draft': [('readonly', False)]}),
         'bank_id': fields.many2one("res.bank", "Bank", required=False, readonly=True, states={"draft":[("readonly", False)]}, select=2),
        'cheque_number': fields.char('Cheque No', size=128, required=False, readonly=True, states={'draft': [('readonly', False)]}),
        "cheque_start_date": fields.date("Cheque Date", required=False, readonly=True, states={"draft":[("readonly", False)]}),
        "cheque_end_date": fields.date("Cheque Expire Date", required=False, readonly=True, states={"draft":[("readonly", False)]}),
    }
    _defaults = {
        'payment_adm': 'cash'
    }
    
    def cancel_voucher(self, cr, uid, ids, context=None):
        reconcile_pool = self.pool.get('account.move.reconcile')
        move_pool = self.pool.get('account.move')
        #tambahan untuk ad_payment_adm
        cheque_pool = self.pool.get('account.cheque')
        #-----------------------------

        for voucher in self.browse(cr, uid, ids, context=context):
            #print "delete",voucher
            recs = []
            for line in voucher.move_ids:
                if line.reconcile_id:
                    recs += [line.reconcile_id.id]
                if line.reconcile_partial_id:
                    recs += [line.reconcile_partial_id.id]

            reconcile_pool.unlink(cr, uid, recs)
            if voucher.move_id:
                move_pool.button_cancel(cr, uid, [voucher.move_id.id])
                move_pool.unlink(cr, uid, [voucher.move_id.id])
        
        #tambah untuk ad_payment_adm
        cheque_id = cheque_pool.search(cr, uid, [('voucher_id','=',ids)])
        #print cheque_id
        cheque_pool.unlink(cr, uid, cheque_id)
        #---------------------------
        res = {
            'state':'cancel',
            'move_id':False,
        }
        self.write(cr, uid, ids, res)
        return True
    
    def proforma_voucher(self, cr, uid, ids, context=None):
        if self.browse(cr,uid,ids,context=None)[0].amount == 0.0:
            raise osv.except_osv(_('Error !'), _('Can not set Total/ Paid Amount is 0.0'))
        self.create_cheque(cr, uid, ids, context=context)
        self.action_move_line_create(cr, uid, ids, context=context)
        return True
    
    def create_cheque(self, cr, uid, ids, context=None):
        #self.action_move_line_create(cr, uid, ids, context=context)
        voucher_pool = self.pool.get('account.voucher')
        cheque_pool = self.pool.get('account.cheque')
        voucher_ids = voucher_pool.browse(cr, uid, ids)[0]
        #print "vocer",voucher_ids.id
        if voucher_ids.payment_adm == 'cheque':
            cheque = {
                    'name': voucher_ids.cheque_number,
                    'type': 'payment',
                    #'voucher': voucher_ids.number,
                    'voucher': "/",
                    'date': voucher_ids.cheque_start_date,
                    'date_end': voucher_ids.cheque_end_date,
                    'amount': voucher_ids.amount,
                    'voucher_id': voucher_ids.id,
                    'partner_id': voucher_ids.partner_id.id,
                    'state': 'paid',
                }
            #print "xxx",cheque
            cheque_pool.create(cr, uid, cheque)
        return True
    
    def action_move_line_create(self, cr, uid, ids, context=None):
        #print "action_move_line_create"
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
            print "Debit :", debit,"VS","Credit :", credit
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
            #print "xxxx1xxxx",move_line 
            move_line_pool.create(cr, uid, move_line)
            rec_list_ids = []
            line_total = debit - credit
            if inv.type == 'sale':
                line_total = line_total - currency_pool.compute(cr, uid, inv.currency_id.id, company_currency, inv.tax_amount, context=context_multi_currency)
            elif inv.type == 'purchase':
                line_total = line_total + currency_pool.compute(cr, uid, inv.currency_id.id, company_currency, inv.tax_amount, context=context_multi_currency)

            for line in inv.line_ids:
                ###################Cek Total##################
                cek_line_total  = 0.0
                cek_line_total  = cek_line_total + line.amount
                ###############################################
                #create one move line per voucher line where amount is not 0.0
                if not line.amount:
                    continue
                #we check if the voucher line is fully paid or not and create a move line to balance the payment and initial invoice if needed
                if line.amount == line.amount_unreconciled:
                    amount = line.move_line_id.amount_residual #residual amount in company currency
                else:
                    amount = currency_pool.compute(cr, uid, current_currency, company_currency, line.untax_amount or line.amount, context=context_multi_currency)
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
                
                #print "xxxx2xxxx",move_line
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
                    line_total -= amount
                    move_line['credit'] = amount

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
                voucher_line = move_line_pool.create(cr, uid, move_line)
                if line.move_line_id.id:
                    rec_ids = [voucher_line, line.move_line_id.id]
                    rec_list_ids.append(rec_ids)
            
#            #----------------------tambah disini buat gbu-------------
            #print "pppppppppppppppp"
            
            ###################Cek Total##################
            cek_total = inv.amount
            print "cek_total", cek_total
            if cek_total == 0.0:
                raise osv.except_osv(_('Error !'), _('You Can not Payment with Zero Amount !'))
            elif cek_total <> cek_line_total and inv.payment_option == 'without_writeoff':
                raise osv.except_osv(_('Error !'), _('Please Check Your Total Payment !'))
            #############################################
            
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
            #------------------------------------------------------
            
            inv_currency_id = inv.currency_id or inv.journal_id.currency or inv.journal_id.company_id.currency_id
            if not currency_pool.is_zero(cr, uid, inv_currency_id, line_total):
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
            move_pool.post(cr, uid, [move_id], context={})
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    move_line_pool.reconcile_partial(cr, uid, rec_ids)
        return True
account_voucher()