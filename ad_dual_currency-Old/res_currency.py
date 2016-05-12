import time
import netsvc
from osv import fields, osv
import ir

from tools.misc import currency
from tools.translate import _

class res_currency(osv.osv):
    _inherit = "res.currency"
    _description = "Currency"
    _columns = {
            'currency_dual':fields.many2one('res.currency.dual', 'Currency Dual'),
                }
    
res_currency()