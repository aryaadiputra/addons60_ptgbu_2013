import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _

class account_invoice(osv.osv):
    
    _inherit = 'account.invoice'
    
    def action_check(self, cr, uid, ids, *args):
        
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        context = {}
        for inv in self.browse(cr, uid, ids):
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error !'), _('Please define sequence on invoice journal'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines !'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue
            
            if not inv.date_invoice_validation:
                self.write(cr, uid, [inv.id], {'date_invoice_validation':time.strftime('%Y-%m-%d')})
            
            if not inv.date_invoice_out:
                self.write(cr, uid, [inv.id], {'date_invoice_out':time.strftime('%Y-%m-%d')})
            
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice':time.strftime('%Y-%m-%d')})
            company_currency = inv.company_id.currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id)
            # check if taxes are all computed
            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

            if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0):
                raise osv.except_osv(_('Bad total !'), _('Please verify the price of the invoice !\nThe real total does not match the computed total.'))

    
    def reject(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"draft"})
        return True
    
    def action_note(self, cr, uid, ids,):
        
        #text = "Insert Your Reason In Here"
        text = ""
        obj_users = self.pool.get('res.users')
        account_invoice = self.browse(cr, uid, ids)
        
        for account_invoice_id in account_invoice:
            account_invoice_id.text
        
        if not account_invoice_id.text:
            raise osv.except_osv(_('Error'), _("Please Insert Your Reason."))
        else:
        
            user_id = uid
            user_search = obj_users.search(cr, uid, [('id','=', uid)])
            user_browse = obj_users.browse(cr, uid, user_search)
            for user_id in user_browse:
                user_name = user_id.name
            reason_time = time.strftime("%Y-%m-%d %H:%M:%S")
            self.write(cr, uid, ids, {'user': user_name})
            self.write(cr, uid, ids, {'note': "("+reason_time+")"+":"+ account_invoice_id.text})
            self.write(cr, uid, ids, {'text': text})
    
    
    def action_move_create(self, cr, uid, ids, *args):
        """Creates invoice related analytics and financial move lines"""
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        context = {}
        for inv in self.browse(cr, uid, ids):
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error !'), _('Please define sequence on invoice journal'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines !'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue
            if not inv.date_invoice_validation:
                self.write(cr, uid, [inv.id], {'date_invoice_validation':time.strftime('%Y-%m-%d')})
            

            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice':time.strftime('%Y-%m-%d')})
                
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice':time.strftime('%Y-%m-%d')})
            
            company_currency = inv.company_id.currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id)
            # check if taxes are all computed
            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
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
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml)
            acc_id = inv.account_id.id

            name = inv['name'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = self.pool.get('account.payment.term').compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                for t in totlines:
                    if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid,
                                company_currency, inv.currency_id.id, t[1])
                    else:
                        amount_currency = False

                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency

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

            date = inv.date_invoice or time.strftime('%Y-%m-%d')
            part = inv.partner_id.id

            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part, date, context={})),iml)

            line = self.group_lines(cr, uid, iml, line, inv)

            journal_id = inv.journal_id.id
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
            if journal.centralisation:
                raise osv.except_osv(_('UserError'),
                        _('Cannot create invoice move on centralised journal'))

            line = self.finalize_invoice_move_lines(cr, uid, inv, line)
            print "journal_id---->", journal_id
            move = {
                'ref': inv.reference and inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal_id,
                'date': date,
                'type': entry_type,
                'narration':inv.comment
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

            move_id = self.pool.get('account.move').create(cr, uid, move, context=context)
            new_move_name = self.pool.get('account.move').browse(cr, uid, move_id).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name})
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            self.pool.get('account.move').post(cr, uid, [move_id], context={'invoice':inv})
        self._log_event(cr, uid, ids)
        raise osv.except_osv(_('Error !'), _('Please define sequence on invoice journal'))
        return True

    
    _columns = {
            'date_invoice': fields.date('Receive Invoice Date', readonly=True, states={'draft':[('readonly', False)]}, select=True, help="Keep empty to use the current date"),
            'date_invoice_validation': fields.date('Invoice Validation Date', readonly=True, select=True, help="Keep empty to use the current date"),
            'reference': fields.char('Invoice Reference', size=64, help="The partner reference of this invoice.", states={'approved':[('readonly', True)],}),
            'check_total': fields.float('Supplier Payable', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft':[('readonly', False)]}),
            'payment_date': fields.date('Payment Date', select=True,),
            'date_invoice_out': fields.date('Invoice Date', readonly=True, states={'draft':[('readonly', False)]}, select=True, help="Keep empty to use the current date"),
            'user':fields.char('Note By', size=64),
            'text':fields.text('Text'),
            'note':fields.text('Notes', readonly=True),
            'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('wait_approve', 'Waiting Approve'),
            ('approved','Approved'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
            ('approve_lv2','Waitting CFO Cost Control Approve'),
            ('approve_lv2-1','Waitting CEO Cost Control Approve'),
            ('approve_lv3','Waitting Treasury Approve'),
            ('approve_lv4','Waitting CFO Payment Approve'),
            ('approve_lv5','Waitting CEO Approve'),
            ('approve_lv6','Approve Lv6'),
            ('approve_lv7','Approve Lv7'),
            ],'State', select=True, readonly=True,
            help=' * The \'Draft\' state is used when a user is encoding a new and unconfirmed Invoice. \
            \n* The \'Pro-forma\' when invoice is in Pro-forma state,invoice does not have an invoice number. \
            \n* The \'Open\' state is used when user create invoice,a invoice number is generated.Its in open state till user does not pay invoice. \
            \n* The \'Paid\' state is set automatically when invoice is paid.\
            \n* The \'Cancelled\' state is used when user cancel invoice.'),
            'create_record_date': fields.datetime('Create Invoice Date')
                }
    
    _defaults = {
            'create_record_date': lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
                 }
    
account_invoice()