import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter

import netsvc
import pooler
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _

#class account_move(osv.osv):
#    _inherit = 'account.move'
#    _columns = {}
#    
#    def button_validate(self, cursor, user, ids, context=None):
#        for move in self.browse(cursor, user, ids, context=context):
#            top = None
#            for line in move.line_id:
#                #######################
#                #self.pool.get('account.move.line').write(cursor, user, [line.id], {'date' : move.date})
#                #######################
#                account = line.account_id
#                while account:
#                    account2 = account
#                    account = account.parent_id
#                if not top:
#                    top = account2.id
#                elif top<>account2.id:
#                    raise osv.except_osv(_('Error !'), _('You cannot validate a Journal Entry unless all journal items are in same chart of accounts !'))
#        return self.post(cursor, user, ids, context=context)
#    
#account_move()

class account_move(osv.osv):
    _inherit = 'account.move'
    
    def _move_name_search(self, cr, uid, ids, name, arg, context=None):
        if not ids: return {}
        cr.execute( 'select move_id, partner_id '\
                    'FROM account_move_line '\
                    'where move_id IN (28229) and partner_id is not null '\
                    'GROUP BY move_id, partner_id', (tuple(ids),))
    
    def _search_move_name(self, cr, uid, obj, name, args, context):
        ids = set()
        for cond in args:
            number = cond[2]
            if isinstance(cond[2],(list,tuple)):
                if cond[1] in ['in','not in']:
                    number = tuple(cond[2])
                else:
                    continue
#            else:
#                print '2222222222222222222222222222'
#                if cond[1] in ['=like', 'like', 'not like', 'ilike', 'not ilike', 'in', 'not in', 'child_of']:
#                    print "AAAAAAAAAAAAAAAAAA", cond[1]
#                    continue
            if cond[1] == 'ilike':
                number = '%'+number+'%'
                #print "TRUE", (cond[1]),partner
                cr.execute("select id from res_partner where name %s %%s" % (cond[1]),(number,))
                
#                partner_list=tuple([x[0] for x in cr.fetchall()])
#                if len(partner_list)==1:
#                    partner_list=str("(%s)"%partner_list[0])
#                
#                if partner_list:
                cr.execute("""select id from account_move where move_name_manual ilike '%s' or name ilike '%s'  group by id""" % (str(number), str(number)))
            
            else:
                print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                #cr.execute("select id from account_move where name %s %%s group by move_id" % (cond[1]),(partner,))
                #number = str('%'+number+'%')
                print "AAAAAAAAAAA", (cond[1]), "BBBBBBBBBBBBBBBBBBBBBB", (number)
                cr.execute("select id from account_move where move_name_manual = '%s' or name = '%s' group by id" % (str(number), str(number)))
            
            res_ids = set(id[0] for id in cr.fetchall())
            ids = ids and (ids & res_ids) or res_ids
        if ids:
            return [('id','in',tuple(ids))]
        else:
            return [('id', '=', '0')]
    
    
    
    
    
    
    
    
    
    def _partner_search(self, cr, uid, ids, name, arg, context=None):
        if not ids: return {}
        cr.execute( 'select move_id, partner_id '\
                    'FROM account_move_line '\
                    'where move_id IN (28229) and partner_id is not null '\
                    'GROUP BY move_id, partner_id', (tuple(ids),))
    
    def _search_partner(self, cr, uid, obj, name, args, context):
        ids = set()
        for cond in args:
            partner = cond[2]
            if isinstance(cond[2],(list,tuple)):
                if cond[1] in ['in','not in']:
                    partner = tuple(cond[2])
                else:
                    continue
#            else:
#                print '2222222222222222222222222222'
#                if cond[1] in ['=like', 'like', 'not like', 'ilike', 'not ilike', 'in', 'not in', 'child_of']:
#                    print "AAAAAAAAAAAAAAAAAA", cond[1]
#                    continue
            if cond[1] == 'ilike':
                partner = '%'+partner+'%'
                print "TRUE", (cond[1]),partner
                cr.execute("select id from res_partner where name %s %%s" % (cond[1]),(partner,))
                
                partner_list=tuple([x[0] for x in cr.fetchall()])
                if len(partner_list)==1:
                    partner_list=str("(%s)"%partner_list[0])
                
                if partner_list:
                    cr.execute("""select move_id from account_move_line where partner_id in %s group by move_id"""%str(partner_list))
            
            else:
                cr.execute("select move_id from account_move_line where partner_id %s %%s group by move_id" % (cond[1]),(partner,))
            
            res_ids = set(id[0] for id in cr.fetchall())
            ids = ids and (ids & res_ids) or res_ids
        if ids:
            return [('id','in',tuple(ids))]
        else:
            return [('id', '=', '0')]
    
    _columns = {
            'partner_search': fields.function(_partner_search, method=True, string='Partner Search ', type='many2one', relation='res.partner', fnct_search=_search_partner),
            'move_name_search': fields.function(_move_name_search, method=True, string='Move Number Search ', type='char', size=240, fnct_search=_search_move_name),
                }
    
    
    
account_move()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
            'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=False, ),
                }
    
    def compute_all_budget_info(self,cr, uid, ids, context=None):
        search1     = self.pool.get('account.invoice').search(cr, uid, [])
        inv_browse  = self.pool.get('account.invoice').browse(cr, uid, search1)
        no = 1
        for i in inv_browse:
            print no, " +++ " ,i.name, [i.id]
            self.compute_budget_info(cr, uid, [i.id])
            no += 1
        
        
        return True
    
account_invoice()


class account_move_line(osv.osv):
    
    _inherit = "account.move.line"
    _description = "Journal Items"
    
    _columns = {}
    
    _order = 'partner_id asc'
#    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
#        if context is None:
#            context={}
#        move_obj = self.pool.get('account.move')
#        account_obj = self.pool.get('account.account')
#        journal_obj = self.pool.get('account.journal')
#        if vals.get('account_tax_id', False):
#            raise osv.except_osv(_('Unable to change tax !'), _('You can not change the tax, you should remove and recreate lines !'))
#        self._check_date(cr, uid, vals, context, check)
#        if ('account_id' in vals) and not account_obj.read(cr, uid, vals['account_id'], ['active'])['active']:
#            raise osv.except_osv(_('Bad account!'), _('You can not use an inactive account!'))
#        if update_check:
#            if ('account_id' in vals) or ('journal_id' in vals) or ('period_id' in vals) or ('move_id' in vals) or ('debit' in vals) or ('credit' in vals) or ('date' in vals):
#                print "SEMENTARA"
#                self._update_check(cr, uid, ids, context)
#
#        todo_date = None
#        if vals.get('date', False):
#            todo_date = vals['date']
#            del vals['date']
#
#        for line in self.browse(cr, uid, ids, context=context):
#            ctx = context.copy()
#            if ('journal_id' not in ctx):
#                if line.move_id:
#                   ctx['journal_id'] = line.move_id.journal_id.id
#                else:
#                    ctx['journal_id'] = line.journal_id.id
#            if ('period_id' not in ctx):
#                if line.move_id:
#                    ctx['period_id'] = line.move_id.period_id.id
#                else:
#                    ctx['period_id'] = line.period_id.id
#            #Check for centralisation
#            journal = journal_obj.browse(cr, uid, ctx['journal_id'], context=ctx)
#            if journal.centralisation:
#                self._check_moves(cr, uid, context=ctx)
#        result = super(account_move_line, self).write(cr, uid, ids, vals, context)
#        if check:
#            done = []
#            for line in self.browse(cr, uid, ids):
#                if line.move_id.id not in done:
#                    done.append(line.move_id.id)
#                    move_obj.validate(cr, uid, [line.move_id.id], context)
#                    if todo_date:
#                        move_obj.write(cr, uid, [line.move_id.id], {'date': todo_date}, context=context)
#        return result
#    
    
    def _update_check(self, cr, uid, ids, context=None):
        done = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.move_id.state <> 'draft' and (not line.journal_id.entry_posted):
                raise osv.except_osv(_('Error !'), _('You can not do this modification on a confirmed entry ! Please note that you can just change some non important fields !'))
            #if line.reconcile_id:
             #   raise osv.except_osv(_('Error !'), _('You can not do this modification on a reconciled entry ! Please note that you can just change some non important fields !'))
            t = (line.journal_id.id, line.period_id.id)
            if t not in done:
                self._update_journal_check(cr, uid, line.journal_id.id, line.period_id.id, context)
                done[t] = True
        return True
    
    
    def onchange_debit_credit(self, cr, uid, ids, reconcile_id, date_inv=False, context=None):
        print "qqqqqqqqqqqqqqqqqqq"
        print "reconcile_id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", reconcile_id
        if reconcile_id:
            raise osv.except_osv(_('Error !'), _('You can not do this modification on a reconciled entry ! Please note that you can just change some non important fields !'))
        
        
        
account_move_line()