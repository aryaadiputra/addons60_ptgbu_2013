from osv import osv, fields
import wizard
import pooler
from tools.translate import _
import ir
import time
class partner_template(osv.osv):
    _name = "partner.template"
    _columns = {
                'name' : fields.char('Name',size=128),
                'desc' : fields.text('Description'),
                }
partner_template()