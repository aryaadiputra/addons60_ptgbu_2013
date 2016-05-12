
from osv import osv, fields
import decimal_precision as dp

import math
#from _common import rounding
import re
from tools.translate import _

class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
        'budget_item': fields.many2many('account.analytic.account', 'budget_product_rel', 'product_id', 'budget_item_id', 'Budget Item'),
        
                }
    
product_product()