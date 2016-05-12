import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _

class make_to_asset_info_line(osv.osv):
    
    ''' inherited account.invoice.line '''
    
    _inherit = "account.invoice.line"
    
    _columns = {
        'asset_check': fields.boolean('Asset'),
        'set_to_asset': fields.char('Make to Asset?', size=64,),
        
                }
        
make_to_asset_info_line()