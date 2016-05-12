
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64, urllib
from osv import osv, fields
import decimal_precision as dp

class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'
    _description = 'Asset'
    
    _columns = {
            'asset_rate': fields.float('Rate for Asset Depreciation'),
                }
    
account_asset_asset()

class account_asset_depreciation_line(osv.osv):
    _inherit = 'account.asset.depreciation.line'
    _description = 'Asset depreciation line'

    _columns = {}
    
    def create_move(self, cr, uid, ids, context=None):
        print "ASSET DUAL CURRENCY"
        can_close = False
        if context is None:
            context = {}
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        created_move_ids = []
        for line in self.browse(cr, uid, ids, context=context):
            if currency_obj.is_zero(cr, uid, line.asset_id.currency_id, line.remaining_value):
                can_close = True
                asset_obj.write(cr, uid, [line.asset_id.id], {'state': 'close'}, context=context)
            #depreciation_date = line.asset_id.prorata and line.asset_id.purchase_date or time.strftime('%Y-%m-%d')
            #depreciation_date = line.asset_id.prorata and line.depreciation_date or time.strftime('%Y-%m-%d')
            depreciation_date = line.asset_id.prorata and line.asset_id.purchase_date or line.depreciation_date
            
            period_ids = period_obj.find(cr, uid, depreciation_date, context=context)
            company_currency = line.asset_id.company_id.currency_id.id
            current_currency = line.asset_id.currency_id.id
            context.update({'date': depreciation_date})
            amount = currency_obj.compute(cr, uid, current_currency, company_currency, line.amount, context=context)
            sign = line.asset_id.category_id.journal_id.type = 'purchase' and 1 or - 1
            #asset_name = line.asset_id.name
            
            #################Asset Journal Number#####################
            seq_obj = self.pool.get('ir.sequence')
            reference_code = line.asset_id.code
            asset_seq_name = reference_code + "/" + seq_obj.get_id(cr, uid, line.asset_id.category_id.journal_id.sequence_id.id)
            asset_name = line.asset_id.name
            ##########################################################
            
            reference = line.name
            move_vals = {
                'name': asset_seq_name,
                'date': depreciation_date,
                'ref': reference,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': line.asset_id.category_id.journal_id.id,
                ###Asset Rate###
                'manual_rate' : True,
                ################
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            journal_id = line.asset_id.category_id.journal_id.id
            partner_id = line.asset_id.partner_id.id
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_depreciation_id.id,
                'debit': 0.0,
                'credit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and - sign * line.amount or 0.0,
                'date': depreciation_date,
                ###Asset Rate###
                'rate_dual' : line.asset_id.asset_rate
                ################
            })
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_expense_depreciation_id.id,
                'credit': 0.0,
                'debit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * line.amount or 0.0,
                'analytic_account_id': line.asset_id.category_id.account_analytic_id.id,
                'date': depreciation_date,
                'asset_id': line.asset_id.id,
                ###Asset Rate###
                'rate_dual' : line.asset_id.asset_rate
                ################
            })
            self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
            created_move_ids.append(move_id)
            ######Pindah Ke Atas Bugs Close Asset####
            #if can_close:
                #asset_obj.write(cr, uid, [line.asset_id.id], {'state': 'close'}, context=context)                
        return created_move_ids
    
account_asset_depreciation_line()