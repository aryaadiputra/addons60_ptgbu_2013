import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _

class account_invoice(osv.osv):
    
    _inherit = 'account.invoice'
    
    _columns = {}
    
    
    
account_invoice()