import time
from lxml import etree

import netsvc
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _


class advance_type(osv.osv):
    
    _name = 'advance.type'
    
    _columns = {
            'name'          : fields.char('Name', size=256, required=True, ),
            'account_id'    : fields.many2one('account.account', 'Account' ),
            'type'          : fields.selection([
                                ('general','General'),
                                ('travel','Travel'),
                                ],'Type', select=True),
                                    }
advance_type()