from osv import fields,osv
from osv.orm import browse_record
import tools
from functools import partial
import pytz
import pooler
from tools.translate import _
from service import security
import netsvc

class res_users(osv.osv):
    _inherit = 'res.users'
    _description = 'User'

    _columns = {
        'context_division_id': fields.many2one('hr.division', 'Divisions'),
    }

res_users()