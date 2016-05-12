from operator import itemgetter

from osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
            'account_balance_id':fields.many2one('account.account','Account Settlement Balance', required=False,),
                }

res_partner()