import time
from osv import fields, osv

class purchase_requisition_res(osv.osv):
    
    _inherit = "purchase.requisition"
    

    _columns = {
             'delegate': fields.many2one('hr.employee', 'Delegate to', required=False),
             #'contact_supplier': fields.char('Contact Supplier', size=64,),
                }
    
purchase_requisition_res()