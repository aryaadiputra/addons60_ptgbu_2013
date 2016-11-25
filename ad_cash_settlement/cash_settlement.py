# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from lxml import etree

import netsvc
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _


class cash_settlement(osv.osv):
    
    def auto_recon(self, cr, uid, ids, context=None):
        #print "xxxxxxxxxxxxxx"
        reconcile_lines = []
        move_line_pool  = self.pool.get('account.move.line')
        search = self.pool.get('cash.settlement').search(cr, uid, [('state','=','posted')])
        browse = self.pool.get('cash.settlement').browse(cr, uid, search)
        
        no = 0
        for x in browse:
            no += 1
            print "############################", x.name, no
            settle_id   = x.id
            advance_id  = x.cash_advance_id.id
            advance_account = x.account_advance_id.id
            
            #print "ssssssssssssssssssssssssss",x.move_ids
            for y in x.move_ids:
                print y.account_id.name
                if y.account_id.id == advance_account and not y.reconcile_id:
                    reconcile_lines.append(y.id)
            
            
            #print "BBBBBBBBBBBBBBBBBBBBBBBBBB", x.cash_advance_id.move_ids
            for z in x.cash_advance_id.move_ids:
                if z.account_id.id == advance_account and not z.reconcile_id:
                    reconcile_lines.append(z.id)
            
            if len(reconcile_lines) == 2:
                #print "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP", len(reconcile_lines), settle_id
                #raise osv.except_osv(_('Error'), _('xxxx %s'))
                move_line_pool.reconcile(cr, uid, reconcile_lines, 'auto', False, False, False, context=None)
            else:
                print "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP", len(reconcile_lines), settle_id
            
            reconcile_lines = []
        return True
    
    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('type', False)

    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        if context.get('invoice_id', False):
            company_id = self.pool.get('account.invoice').browse(cr, uid, context['invoice_id'], context=context).company_id.id
            context.update({'company_id': company_id})
        periods = self.pool.get('account.period').find(cr, uid, context=context)
        return periods and periods[0] or False

    def _get_journal(self, cr, uid, context=None):
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
        res = journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
        return res and res[0] or False

    def _get_tax(self, cr, uid, context=None):
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        journal_id = context.get('journal_id', False)
        if not journal_id:
            ttype = context.get('type', 'bank')
            res = journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
            if not res:
                return False
            journal_id = res[0]

        if not journal_id:
            return False
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id
            return tax_id
        return False
    
    def _get_currency_base(self, cr, uid, context=None):
        
        currency_search = self.pool.get('res.currency').search(cr, uid, [('base','=',True)])
        currency_browse = self.pool.get('res.currency').browse(cr, uid, currency_search)
        
        for cur_id in currency_browse:
            id_currency = cur_id.id
            
        return id_currency

    def _get_currency(self, cr, uid, context=None):
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        journal_id = context.get('journal_id', False)
        if journal_id:
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
#            currency_id = journal.company_id.currency_id.id
            if journal.currency:
                return journal.currency.id
        return False

    def _get_partner(self, cr, uid, context=None):
        if context is None: context = {}
        return context.get('partner_id', False)

    def _get_reference(self, cr, uid, context=None):
        if context is None: context = {}
        return context.get('reference', False)

    def _get_narration(self, cr, uid, context=None):
        if context is None: context = {}
        return context.get('narration', False)

    def _get_amount(self, cr, uid, context=None):
        if context is None:
            context= {}
        return context.get('amount', 0.0)

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if context is None: context = {}
        return [(r['id'], (str("%.2f" % r['amount']) or '')) for r in self.read(cr, uid, ids, ['amount'], context, load='_classic_write')]

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        mod_obj = self.pool.get('ir.model.data')
        if context is None: context = {}

        def get_res_id(view_type, condition):
            result = False
            if view_type == 'tree':
                result = mod_obj.get_object_reference(cr, uid, 'cash_settlement', 'view_voucher_tree')
            elif view_type == 'form':
                if condition:
                    result = mod_obj.get_object_reference(cr, uid, 'cash_settlement', 'view_vendor_receipt_form')
                else:
                    result = mod_obj.get_object_reference(cr, uid, 'cash_settlement', 'view_vendor_payment_form')
            return result and result[1] or False

        if not view_id and context.get('invoice_type', False):
            view_id = get_res_id(view_type,context.get('invoice_type', False) in ('out_invoice', 'out_refund'))

        if not view_id and context.get('line_type', False):
            view_id = get_res_id(view_type,context.get('line_type', False) == 'customer')

        res = super(cash_settlement, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='partner_id']")
        if context.get('type', 'sale') in ('purchase', 'payment'):
            for node in nodes:
                node.set('domain', "[('supplier', '=', True)]")
            res['arch'] = etree.tostring(doc)
        return res

    def _compute_writeoff_amount(self, cr, uid, line_dr_ids, line_cr_ids, amount):
        debit = credit = 0.0
        for l in line_dr_ids:
            debit += l['amount']
        for l in line_cr_ids:
            credit += l['amount']
        return abs(amount - abs(credit - debit))

    def onchange_line_ids(self, cr, uid, ids, line_dr_ids, line_cr_ids, amount):
        if not line_dr_ids and not line_cr_ids:
            return {'value':{}}
        line_dr_ids = [x[2] for x in line_dr_ids]
        line_cr_ids = [x[2] for x in line_cr_ids]
        return {'value': {'writeoff_amount': self._compute_writeoff_amount(cr, uid, line_dr_ids, line_cr_ids, amount)}}

    def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
        if not ids: return {}
        res = {}
        debit = credit = 0.0
        for voucher in self.browse(cr, uid, ids, context=context):
            for l in voucher.line_dr_ids:
                debit += l.amount
            for l in voucher.line_cr_ids:
                credit += l.amount
            res[voucher.id] =  abs(voucher.amount - abs(credit - debit))
        return res
    
    def check_adv_method(self, cr, uid, ids):
        print "aaaaaa"
        for adv in self.browse(cr, uid, ids):
            if adv.advance_method == 'travel':
                return True
        return False
    
    def onchange_employee (self, cr, uid, ids, employee_id):
        
        try:
        
            employee_search = self.pool.get('hr.employee').search(cr, uid, [('id', '=', employee_id)])
        
            for onchange in self.pool.get('hr.employee').browse(cr, uid, employee_search):
                
                employee_partner = onchange.address_home_id.partner_id.id
                account_partner = onchange.address_home_id.partner_id.property_account_payable.id
                
            return {'value':{'partner_id': employee_partner, 'account_id': account_partner}}
        
        except: 
               
            result = {}
            
            warning = {
                    "title": ("The Employee not to set as Partner !"),
                    "message": ("Please Set Employee Partner before ")
                }
            
            
            return {'warning': warning, 'value':{'partner_id': result, 'account_id':result}}

    _name = 'cash.settlement'
    _description = 'Cash Settlement'
    _order = "date desc, id desc"
#    _rec_name = 'number'
    _columns = {
        'type':fields.selection([
            ('sale','Sale'),
            ('purchase','Purchase'),
            ('payment','Payment'),
            ('receipt','Receipt'),
        ],'Default Type', readonly=True, states={'draft':[('readonly',False)]}),
        'name':fields.char('Memo', size=256, readonly=False,),
        'date':fields.date('Settlement Payment', select=True, help="Effective date for accounting entries"),
        'receive_settle_date':fields.date('Settlement Receive', select=True, help="Date when Cost Control receive Settlement "),
        'journal_id':fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'account_id':fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'line_ids':fields.one2many('cash.settlement.line','voucher_id','Voucher Lines', readonly=True, states={'approve_lv3':[('readonly',False)]}),
        'line_cr_ids':fields.one2many('cash.settlement.line','voucher_id','Credits',
            domain=[('type','=','cr')], context={'default_type':'cr'}, readonly=True, states={'draft':[('readonly',False)]}),
        'line_dr_ids':fields.one2many('cash.settlement.line','voucher_id','Cash Settlement Lines',
            domain=[('type','=','dr')], context={'default_type':'dr'}, readonly=False, ),
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'narration':fields.text('Notes', readonly=True, states={'draft':[('readonly',False)]}),
        'currency_id':fields.many2one('res.currency', 'Currency', readonly=True,required=True),
#        'currency_id': fields.related('journal_id','currency', type='many2one', relation='res.currency', string='Currency', store=True, readonly=True, states={'draft':[('readonly',False)]}),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True, ),
        'state':fields.selection(
            [('draft','Open'),
             ('proforma','Pro-forma'),
             ('approve_lv2','Approve_lv2'),
             ('approve_lv3','Approve_lv3'),
             ('approve_lv4','Approve_lv4'),
             ('approve_lv5','Approve_lv5'),
             ('posted','Posted'),
             ('cancel','Cancelled')
            ], 'State', readonly=False, size=32,
            help=' * The \'Draft\' state is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma state,voucher does not have an voucher number. \
                        \n* The \'Posted\' state is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Cancelled\' state is used when user cancel voucher.'),
        'amount': fields.float('Total', digits_compute=dp.get_precision('Account'), required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'tax_amount':fields.float('Tax Amount', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft':[('readonly',False)]}),
        'reference': fields.char('Ref #', size=64, readonly=True, states={'draft':[('readonly',False)]}, help="Transaction reference number."),
        'number': fields.char('Number', size=32, readonly=False,),
        'move_id':fields.many2one('account.move', 'Account Entry'),
        'move_ids': fields.related('move_id','line_id', type='one2many', relation='account.move.line', string='Journal Items', readonly=True),
        'partner_id':fields.many2one('res.partner', 'Partner', change_default=1, readonly=True,),
        'audit': fields.related('move_id','to_check', type='boolean', relation='account.move', string='Audit Complete ?'),
        'pay_now':fields.selection([
            ('pay_now','Pay Directly'),
            ('pay_later','Pay Later or Group Funds'),
        ],'Payment', select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'tax_id':fields.many2one('account.tax', 'Tax', readonly=True, states={'draft':[('readonly',False)]}),
        'pre_line':fields.boolean('Previous Payments ?', required=False),
        'date_due': fields.date('Due Date', readonly=True, select=True, states={'draft':[('readonly',False)]}),
        'payment_option':fields.selection([
                                           ('without_writeoff', 'Keep Open'),
                                           ('with_writeoff', 'Reconcile with Write-Off'),
                                           ], 'Payment Difference', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'writeoff_acc_id': fields.many2one('account.account', 'Write-Off account', readonly=True, states={'draft': [('readonly', False)]}),
        'comment': fields.char('Write-Off Comment', size=64, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'analytic_id': fields.many2one('account.analytic.account','Write-Off Analytic Account', readonly=True, states={'draft': [('readonly', False)]}),
        'writeoff_amount': fields.function(_get_writeoff_amount, method=True, string='Write-Off Amount', type='float', readonly=True),
        'employee_id': fields.many2one("hr.employee","Employee",required=True, readonly=True,),
        'reserved' : fields.float("Reserved Amount", readonly=True),
        'account_advance_id':fields.many2one('account.account','Account', required=True, readonly=True,),
        'line_history_ids':fields.one2many('cash.advance.history','voucher_id','Voucher Lines', readonly=True,),
        'cash_advance_id': fields.many2one('cash.advance', 'Cash Advance ID', readonly=False),
        'cash_advance_ref': fields.char('Advance Ref.Number', size=32, readonly=True),
        'date_req': fields.date("Cash Advance Request Date", readonly=True),
        'settlement_check': fields.boolean('Settlement Check',help="Check after Corrected"),
        
        "settlement_amount": fields.float('Settlement Amount', required=False, readonly=True, states={"approve_lv2":[("readonly", False),("required", True)]}),
        'settlement_journal_id':fields.many2one('account.journal', 'Settlement Method', required=False, readonly=True, states={'approve_lv2':[('readonly',False),('required',True)]}),
        
        'advance_method' : fields.selection([
            ('general','General'),
            ('travel','Travel'),
            ],'Advance Method', select=True),
    }
    _defaults = {
        'period_id': _get_period,
        'partner_id': _get_partner,
        'journal_id':_get_journal,
        'currency_id': _get_currency_base,
        'reference': _get_reference,
        'narration':_get_narration,
        'amount': _get_amount,
        'type':_get_type,
        'state': 'draft',
        'pay_now': 'pay_later',
        'name': '',
        #'date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'cash.settlement',context=c),
        'tax_id': _get_tax,
        'payment_option': 'without_writeoff',
        'comment': _('Write-Off'),
        'settlement_check': False,
    }
    
    def compute_tax(self, cr, uid, ids, context=None):
        tax_pool = self.pool.get('account.tax')
        partner_pool = self.pool.get('res.partner')
        position_pool = self.pool.get('account.fiscal.position')
        voucher_line_pool = self.pool.get('cash.settlement.line')
        voucher_pool = self.pool.get('cash.settlement')
        if context is None: context = {}

        for voucher in voucher_pool.browse(cr, uid, ids, context=context):
            voucher_amount = 0.0
            for line in voucher.line_ids:
                voucher_amount += line.untax_amount or line.amount
                line.amount = line.untax_amount or line.amount
                voucher_line_pool.write(cr, uid, [line.id], {'amount':line.amount, 'untax_amount':line.untax_amount})

            if not voucher.tax_id:
                self.write(cr, uid, [voucher.id], {'amount':voucher_amount, 'tax_amount':0.0})
                continue

            tax = [tax_pool.browse(cr, uid, voucher.tax_id.id, context=context)]
            partner = partner_pool.browse(cr, uid, voucher.partner_id.id, context=context) or False
            taxes = position_pool.map_tax(cr, uid, partner and partner.property_account_position or False, tax)
            tax = tax_pool.browse(cr, uid, taxes, context=context)

            total = voucher_amount
            total_tax = 0.0

            if not tax[0].price_include:
                for tax_line in tax_pool.compute_all(cr, uid, tax, voucher_amount, 1).get('taxes', []):
                    total_tax += tax_line.get('amount', 0.0)
                total += total_tax
            else:
                for line in voucher.line_ids:
                    line_total = 0.0
                    line_tax = 0.0

                    for tax_line in tax_pool.compute_all(cr, uid, tax, line.untax_amount or line.amount, 1).get('taxes', []):
                        line_tax += tax_line.get('amount', 0.0)
                        line_total += tax_line.get('price_unit')
                    total_tax += line_tax
                    untax_amount = line.untax_amount or line.amount
                    voucher_line_pool.write(cr, uid, [line.id], {'amount':line_total, 'untax_amount':untax_amount})

            self.write(cr, uid, [voucher.id], {'amount':total, 'tax_amount':total_tax})
        return True

    def onchange_price(self, cr, uid, ids, line_ids, tax_id, partner_id=False, context=None):
        tax_pool = self.pool.get('account.tax')
        partner_pool = self.pool.get('res.partner')
        position_pool = self.pool.get('account.fiscal.position')
        res = {
            'tax_amount': False,
            'amount': False,
        }
        voucher_total = 0.0
        voucher_line_ids = []

        total = 0.0
        total_tax = 0.0
        for line in line_ids:
            line_amount = 0.0
            line_amount = line[2] and line[2].get('amount',0.0) or 0.0
            voucher_line_ids += [line[1]]
            voucher_total += line_amount

        total = voucher_total
        total_tax = 0.0
        if tax_id:
            tax = [tax_pool.browse(cr, uid, tax_id, context=context)]
            if partner_id:
                partner = partner_pool.browse(cr, uid, partner_id, context=context) or False
                taxes = position_pool.map_tax(cr, uid, partner and partner.property_account_position or False, tax)
                tax = tax_pool.browse(cr, uid, taxes, context=context)

            if not tax[0].price_include:
                for tax_line in tax_pool.compute_all(cr, uid, tax, voucher_total, 1).get('taxes', []):
                    total_tax += tax_line.get('amount')
                total += total_tax

        res.update({
            'amount':total or voucher_total,
            'tax_amount':total_tax
        })
        return {
            'value':res
        }

    def onchange_term_id(self, cr, uid, ids, term_id, amount):
        term_pool = self.pool.get('account.payment.term')
        terms = False
        due_date = False
        default = {'date_due':False}
        if term_id and amount:
            terms = term_pool.compute(cr, uid, term_id, amount)
        if terms:
            due_date = terms[-1][0]
            default.update({
                'date_due':due_date
            })
        return {'value':default}

    def onchange_journal_voucher(self, cr, uid, ids, line_ids=False, tax_id=False, price=0.0, partner_id=False, journal_id=False, ttype=False, context=None):
        """price
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        default = {
            'value':{},
        }

        if not partner_id or not journal_id:
            return default

        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        account_id = False
        tr_type = False
        if journal.type in ('sale','sale_refund'):
            account_id = partner.property_account_receivable.id
            tr_type = 'sale'
        elif journal.type in ('purchase', 'purchase_refund','expense'):
            account_id = partner.property_account_payable.id
            tr_type = 'purchase'
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
            tr_type = 'receipt'

        default['value']['account_id'] = account_id
        default['value']['type'] = ttype or tr_type

        vals = self.onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, context)
        default['value'].update(vals.get('value'))

        return default

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
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

        line_pool = self.pool.get('cash.settlement.line')
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
            amount_unreconciled = currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, abs(line.amount_residual_currency), context=context_multi_currency)
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': currency_pool.compute(cr, uid, line.currency_id and line.currency_id.id or company_currency, currency_id, line.currency_id and abs(line.amount_currency) or original_amount, context=context_multi_currency),
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
            }

            if line.credit:
                amount = min(amount_unreconciled, currency_pool.compute(cr, uid, company_currency, currency_id, abs(total_debit), context=context_multi_currency))
                rs['amount'] = amount
                total_debit -= amount
            else:
                amount = min(amount_unreconciled, currency_pool.compute(cr, uid, company_currency, currency_id, abs(total_credit), context=context_multi_currency))
                rs['amount'] = amount
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
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price)

        return default

    def onchange_date(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        """
        @param date: latest value from user input for field date
        @param args: other arguments
        @param context: context arguments, like lang, time zone
        @return: Returns a dict which contains new values, and context
        """
        if context is None: context = {}
        period_pool = self.pool.get('account.period')
        res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=context)
        if context.get('invoice_id', False):
            company_id = self.pool.get('account.invoice').browse(cr, uid, context['invoice_id'], context=context).company_id.id
            context.update({'company_id': company_id})
        pids = period_pool.find(cr, uid, date, context=context)
        if pids:
            if not 'value' in res:
                res['value'] = {}
            res['value'].update({'period_id':pids[0]})
        return res

    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, context=None):
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id

        vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
        vals['value'].update({'tax_id':tax_id})
        currency_id = journal.company_id.currency_id.id
        if journal.currency:
            currency_id = journal.currency.id
        #vals['value'].update({'currency_id':currency_id})
        return vals

    def proforma_voucher(self, cr, uid, ids, context=None):
        self.action_move_line_create(cr, uid, ids, context=context)
        return True
    
    def proforma_voucher2(self, cr, uid, ids, context=None):
        self.action_move_line_create2(cr, uid, ids, context=context)
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for voucher_id in ids:
            wf_service.trg_create(uid, 'cash.settlement', voucher_id, cr)
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def cancel_voucher(self, cr, uid, ids, context=None):
        reconcile_pool = self.pool.get('account.move.reconcile')
        move_pool = self.pool.get('account.move')
        move_pool_line = self.pool.get('account.move.line')
        obj_account_analytic_line = self.pool.get('account.analytic.line')
        
        for voucher in self.browse(cr, uid, ids, context=context):
            recs = []
            for line in voucher.move_ids:
                if line.reconcile_id:
                    recs += [line.reconcile_id.id]
                if line.reconcile_partial_id:
                    recs += [line.reconcile_partial_id.id]
            print "Cancel1"
            reconcile_pool.unlink(cr, uid, recs)
            print "Cancel2"
            if voucher.move_id:
                move_line = move_pool_line.search(cr, uid, [('move_id','=',voucher.move_id.id)])
                for l in move_line:
                    print "-----------------------", l
                    analytic_line_id = obj_account_analytic_line.search(cr, uid, [('move_id','=',l)])
                    if analytic_line_id:
                        obj_account_analytic_line.unlink(cr, uid, analytic_line_id)
                    
                
                print "Cancel3", voucher.move_id
                move_pool.button_cancel(cr, uid, [voucher.move_id.id])
                print "Cancel4"
                move_pool.unlink(cr, uid, [voucher.move_id.id])
                
                
                print "Cancel5"
        res = {
            'state':'cancel',
            'move_id':False,
        }
        self.write(cr, uid, ids, res)
        #################################Update Settled###################################
        self.pool.get('cash.advance').write(cr, uid, [voucher.cash_advance_id.id], {
                                 'status': 'advance',                                                   
                                                    })
        #############################################################################
        return True

    def unlink(self, cr, uid, ids, context=None):
        for t in self.read(cr, uid, ids, ['state'], context=context):
            if t['state'] not in ('draft', 'cancel'):
                raise osv.except_osv(_('Invalid action !'), _('Cannot delete Voucher(s) which are already opened or paid !'))
        return super(cash_settlement, self).unlink(cr, uid, ids, context=context)

    # TODO: may be we can remove this method if not used anyware
    def onchange_payment(self, cr, uid, ids, pay_now, journal_id, partner_id, ttype='sale'):
        res = {}
        if not partner_id:
            return res
        res = {'account_id':False}
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        if pay_now == 'pay_later':
            partner = partner_pool.browse(cr, uid, partner_id)
            journal = journal_pool.browse(cr, uid, journal_id)
            if journal.type in ('sale','sale_refund'):
                account_id = partner.property_account_receivable.id
            elif journal.type in ('purchase', 'purchase_refund','expense'):
                account_id = partner.property_account_payable.id
            else:
                account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
            res['account_id'] = account_id
        return {'value':res}
    
    def account_expense_check(self, cr, uid, ids):
        
        reserved_amount = self.browse(cr, uid,ids)
        for a in reserved_amount:
            reserved_amount = a.reserved
            amount = a.amount
        print "reserved_amount :", reserved_amount
        
        settlement_amount = abs(reserved_amount-amount)
        
        self.pool.get('cash.settlement').write(cr, uid, ids,{'settlement_amount':settlement_amount})
        
        cash_search = self.pool.get('cash.settlement.line').search(cr, uid, [('voucher_id','=',ids)])
        cash_browse = self.pool.get('cash.settlement.line').browse(cr, uid, cash_search)
        for cash_id in cash_browse:
            
            if not cash_id.account_id.id:
                raise osv.except_osv(_('Error !'), _('Please define a Expenses Account !'))
        
    def check_amount(self, cr, uid, ids, context=None):
        a = self.browse(cr, uid, ids)
        for b in a:
            total_amount = b.amount
            
        cr.execute("SELECT SUM(amount) FROM cash_settlement_line WHERE voucher_id in (%s)"% (tuple(ids)))
        sum_amount = cr.fetchone()[0]
        
        if total_amount != sum_amount:
            raise osv.except_osv(_('Error Amount !'), _('Please check your Total Amount !'))
    
    def action_move_line_create2(self, cr, uid, ids, context=None):
        print "ARYA12345"
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
        period_obj = self.pool.get('account.period')
        for inv in self.browse(cr, uid, ids, context=context):
           
            if inv.move_id:
                continue
            context_multi_currency = context.copy()
            context_multi_currency.update({'date': inv.date})
            
            ###
            period_id = period_obj.browse(cr,uid,[period_obj.find(cr, uid, inv.date, context=None)[0]],context=None)[0].id
            self.write(cr, uid, ids, {'period_id' : period_id})
            ###
            
            if inv.number:
                name = inv.number
            elif inv.journal_id.sequence_id:
                name = seq_obj.get_id(cr, uid, inv.journal_id.sequence_id.id)
            else:
                raise osv.except_osv(_('Error !'), _('Please define a sequence on the journal !'))
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
                'period_id': period_id or inv.period_id and inv.period_id.id or False
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
                context_multi_currency.update({'date': inv.date_req})
                credit = currency_pool.compute(cr, uid, current_currency, company_currency, inv.amount, context=context_multi_currency)
                
            elif inv.type in ('sale', 'receipt'):
                debit = currency_pool.compute(cr, uid, current_currency, company_currency, inv.amount, context=context_multi_currency)
                
            #credit = inv.reserved
            
            credit = currency_pool.compute(cr, uid, current_currency, company_currency, inv.reserved, context=context_multi_currency)
            
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            
            sign = debit - credit < 0 and -1 or 1
           
            #create the first line of the voucher
            
            cur_date = time.strftime('%Y-%m-%d')
            
            if inv.advance_method == 'travel':
                first_line_desc = inv.name + " " + inv.cash_advance_id.from_date_travel + " s/d " + " " + inv.cash_advance_id.to_date_travel
            else:
                first_line_desc = inv.name
            
            move_line = {
                #'name': inv.name or '/',
                'name': first_line_desc or '/',
                'debit': debit,
                'credit': credit,
                #'account_id': inv.account_id.id,
                'account_id': inv.account_advance_id.id,
                'move_id': move_id,
                'journal_id': inv.journal_id.id,
                'period_id': period_id or inv.period_id.id,
                'partner_id': inv.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * inv.amount or 0.0,
                'date': inv.date,
                'date_maturity': inv.date_due
            }
            adv_move_line_id = move_line_pool.create(cr, uid, move_line)
            
            print "inv.reserved :", inv.reserved
            print "settlement_amount :", inv.settlement_amount
            #balance_diff = inv.settlement_amount
            
            if inv.reserved < inv.amount:
                print "keluar Uang"
                xdebit = 0.0
                xcredit = inv.settlement_amount
                xcredit = currency_pool.compute(cr, uid, current_currency, company_currency, inv.settlement_amount, context=context_multi_currency)
                balance_diff = -1 * inv.settlement_amount
                xaccount_id = inv.settlement_journal_id.default_credit_account_id.id
                
            elif inv.reserved > inv.amount:
                print "Masuk Uang"
                xdebit = currency_pool.compute(cr, uid, current_currency, company_currency, inv.settlement_amount, context=context_multi_currency)
                #xdebit = inv.settlement_amount
                xcredit = 0.0
                balance_diff = inv.settlement_amount
                xaccount_id = inv.settlement_journal_id.default_debit_account_id.id
                print "xaccount_id :", inv.settlement_journal_id.default_debit_account_id.id
                
            else:
                print "Pas"
                xdebit = 0.0
                xcredit = 0.0
                balance_diff = inv.settlement_amount
                xaccount_id = inv.account_id.id
                print "xaccount_id :", xaccount_id
                
                
            print "balance_diff :----------------------->>", balance_diff
            move_line2 = {
                #'name': inv.name or '/',
                'name': first_line_desc,
                'debit': xdebit,
                'credit': xcredit,
                #'account_id': inv.account_id.id,
                'account_id': xaccount_id,
                'move_id': move_id,
                'journal_id': inv.journal_id.id,
                'period_id': period_id or inv.period_id.id,
                'partner_id': inv.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * inv.amount or 0.0,
                'date': inv.date,
                'date_maturity': inv.date_due
            }
#            if debit != 0.0 and credit != 0.0:
#                move_line_pool.create(cr, uid, move_line2)
            if xdebit == 0.0 and xcredit == 0.0:
                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            else:
                move_line_pool.create(cr, uid, move_line2)
            
            rec_list_ids = []
            line_total = debit - credit
            if inv.type == 'sale':
                
                line_total = line_total - currency_pool.compute(cr, uid, inv.currency_id.id, company_currency, inv.tax_amount, context=context_multi_currency)
            elif inv.type == 'purchase':
                
                context_multi_currency.update({'date': inv.date})
                line_total = line_total + currency_pool.compute(cr, uid, inv.currency_id.id, company_currency, inv.tax_amount, context=context_multi_currency)

            for line in inv.line_ids:
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
                    'period_id': period_id or inv.period_id.id,
                    ###########################Ambil Desc Dari Memo############################
                    #'name': line.name and line.name or '/',inv.name or '/',
                    #'name': inv.name or '/',
                    'name' : first_line_desc or '/',
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

            if inv.reserved == inv.amount and inv.settlement_amount != 0.0: 
                raise osv.except_osv(_('Writeoff Warning !'), _('Your Writeoff More than Rp.100,- !'))
                

            inv_currency_id = inv.currency_id or inv.journal_id.currency or inv.journal_id.company_id.currency_id
            if not currency_pool.is_zero(cr, uid, inv_currency_id, line_total):
                diff = line_total + balance_diff
                print "Diff :", diff
                absolut_diff = abs(diff)
                print "absolut_diff :", absolut_diff
                
                print "inv.reservedxxxx :", inv.reserved
                print "inv.amountxxxx ::", inv.amount
                
                if absolut_diff > 100:
                    #raise osv.except_osv(_('Writeoff Warning !'), _('%s   Your Writeoff More than Rp.100,- !'%(absolut_diff)))
                    raise osv.except_osv(_('Writeoff Warning !'), _('Your Writeoff More than Rp.100,- !'))
                
                account_id = False
                if inv.payment_option == 'with_writeoff':
                    account_id = inv.writeoff_acc_id.id
                elif inv.type in ('sale', 'receipt'):
                    account_id = inv.partner_id.property_account_receivable.id
                else:
                    account_id = inv.partner_id.property_account_payable.id
                    #account_balance_id = inv.partner_id.account_balance_id.id
                    rounding_account_id = inv.company_id.rounding_account_id.id
                move_line = {
                    #'name': name,
                    'name' : first_line_desc,
                    'account_id': rounding_account_id or account_id,
                    
                    #'account_id': account_id,
                    'period_id': period_id or inv.period_id.id,
                    'move_id': move_id,
                    'partner_id': inv.partner_id.id,
                    'date': inv.date,
                    'credit': diff > 0 and diff or 0.0,
                    'debit': diff < 0 and -diff or 0.0,
                    #'amount_currency': company_currency <> current_currency and currency_pool.compute(cr, uid, company_currency, current_currency, diff * -1, context=context_multi_currency) or 0.0,
                    #'currency_id': company_currency <> current_currency and current_currency or False,
                }
                
                if move_line['credit'] > 0 or move_line['debit'] > 0:
                    print "tttt", move_line['credit']
                    print "cccc", move_line['debit']
                    move_line_pool.create(cr, uid, move_line)
            self.write(cr, uid, [inv.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            self.pool.get('cash.advance').write(cr, uid, [inv.cash_advance_id.id], {
                                 'status': 'settled',                                                   
                                                                                    })
            
            ####Reconcile####
            move_id_adv     = inv.cash_advance_id.move_id.id
            adv_account = inv.account_advance_id.id
            
            print "+++++++++++++++++++++", inv, adv_account
            
            adv_search = move_line_pool.search(cr, uid, [('move_id','=', move_id_adv),('account_id','=',adv_account)])
            adv_browse = move_line_pool.browse(cr, uid, adv_search)
            for i in adv_browse:
                print "i.id---------------------------->>", i.id
                i.id
            
            reconcile_lines = []
            reconcile_lines.append(adv_move_line_id)
            reconcile_lines.append(i.id)
            
            move_line_pool.reconcile(cr, uid, reconcile_lines, 'auto', False, False, False, context=None)
            
            #################
            move_pool.post(cr, uid, [move_id], context={})
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    move_line_pool.reconcile_partial(cr, uid, rec_ids)
        return True

    
    def copy(self, cr, uid, id, default={}, context=None):
        default.update({
            'state': 'draft',
            'number': False,
            'move_id': False,
            'line_cr_ids': False,
            'line_dr_ids': False,
            'reference': False
        })
        if 'date' not in default:
            default['date'] = time.strftime('%Y-%m-%d')
        return super(cash_settlement, self).copy(cr, uid, id, default, context)

cash_settlement()

class cash_settlement_line(osv.osv):
    _name = 'cash.settlement.line'
    _description = 'Voucher Lines'
    _order = "move_line_id"

    def _compute_balance(self, cr, uid, ids, name, args, context=None):
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
        'voucher_id':fields.many2one('cash.settlement', 'Voucher', required=1, ondelete='cascade'),
        'name':fields.char('Description', size=256),
        'account_id':fields.many2one('account.account','Account', required=False),
        'partner_id':fields.related('voucher_id', 'partner_id', type='many2one', relation='res.partner', string='Partner'),
        'untax_amount':fields.float('Untax Amount'),
        'amount':fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'type':fields.selection([('dr','Debit'),('cr','Credit')], 'Cr/Dr'),
        'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),
        'move_line_id': fields.many2one('account.move.line', 'Journal Item'),
        'date_original': fields.related('move_line_id','date', type='date', relation='account.move.line', string='Date', readonly=1),
        'date_due': fields.related('move_line_id','date_maturity', type='date', relation='account.move.line', string='Due Date', readonly=1),
        'amount_original': fields.function(_compute_balance, method=True, multi='dc', type='float', string='Original Amount', store=True),
        'amount_unreconciled': fields.function(_compute_balance, method=True, multi='dc', type='float', string='Open Balance', store=True),
        'company_id': fields.related('voucher_id','company_id', relation='res.company', type='many2one', string='Company', store=True, readonly=True),
        ############Link Budget#############
        'advance_type_id':fields.many2one('advance.type','Advance Type', ),
        ####################################
    }
    _defaults = {
        'name': ''
    }

    def onchange_move_line_id(self, cr, user, ids, move_line_id, context=None):
        """
        Returns a dict that contains new values and context

        @param move_line_id: latest value from user input for field move_line_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        res = {}
        move_line_pool = self.pool.get('account.move.line')
        if move_line_id:
            move_line = move_line_pool.browse(cr, user, move_line_id, context=context)
            if move_line.credit:
                ttype = 'dr'
            else:
                ttype = 'cr'
            account_id = move_line.account_id.id
            res.update({
                'account_id':account_id,
                'type': ttype
            })
        return {
            'value':res,
        }

    def default_get(self, cr, user, fields_list, context=None):
        """
        Returns default values for fields
        @param fields_list: list of fields, for which default values are required to be read
        @param context: context arguments, like lang, time zone

        @return: Returns a dict that contains default values for fields
        """
        if context is None:
            context = {}
        journal_id = context.get('journal_id', False)
        partner_id = context.get('partner_id', False)
        journal_pool = self.pool.get('account.journal')
        partner_pool = self.pool.get('res.partner')
        values = super(cash_settlement_line, self).default_get(cr, user, fields_list, context=context)
        if (not journal_id) or ('account_id' not in fields_list):
            return values
        journal = journal_pool.browse(cr, user, journal_id, context=context)
        account_id = False
        ttype = 'cr'
        if journal.type in ('sale', 'sale_refund'):
            account_id = journal.default_credit_account_id and journal.default_credit_account_id.id or False
            ttype = 'cr'
        elif journal.type in ('purchase', 'expense', 'purchase_refund'):
            account_id = journal.default_debit_account_id and journal.default_debit_account_id.id or False
            ttype = 'dr'
        elif partner_id:
            partner = partner_pool.browse(cr, user, partner_id, context=context)
            if context.get('type') == 'payment':
                ttype = 'dr'
                account_id = partner.property_account_payable.id
            elif context.get('type') == 'receipt':
                account_id = partner.property_account_receivable.id

        values.update({
            'account_id':account_id,
            'type':ttype
        })
        return values
    
#    ##########################Link Budget#################################
#    def onchange_advance_type(self, cr, uid, ids, advance_type_id, employee_id, partner_id):
#        employee        = self.pool.get('hr.employee')
#        partner         = self.pool.get('res.partner')
#        advance_type    = self.pool.get('advance.type')
#        analytic        = self.pool.get('account.analytic.account')
#        
#        department     = employee.browse(cr, uid, employee_id).department_id.id
#        division       = employee.browse(cr, uid, employee_id).user_id.context_division_id.id
#        
#        if advance_type_id:
#            account_id          = advance_type.browse(cr, uid, advance_type_id).account_id.id
#            analytic_search     = analytic.search(cr, uid, [('department_id','=',department),('budget_expense','=',account_id)])
#            budget_analytic_id  = analytic.browse(cr, uid, analytic_search)[0].id
#            
#            budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('dept_relation','=',department)])
#            budget_line_browse = self.pool.get('ad_budget.line').browse(cr, uid, budget_line_search)
#            
#            
#            
#            if budget_line_browse:
#                #print "Dept ada", department
#                for budget_line_item in budget_line_browse:
#                    budget_line_analytic_id = budget_line_item.analytic_account_id.id
#                    
#                value = {'account_analytic_id' : budget_line_analytic_id, 'account_id' : account_id}
#            else :
#                value = {'account_analytic_id' : '', 'account_id' : account_id}
#            #print "analytic_account_id :::", analytic_account_id
#        
#        else :
#            value = {'account_analytic_id' : '', 'account_id' : ''}
#        
#        return {'value': value}
#    ######################################################################

##########################Link Budget#################################
    def onchange_advance_type(self, cr, uid, ids, advance_type_id, employee_id, partner_id):
        employee        = self.pool.get('hr.employee')
        partner         = self.pool.get('res.partner')
        advance_type    = self.pool.get('advance.type')
        analytic        = self.pool.get('account.analytic.account')
        division        = False
        
        department     = employee.browse(cr, uid, employee_id).department_id.id
        #division       = employee.browse(cr, uid, employee_id).user_id.context_division_id.id
        
        if employee.browse(cr, uid, employee_id).user_id:
            division   = employee.browse(cr, uid, employee_id).user_id.context_division_id.id
        
        if advance_type_id:
            print "222222222"
            account_id = advance_type.browse(cr, uid, advance_type_id).account_id.id
            if department:
                analytic_search     = analytic.search(cr, uid, [('department_id','=',department),('budget_expense','=',account_id)])
            elif division:
                analytic_search     = analytic.search(cr, uid, [('division_id','=',division),('budget_expense','=',account_id)])
            else:
                raise osv.except_osv(_('Department or Division not Define'), _('Please Check your Department or Division'))
        
            check_pool_budget = self.pool.get('pool.budget').check_pool_account(cr, uid, ids, account_id, department)
        
            if check_pool_budget['account_analytic_id']:
                print "check_pool_budget", check_pool_budget
                value = {'account_analytic_id' : check_pool_budget['account_analytic_id'], 'account_id' : account_id}
            else:
                if advance_type_id:
                    account_id          = advance_type.browse(cr, uid, advance_type_id).account_id.id
                    if department:
                        analytic_search     = analytic.search(cr, uid, [('department_id','=',department),('budget_expense','=',account_id)])
                    elif division:
                        analytic_search     = analytic.search(cr, uid, [('division_id','=',division),('budget_expense','=',account_id)])
                    else:
                        raise osv.except_osv(_('Department or Division not Define'), _('Please Check your Department or Division'))
                    if analytic_search:
                        budget_analytic_id  = analytic.browse(cr, uid, analytic_search)[0].id
                        
                        if department:
                            budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('dept_relation','=',department)])
                        else:
                            budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('div_relation','=',division)])
                        budget_line_browse = self.pool.get('ad_budget.line').browse(cr, uid, budget_line_search)
                        
                        if budget_line_browse:
                            print "masuk"
                            #print "Dept ada", department
                            for budget_line_item in budget_line_browse:
                                budget_line_analytic_id = budget_line_item.analytic_account_id.id
                            print "Adella Collection", account_id
                            value = {'account_analytic_id' : budget_line_analytic_id, 'account_id' : account_id}
                        else :
                            value = {'account_analytic_id' : '', 'account_id' : ''}
                    else:
                        
                        value = {'account_analytic_id' : '', 'account_id' : ''}
                
                else :
                    value = {'account_analytic_id' : '', 'account_id' : ''}
        else:
            print "okokokoko"
            value = {'account_analytic_id' : '', 'account_id' : ''}    
        return {'value': value}

#############################12 Maret 2013############################
#    def onchange_advance_type(self, cr, uid, ids, advance_type_id, employee_id, partner_id):
#        employee        = self.pool.get('hr.employee')
#        partner         = self.pool.get('res.partner')
#        advance_type    = self.pool.get('advance.type')
#        analytic        = self.pool.get('account.analytic.account')
#        
#        department     = employee.browse(cr, uid, employee_id).department_id.id
#        division       = employee.browse(cr, uid, employee_id).user_id.context_division_id.id
#        
#        if advance_type_id:
#            account_id              = advance_type.browse(cr, uid, advance_type_id).account_id.id
#            if department:
#                analytic_search     = analytic.search(cr, uid, [('department_id','=',department),('budget_expense','=',account_id)])
#            elif division:
#                analytic_search     = analytic.search(cr, uid, [('division_id','=',division),('budget_expense','=',account_id)])
#            else:
#                raise osv.except_osv(_('Department or Division not Define'), _('Please Check your Department or Division'))
#            if analytic_search:
#                budget_analytic_id  = analytic.browse(cr, uid, analytic_search)[0].id
#                
#                if department:
#                    budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('dept_relation','=',department)])
#                else:
#                    budget_line_search = self.pool.get('ad_budget.line').search(cr, uid, [('analytic_account_id','=',budget_analytic_id),('div_relation','=',division)])
#                budget_line_browse = self.pool.get('ad_budget.line').browse(cr, uid, budget_line_search)
#                
#                if budget_line_browse:
#                    #print "Dept ada", department
#                    for budget_line_item in budget_line_browse:
#                        budget_line_analytic_id = budget_line_item.analytic_account_id.id
#                        
#                    value = {'account_analytic_id' : budget_line_analytic_id, 'account_id' : account_id}
#                else :
#                    value = {'account_analytic_id' : '', 'account_id' : account_id}
#            else:
#                
#                value = {'account_analytic_id' : '', 'account_id' : account_id}
#            #print "analytic_account_id :::", analytic_account_id
#        
#        else :
#            value = {'account_analytic_id' : '', 'account_id' : ''}
#        
#        return {'value': value}
    ######################################################################
    
cash_settlement_line()

class cash_advance_history(osv.osv):
    _name = 'cash.advance.history'
    
    _columns = {
                'voucher_id':fields.integer("id"),
                'name_history':fields.char('Description', size=256, readonly=True),
                'amount_history':fields.float('Amount', digits_compute=dp.get_precision('Account'), readonly=True),
                }
    
cash_advance_history()