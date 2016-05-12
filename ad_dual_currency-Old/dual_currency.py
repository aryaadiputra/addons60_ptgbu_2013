import time
from datetime import datetime
from operator import itemgetter

import netsvc
from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import tools

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    _description = "Journal Items"
    
    _columns = {
            'rate_dual': fields.float('Rate USD', digits_compute=dp.get_precision('Account')),
            'debit_dual': fields.float('Debit USD', digits_compute=dp.get_precision('Account')),
            'credit_dual': fields.float('Credit USD', digits_compute=dp.get_precision('Account')),
            'gain_loss' : fields.boolean('Gain Loss'),
                }
account_move_line()

class account_move(osv.osv):
    _inherit = 'account.move'
    
    _columns = {
            'manual_rate' : fields.boolean('Manual Rate')
                }
    
    def post(self, cr, uid, ids, context=None):
        print "PosttttttXXX"
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)

        if not valid_moves:
            raise osv.except_osv(_('Integrity Error !'), _('You cannot validate a non-balanced entry !\nMake sure you have configured Payment Term properly !\nIt should contain atleast one Payment Term Line with type "Balance" !'))
        obj_sequence = self.pool.get('ir.sequence')
        for move in self.browse(cr, uid, valid_moves, context=context):
            
            #################################
            move_id = move.id
            currency_dual   = self.pool.get('res.currency.rate.dual')
            move_line_obj   = self.pool.get('account.move.line')
            currency_obj    = self.pool.get('res.currency.dual')
            rate            = 0
            
            if move.manual_rate == True:
                cr.execute('delete from account_move_line where move_id = %s and (debit = 0.0 or debit is null) and (credit = 0.0 or credit is null) and gain_loss = True',(move.id,))
                for line in move.line_id:
                    rate        = line.rate_dual
                    debit_dual  = 0.0
                    credit_dual = 0.0
                    
                    if line.debit <> 0.0:
                        debit_dual = line.debit / line.rate_dual
                    if line.credit <> 0.0:
                        credit_dual = line.credit / line.rate_dual
                        
                    move_line_obj.write(cr, uid, [line.id], {'rate_dual' :  rate, 
                                                         'debit_dual'  : debit_dual,
                                                         'credit_dual' : credit_dual,
                                                         }, context)
            
                ###Create Gain/Loss###
                cr.execute("select sum(debit_dual)-sum(credit_dual) as balance from account_move_line where move_id = %s", (move_id, ))
                balance_gain_loss = cr.fetchone()[0]
                print "Balance Gain Loss--------->>",balance_gain_loss
                debit_forex     = 0.0
                credit_forex    = 0.0
                
                if balance_gain_loss <> 0.0:
                    if balance_gain_loss < 0.0:
                        print "Masuuuuuuuuuuuuukkk"
                        debit_forex = abs(balance_gain_loss)
                    else:
                        credit_forex = abs(balance_gain_loss)
                        
                    move_line = {
                        'name': "Gain/ Loss "+ move.name or '/',
                        'debit_dual': debit_forex,
                        'credit_dual': credit_forex,
                        'account_id': move.company_id.gl_account_id.id,
                        'move_id': move.id,
                        'journal_id': move.journal_id.id,
                        'period_id': move.period_id.id,
                        'partner_id': move.partner_id.id,
                        'currency_id': False,
                        #'amount_currency': company_currency <> current_currency and -bts.amount or 0.0,
                        'date': move.date,
                        'gain_loss' : True,
                            }
                    print "MOve :::", move.id
                    move_line_obj.create(cr, uid, move_line)
            
            #################################
            
            else:
                cr.execute('select c.currency_dual from account_move_line l, res_currency c where l.move_id = %s and l.currency_id is not null and l.currency_id = c.id',(move.id,))
                from_currency_dual = cr.fetchone()
                
                if from_currency_dual:
                    from_currency_dual = from_currency_dual[0]
                    from_currency_dual = 1
                else:
                    from_currency_dual = move.company_id.currency_id.currency_dual.id
                    
                cr.execute('select id from res_currency_dual where base = True')
                to_currency_dual = cr.fetchone()[0]
                
                print "From :", from_currency_dual, "To :", to_currency_dual
    
                cr.execute('delete from account_move_line where move_id = %s and (debit = 0.0 or debit is null) and (credit = 0.0 or credit is null) and gain_loss = True',(move.id,))
                ##########################
                currency_name = False
                cr.execute('select c.name from account_move_line l, res_currency c where move_id = %s and l.currency_id is not null and l.currency_id = c.id',(move.id,))
                currency_name = cr.fetchone()
                if currency_name:
                    currency_name = currency_name[0]
                
                
                cr.execute('select name from res_currency_dual where base = True')
                currency_dual_name = cr.fetchone()[0]
                
                if currency_name == currency_dual_name:
                    for line in move.line_id:
                        debit_dual  = 0.0
                        credit_dual = 0.0
                        
                        if line.amount_currency > 0.0:
                            debit_dual = line.amount_currency
                        else:
                            credit_dual = abs(line.amount_currency)
                            
                        
                        
                        move_line_obj.write(cr, uid, [line.id], {'rate_dual'   : 0, 
                                                         'debit_dual'  : debit_dual,
                                                         'credit_dual' : credit_dual,
                                                         }, context)
                
                else:
                    for line in move.line_id:
                        
                        debit_dual  = 0.0
                        credit_dual = 0.0
                        reconcile_partial_id = line.reconcile_partial_id.id
                        reconcile_id = line.reconcile_id.id
                        rate_date = move.date
                        
                        if line.reconcile_partial_id:
                            cr.execute("select min(date) from account_move_line where reconcile_partial_id = %s", (reconcile_partial_id, ))
                            rate_date = cr.fetchone()[0]
                            
                            ###Cek Period Accrual###
                            ###Currenct Date Transaction###
                            #cr.execute("select id from account_period where date_start <= %s and date_stop >= %s" ,(move.date, move.date))
                            #current_period_id = cr.fetchone()[0]
                            
                            ###Min Date Transaction###
                            #cr.execute("select id from account_period where date_start <= %s and date_stop >= %s" ,(rate_date, rate_date))
                            #current_period_id = cr.fetchone()[0]
                            
                            cr.execute("select name from res_currency_rate_dual where closing_rate = True and name <= %s and name >= %s", (move.date, rate_date))
                            closing_rate_date = cr.fetchone()[0]
                            if closing_rate_date:
                                rate_date = closing_rate_date
                            ###############
                            
                        
                        elif line.reconcile_id:
                            cr.execute("select min(date) from account_move_line where reconcile_id = %s", (reconcile_id, ))
                            rate_date = cr.fetchone()[0]
                            
#                            cr.execute("select name from res_currency_rate_dual where closing_rate = True and name <= %s and name >= %s", (move.date, rate_date))
#                            closing_rate_date = cr.fetchone()[0]
#                            if closing_rate_date:
#                                rate_date = closing_rate_date
                            
                        print "Debit :", line.debit, "Credit :",line.credit, "Rate Date ::", rate_date
                        if line.debit <> 0.0:
                            print "QQQQQQQQ"
                            #debit_dual = line.debit/ rate
                            debit_dual = currency_obj.compute(cr, uid, from_currency_dual, to_currency_dual, line.debit, context={'date': rate_date})
                            print "debit_dual>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", debit_dual, from_currency_dual, to_currency_dual
                            
                        if line.credit <> 0.0:
                            #credit_dual = line.credit / rate
                            credit_dual = currency_obj.compute(cr, uid, from_currency_dual, to_currency_dual, line.credit, context={'date': rate_date})
                        
                        rate = currency_obj.get_rate(cr, uid, from_currency_dual, to_currency_dual,context={'date' : rate_date})
                        
                        print "ID ::", line.id, "RATE ::", rate
                        
                        if line.account_id.id <> move.company_id.gl_account_id.id:
                            move_line_obj.write(cr, uid, [line.id], {'rate_dual'    : rate, 
                                                             'debit_dual'       : debit_dual,
                                                             'credit_dual'      : credit_dual,
                                                             }, context)
                    
                    
                ###Create Gain/Loss###
                cr.execute("select sum(debit_dual)-sum(credit_dual) as balance from account_move_line where move_id = %s", (move_id, ))
                balance_gain_loss = cr.fetchone()[0]
                print "Balance Gain Loss--------->>",balance_gain_loss
                debit_forex     = 0.0
                credit_forex    = 0.0
                
                if balance_gain_loss <> 0.0:
                    if balance_gain_loss < 0.0:
                        print "Masuuuuuuuuuuuuukkk"
                        debit_forex = abs(balance_gain_loss)
                    else:
                        credit_forex = abs(balance_gain_loss)
                        
                    move_line = {
                        'name': "Gain/ Loss "+ move.name or '/',
                        'debit_dual': debit_forex,
                        'credit_dual': credit_forex,
                        'account_id': move.company_id.gl_account_id.id,
                        'move_id': move.id,
                        'journal_id': move.journal_id.id,
                        'period_id': move.period_id.id,
                        'partner_id': move.partner_id.id,
                        'currency_id': False,
                        #'amount_currency': company_currency <> current_currency and -bts.amount or 0.0,
                        'date': move.date,
                        'gain_loss' : True,
                            }
                    print "MOve :::", move.id
                    move_line_obj.create(cr, uid, move_line)
                
            
            
            
            #################################
            
            if move.name =='/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.internal_number:
                    new_name = invoice.internal_number
                else:
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
                        new_name = obj_sequence.get_id(cr, uid, journal.sequence_id.id, context=c)
                    else:
                        raise osv.except_osv(_('Error'), _('No sequence defined on the journal !'))

                if new_name:
                    self.write(cr, uid, [move.id], {'name':new_name})
        
        ###Cek Balance####
        cr.execute("select sum(debit_dual)-sum(credit_dual) as balance from account_move_line where move_id = %s", (move_id, ))
        balance = cr.fetchone()[0]
        print "Balance --------->>",balance 
        if balance <> 0.0:
            raise osv.except_osv(_('Error !'), _('Not Balance'))
        #################
        
        cr.execute('UPDATE account_move '\
                   'SET state=%s '\
                   'WHERE id IN %s',
                   ('posted', tuple(valid_moves),))

        return True
    
    
account_move()