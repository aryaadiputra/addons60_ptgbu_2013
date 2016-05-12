import time
from datetime import datetime
from operator import itemgetter

import netsvc
from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import tools

class bank_transaction(osv.osv):
    _name = "bank.transaction"
    _description = "Bank Transaction"
    
    
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
    
    def _sum_balance(self, cr, uid, ids, name, args, context=None):
        #print "sum balance", ids,"-",name,"-",args,"-",context
        move_pool=self.pool.get('account.move')
        res = {}
        
        for bts in self.browse(cr,uid,ids,context=context):
            #print "xxxxx",bts.period_id, "---",bts.journal_id
            move_ids=move_pool.search(cr,uid,[('period_id','=',bts.period_id.id),('journal_id','=',bts.journal_id.id)])
            #print "move_ids",move_ids
            for move in move_pool.browse(cr,uid,move_ids):
                print ""
                
                #res[bts.id]+=move.amount
        #print 'res',res
        return res
    
    def _get_currency_base(self, cr, uid, context=None):
        
        currency_search = self.pool.get('res.currency').search(cr, uid, [('base','=',True)])
        currency_browse = self.pool.get('res.currency').browse(cr, uid, currency_search)
        
        for cur_id in currency_browse:
            id_currency = cur_id.id
            #rate = cur_id.rate
        return id_currency
    
    def _get_rate_base(self, cr, uid, context=None):
        
        currency_search = self.pool.get('res.currency').search(cr, uid, [('base','=',True)])
        currency_browse = self.pool.get('res.currency').browse(cr, uid, currency_search)
        
        for cur_id in currency_browse:
            #id_currency = cur_id.id
            rate = cur_id.rate
        current_rate = 1 / rate
        return current_rate
    
    _columns = {
        #'name' : fields.char('Transaction Number', 64,required=True,readonly=True, states={'draft':[('readonly',False)]}),
        'name' : fields.char('Transaction Number', 64,required=True,readonly=True, ),
        'ref' : fields.char('Ref',64,readonly=True, states={'draft':[('readonly',False)]}),
        'note' : fields.text('Notes'),
        'date' : fields.date('Date Effective',required=True,readonly=True, states={'draft':[('readonly',False)]}),
        'source_rate':fields.float('Source Rate',digit=(16,2),readonly=True, states={'draft':[('readonly',False)]}),
        'period_id': fields.many2one('account.period','Period',required=True,readonly=True, states={'draft':[('readonly',False)]}),
        'partner_id' : fields.many2one('res.partner','Partner',readonly=True, states={'draft':[('readonly',False)]}),
        'date_created': fields.date('Creation date', select=True,readonly=True, states={'draft':[('readonly',False)]}),
        'amount':fields.float('Amount Total',digit=(16,2),required=True,readonly=True, states={'draft':[('readonly',False)]}),
        'state':fields.selection([('draft','Draft'), ('app_lv1','Waitting CFO Approve'),('app_lv2','Ready to Post'),('posted','Posted')], 'State', readonly=True,
                          help='When bank transaction is created the state will be \'Draft\'.\n* When all the payments are done it will be in \'Posted\' state.'),
        'company_id': fields.related('journal_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'journal_id':fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        #'balance':fields.function(_sum_balance, method=True, string="Balance"),
        'balance':fields.float("Balance",readonly=False, states={'draft':[('readonly',True)]}),
        'currency_id':fields.related('journal_id', 'currency', type='many2one', relation='res.currency', string='Currency', store=True, readonly=True, states={'draft':[('readonly',False),('required',True)]}),
        'line_ids':fields.one2many('bank.transaction.line','bank_trans_id','Bank Transaction Lines',readonly=True, states={'draft':[('readonly',False)]}),
        'move_id':fields.many2one('account.move', 'Account Entry',readonly=True, states={'draft':[('readonly',False)]}),
        'move_ids': fields.related('move_id','line_id', type='one2many', relation='account.move.line', string='Journal Items',readonly=True, states={'draft':[('readonly',False)]}),
        'saldo': fields.float("Saldo",readonly=False, states={'draft':[('readonly',True)]}),
    }
    
    _defaults = {
        'name' : '/',
        'source_rate':_get_rate_base,
        'currency_id':_get_currency_base,
        'state':'draft',
    }
    
    def cancel_approval(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=None)
        return True
    
    def confirm_treasury(self, cr, uid, ids, context=None):
        self.hitung_total(cr, uid, ids, context)
        self.write(cr, uid, ids, {'state':'app_lv1'}, context=None)
        return True
    
    def confirm_cfo(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'app_lv2'}, context=None)
        return True
    
    def onchange_src_rate(self, cr, uid, ids, currency_id,context=None):
        
        currency_search = self.pool.get('res.currency').search(cr, uid, [('id','=',currency_id)])
        currency_browse = self.pool.get('res.currency').browse(cr, uid, currency_search)
        rate = 1
        for cur_id in currency_browse:
            print "Name ===================>>", cur_id.name
            id_currency = cur_id.id
            rate = cur_id.rate
        current_rate = 1 / rate
        
        return {'value':{'source_rate':current_rate}}
    
    def onchange_balance(self, cr, uid, ids, journal_id, context=None):
        print ids,"context",context
        journal_id = self.pool.get('account.journal').browse(cr, uid, journal_id, context=None)
        account_debit_id = journal_id.default_debit_account_id.id
        print 'account_debit_id',account_debit_id
        cr.execute("select (sum(debit)-sum(credit)) from account_move_line where account_id=%s", (account_debit_id,))
        balance = cr.fetchone()[0]
        print "Balance ::", ids,balance
        
        #self.write(cr, uid, ids, {'balance':balance})
        print "xxx"
        #return {'value':{'balance':balance}}
        return self.pool.get('bank.transaction').write(cr, uid, ids, {'balance':balance}, context=None)
    
    
    def hitung_total(self,cr, uid, ids, context=None):
        bt=self.browse(cr,uid,ids)[0]
        amount_total = 0.0
        
        for x in bt.line_ids:
        
            journal_id = bt.journal_id.name
            
            print "journal_id ::", journal_id
            
            account_debit_id = bt.journal_id.default_debit_account_id.id
            print 'account_debit_id',account_debit_id
            cr.execute("select (sum(debit)-sum(credit)) from account_move_line where account_id=%s", (account_debit_id,))
            balance = cr.fetchone()[0]
            print "balance ::", balance
            self.pool.get('bank.transaction').write(cr, uid, ids, {'balance':balance}, context=None)
            
        
            
        
        
            #print 'line',x.amount_src
            amount_total += x.amount_src
        print "amount_total :", amount_total
        
         
        self.pool.get('bank.transaction').write(cr, uid, ids, {'amount':amount_total}, context=None)
        return True
        #return True
    
    def confirm_bank_trans(self, cr, uid, ids, context=None):
        print "confirm ids",ids
        if not context:
            context={}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        seq_obj = self.pool.get('ir.sequence')
        
        for bts in self.browse(cr,uid,ids,context=context):
            print "Balance :=============>>", bts.balance
            company_currency=bts.company_id.currency_id.id
            current_currency=bts.journal_id.currency.id
            
            ##################Update Seq Number#####################
            if bts.name <> '/':
                name_seq = bts.name
            elif bts.journal_id.sequence_id:
                name_seq = seq_obj.get_id(cr, uid, bts.journal_id.sequence_id.id)
            else:
                raise osv.except_osv(_('Error !'), _('Please define a sequence on the journal !'))
            #########################################################
            
            move = {
                'name': name_seq,
                'journal_id': bts.journal_id.id,
                'narration': bts.ref,
                'date': bts.date,
                'ref': bts.ref,
                'period_id': bts.period_id and bts.period_id.id or False,
                }
            move_id = move_pool.create(cr, uid, move)
            #print "move_id",move_id
            amt=bts.amount
            if company_currency <> current_currency:
                amt=bts.amount*bts.source_rate
                
            move_line1 = {
                'name': bts.ref or bts.line_ids[0].reference or bts.name or '/',
                'debit': 0,
                'credit': amt,
                'account_id': bts.journal_id.default_credit_account_id.id,
                'move_id': move_id,
                'journal_id': bts.journal_id.id,
                'period_id': bts.period_id.id,
                'partner_id': bts.partner_id.id,
                'currency_id': company_currency <> current_currency and current_currency or False,
                'amount_currency': company_currency <> current_currency and -bts.amount or 0.0,
                'date': bts.date,
            }
            #print "1",move_line1
            move_line_pool.create(cr, uid, move_line1)
            tot = 0
            for line in bts.line_ids:
                move_line2 = {
                    'name': line.reference or '/',
                    'debit': line.amount_rate,
                    'credit': 0,
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'journal_id': line.journal_id.id,
                    'period_id': bts.period_id.id,
                    'partner_id': bts.partner_id.id or False,
                    'currency_id': company_currency <> current_currency and  current_currency or False,
                    'amount_currency': company_currency <> current_currency and bts.amount or 0.0,
                    'date': bts.date,
                    }
                #print "2",move_line2
                tot += line.amount_rate
                move_line_pool.create(cr, uid, move_line2)
                print "bts.journal_id.id =============>>", bts.journal_id.name
                ########################diubah unttuk GBU###################
                #if line.expense_account_credit and line.expense_account_debit and line.expense_amount:
                #############################################################    
                if line.expense == True and line.expense_account_debit and line.expense_amount:
                    print "Masukkkk"
                    move_line3 = {
                    'name': line.reference or '/',
                    'debit': line.expense_amount,
                    'credit': 0,
                    'account_id': line.expense_account_debit.id,
                    'move_id': move_id,
                    ####################Di Ubah UNtuk GBU##
                    'journal_id': bts.journal_id.id,
                    #######################################
                    #'journal_id': line.expense_journal_id.id,
                    'period_id': bts.period_id.id,
                    'partner_id': bts.partner_id.id or False,
                    #'currency_id': company_currency <> current_currency and  current_currency or False,
                    #'amount_currency': company_currency <> current_currency and bts.amount or 0.0,
                    'date': bts.date,
                    }
                    #print "move_line3",move_line3
                    #print "3",move_line3
                    move_line_pool.create(cr, uid, move_line3)
                    move_line4 = {
                        'name': line.reference or '/',
                        'debit': 0,
                        'credit': line.expense_amount,
                        ####################Di Ubah UNtuk GBU###################
                        #'account_id': line.expense_account_credit.id,
                        'account_id': bts.journal_id.default_credit_account_id.id,
                        #######################################
                        'move_id': move_id,
                        ####################Di Ubah UNtuk GBU###################
                        'journal_id': bts.journal_id.id,
                        #######################################
                        #'journal_id': line.expense_journal_id.id,
                        'period_id': bts.period_id.id,
                        'partner_id': bts.partner_id.id or False,
                        #'currency_id': company_currency <> current_currency and  current_currency or False,
                        #'amount_currency': company_currency <> current_currency and bts.amount or 0.0,
                        'date': bts.date,
                        }
                    #print "4",move_line4
                    move_line_pool.create(cr, uid, move_line4)
            #print move_line1['credit'],tot
            if move_line1['credit']-tot != 0:
                raise osv.except_osv(_('Unbalance !'), _('You cannot create journal, there is still remain %s on you account' % (str(move_line1['credit']-tot))))
            ###Remove AUto Post###
            #move_pool.write(cr,uid,[move_id],{'state':'posted'})
            
            ##############Create Saldo##################
            account_debit_id = bts.journal_id.default_debit_account_id.id
            print 'account_debit_id',account_debit_id
            cr.execute("select (sum(debit)-sum(credit)) from account_move_line where account_id=%s", (account_debit_id,))
            saldo = cr.fetchone()[0]
            print "Saldo ::", saldo
            self.pool.get('bank.transaction').write(cr, uid, ids, {'saldo':saldo, 'name':name_seq}, context=None)
            ############################################
            
        return self.write(cr, uid, ids, {'state':'posted','move_id':move_id}, context=context)
    
    def cancel_bank_trans(self, cr, uid, ids, context=None):
        #print "cancel ids",ids
        move_pool = self.pool.get('account.move')
        id=self.browse(cr,uid,ids,context=context)[0]
        move_id=id.move_id.id
        #print "move_id",move_id
        move_pool.write(cr,uid,[move_id],{'state':'draft'})
        move_pool.unlink(cr,uid,[move_id])
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)
    
bank_transaction()

class bank_transaction_line(osv.osv):
    _name = "bank.transaction.line"
    _description = "Bank Transaction Line"
    
    
    def get_amount_rate(self, cr, uid, ids, force_rate, amount_src, context=None):
        if context is None: context = {}
        amt=0.00
        if force_rate and amount_src:
            amt = force_rate * amount_src
        #print "amt",amt
        return {'value': {'amount_rate' : amt, 'balance': amount_src}}
    
    def get_account(self, cr, uid, ids, journal_id, context=None):
        account = False
        currency = False
        if journal_id:
            journal=self.pool.get('account.journal').browse(cr,uid,journal_id,context=context)
            account=journal.default_debit_account_id.id
            currency=journal.currency.id
        return {'value': {'account_id' : account,'currency_id':currency }}
        
    _columns = {
        'bank_trans_id':fields.many2one('bank.transaction','Bank Transaction',readonly=True,store=True),
        'reference':fields.char('Name',128),
        'journal_id':fields.many2one('account.journal',"Journal Destination"),
        'account_id': fields.related('journal_id', 'default_debit_account_id', type='many2one', relation='account.account', string='Account', store=True),
        'currency_id': fields.related('journal_id', 'currency', type='many2one', relation='res.currency', string='Currency', store=True),
        'force_rate':fields.float('Bank Rate', help="If you are transferring from USD to IDR (1 USD= 9000 IDR), fill the rate with 9000, vice versa"),
        'balance':fields.float('Balance',digit=(16,2)),
        'amount_src':fields.float('Amount Source',digit=(16,2)),
        'amount_rate':fields.float("Converted Amount",digit=(16,2)),
        'expense': fields.boolean('With Expense?', help="Check this if transaction with expense"),
        'expense_journal_id':fields.many2one('account.journal','Expense Journal'),
        'expense_account_credit':fields.many2one('account.account','Expense on Credit'),
        'expense_account_debit':fields.many2one('account.account','Expense on Debit'),
        'expense_amount':fields.float('Expense Amount',digit=(16,2)),
    }
    
    _defaults = {
    }
    
    def onchange_force_rate(self, cr, uid, ids, currency_id,context=None):
        
        currency_search = self.pool.get('res.currency').search(cr, uid, [('id','=',currency_id)])
        currency_browse = self.pool.get('res.currency').browse(cr, uid, currency_search)
        rate = 1
        for cur_id in currency_browse:
            print "Name ===================>>", cur_id.name
            id_currency = cur_id.id
            rate = cur_id.rate
        current_rate = 1 / rate
        
        return {'value':{'force_rate':current_rate}}
    
    def on_change_expense(self, cr, uid, ids, journal_id, context=None):
        account_credit = False
        account_debit = False
        if journal_id:
            journal=self.pool.get('account.journal').browse(cr,uid,journal_id,context=context)
            account_debit  = journal.default_debit_account_id.id
            account_credit = journal.default_credit_account_id.id
        return {'value': {'expense_account_credit' : account_credit, 'expense_account_debit': account_debit}}
    
bank_transaction_line()

class account_journal(osv.osv):
    _inherit = "account.journal"
    _description = "Journal"
    _columns = {
        'payment': fields.boolean('Payment'),
        'receipt': fields.boolean('Receipt'),
    }

account_journal()