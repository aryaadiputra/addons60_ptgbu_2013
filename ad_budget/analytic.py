import time

from osv import fields, osv
import decimal_precision as dp

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'
    
    _columns = {
           'division_id': fields.related('department_id', 'division_id', relation='hr.division',type='many2one', string='Division',store=True, readonly=True),
                }
account_analytic_account()