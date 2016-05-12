import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _


class account_invoice_tax(osv.osv):
    _inherit = "account.invoice.tax"

    _columns = {}

    def move_line_get(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_tax WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            if not t['amount'] \
                    and not t['tax_code_id'] \
                    and not t['tax_amount']:
                continue
            account_analytic_id = False
            
            
            res.append({
                'type':'tax',
                'name':t['name'],
                'price_unit': t['amount'],
                'quantity': 1,
                'price': t['amount'] or 0.0,
                'account_id': t['account_id'],
                'tax_code_id': t['tax_code_id'],
                'tax_amount': t['tax_amount'],
                'account_analytic_id' : t['account_analytic_id'],
            })
        return res
    
account_invoice_tax()
    
class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'with_tax_rate':fields.boolean("With Tax Rate",help="Check this field if you want to use tax rate different from currency rate",readonly=True ,states={'draft':[('readonly',False)]}),
        
                }
    
    
    def compute_invoice_totals(self, cr, uid, inv, company_currency, ref, invoice_move_lines):
        total = 0
        total_currency = 0
        cur_obj = self.pool.get('res.currency')
        for i in invoice_move_lines:
            if inv.currency_id.id != company_currency:
                i['currency_id'] = inv.currency_id.id
                i['amount_currency'] = i['price']
                if i['type']=="tax":
                    if inv.currency_id != company_currency and inv.with_tax_rate:
                        i['price'] = cur_obj.compute_pajak_rate(cr, uid, inv.currency_id.id, company_currency, i['price'],context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
                        i['tax_amount']=i['price']
                    else:
                        i['price'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, i['price'],context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
                else:
                    i['price'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, i['price'],context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
            else:
                i['amount_currency'] = False
                i['currency_id'] = False
            i['ref'] = ref
            if inv.type in ('out_invoice','in_refund'):
                total += i['price']
                total_currency += i['amount_currency'] or i['price']
                i['price'] = - i['price']
            else:
                total -= i['price']
                total_currency -= i['amount_currency'] or i['price']
        print "invoice_move_lines",invoice_move_lines
        return total, total_currency, invoice_move_lines
    
    def action_move_create(self, cr, uid, ids, *args):
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        context = {}
        ml_pool = self.pool.get('account.move.line')
        retention_amount = 0.0
        for inv in self.browse(cr, uid, ids):
            ####################RETENTION######################
            for ret in inv.invoice_line:
                retention_amount += ret.retention
            ###################################################
            print "retention_amount>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.", retention_amount
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error !'), _('Please define sequence on invoice journal'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines !'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice':time.strftime('%Y-%m-%d')})
            company_currency = inv.company_id.currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id)
            # check if taxes are all computed
            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            
            ####################################################################
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            ####################################################################
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

            if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0):
                raise osv.except_osv(_('Bad total !'), _('Please verify the price of the invoice !\nThe real total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise osv.except_osv(_('Error !'), _("Cannot create the invoice !\nThe payment term defined gives a computed amount greater than the total invoiced amount."))

            # one move line per tax line
            iml += ait_obj.move_line_get(cr, uid, inv.id)
            
            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = self._convert_ref(cr, uid, inv.number)
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'

            diff_currency_p = inv.currency_id.id <> company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            #print "IML",iml
            #print "11111111111111111111 iml",iml, "TOTAL", total
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml)
            ##########################Downpayment AP - DP#####################
            if inv.amount_dp > 0.0:
                total = total + inv.amount_dp
            ##########################RETENTION###############################
            #if inv.invoice_line[0].retention > 0.0:
            if inv.retention_check == True:
                total = total - cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, -retention_amount)
                #total = total - cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, -inv.invoice_line[0].retention)
                #total = total - (-inv.invoice_line[0].retention)
            ##################################################################
            #print "22222222222222222222 iml",iml, "TOTAL", total
            acc_id = inv.account_id.id
            #print "total, total_currency, iml ",total,"\r\n" ,total_currency,"\r\n" , iml 
            name = inv['name'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = self.pool.get('account.payment.term').compute(cr,uid, inv.payment_term.id, total, inv.date_invoice or False)
            
            #print "totlines",totlines
            
            if totlines:
                res_amount_currency = total_currency
                i = 0
                for t in totlines:
                    #print "iiiiiiiiiiiiiiiii",i
                    if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid,company_currency, inv.currency_id.id, t[1])
                    else:
                        amount_currency = False

                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency
                    #print "***********************************************",t[1]
                    print "amount_currency%%%%%%%%%%%%%%%%%%%%%%%", amount_currency
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': acc_id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency_p \
                                and  amount_currency or False,
                        'currency_id': diff_currency_p \
                                and inv.currency_id.id or False,
                        'ref': ref,
                    })
            else:
                #print "######################################################", total
#                ##########################RETENTION###############################
#                if inv.invoice_line[0].retention > 0.0:
#                    total = total - (-inv.invoice_line[0].retention)
#                ##################################################################
                print "total_currency+++++++++++++++++++++++++++++", total_currency
                ##########################RETENTION###############################
                if inv.retention_check == True:
                     total_currency = total_currency - -(retention_amount)
                     #total_currency = total_currency - -(inv.invoice_line[0].retention)
                ###################################################################
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': acc_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and total_currency or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref
            })
                
            ##########################Create DOWNPAYMENT lINE JOURNAL###############################
            if inv.amount_dp > 0.0:
                amount_dp = -inv.amount_dp
                downpayment_account_id = inv.downpayment_id.dp_line[0].account_id.id
                
                if inv.currency_id.id != company_currency:
                    amount_currency = cur_obj.compute(cr, uid,company_currency, inv.currency_id.id, amount_dp)
                else:
                    amount_currency = False
                
                amount_dp = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, amount_dp)
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': amount_dp,
                    'account_id': downpayment_account_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and retention_amount or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref
            })
            #########################################################
            
            ##########################RETENTION###############################
            #if inv.invoice_line[0].retention > 0.0:
            if inv.retention_check == True:
                #price = -inv.invoice_line[0].retention
                price = -retention_amount
                retention_account_id = inv.company_id.retention_account_id.id
                if not retention_account_id:
                    raise osv.except_osv(_('No Retention Account !'),_("You must define a retention account !"))
                
                if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid,company_currency, inv.currency_id.id, price)
                else:
                    amount_currency = False
                
                #print "masuk Retention", -inv.invoice_line[0].retention
                price_cur = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, price)
                print "price_cur-------->>", price_cur
                print "amount Cuee*******>>", amount_currency
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': price_cur,
                    'account_id': retention_account_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and retention_amount or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref
            })
            #########################################################
            
            
            date = inv.date_invoice or time.strftime('%Y-%m-%d')
            part = inv.partner_id.id
            
            #print "iml!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", iml

            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part, date, context={})),iml)

            line = self.group_lines(cr, uid, iml, line, inv)
            
            #print "---------------->>***", line

            journal_id = inv.journal_id.id
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
            if journal.centralisation:
                raise osv.except_osv(_('UserError'),
                        _('Cannot create invoice move on centralised journal'))

            line = self.finalize_invoice_move_lines(cr, uid, inv, line)
            totaltxx=0
            for txx in inv.tax_line:
                totaltxx+=txx.amount
            #print 'txx################################',totaltxx
            move = {
                'ref': inv.reference and inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal_id,
                'date': date,
                'type': entry_type,
                'narration':inv.comment,
                'labeled_tax_amount':totaltxx or 0.0,
                'with_tax_rate':inv.with_tax_rate,
            }
            period_id = inv.period_id and inv.period_id.id or False
            if not period_id:
                period_ids = self.pool.get('account.period').search(cr, uid, [('date_start','<=',inv.date_invoice or time.strftime('%Y-%m-%d')),('date_stop','>=',inv.date_invoice or time.strftime('%Y-%m-%d')), ('company_id', '=', inv.company_id.id)])
                if period_ids:
                    period_id = period_ids[0]
            if period_id:
                move['period_id'] = period_id
                for i in line:
                    i[2]['period_id'] = period_id
            
            #print "MOVE::::::::::::::",move
            
            move_id = self.pool.get('account.move').create(cr, uid, move, context=context)
            
            new_move_name = self.pool.get('account.move').browse(cr, uid, move_id).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name})
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            self.pool.get('account.move').post(cr, uid, [move_id], context={'invoice':inv})
        self._log_event(cr, uid, ids)
        #raise osv.except_osv(_('Error !'), _('You cannot cancel the Invoice which is Partially Paid! You need to unreconcile concerned payment entries!'))
        return True

account_invoice()