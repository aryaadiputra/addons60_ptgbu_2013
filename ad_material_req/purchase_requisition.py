import time
import netsvc

from osv import fields,osv

class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"
    
    _columns = {
            'int_move_id'       : fields.many2one('stock.picking', 'Internal Move Number', readonly=True),
            'mr_description'    : fields.char('Description', size=64),
            #'material_req_id'   : fields.many2one('material.requisition', 'Material Requisition'),
            'material_req_id': fields.related('int_move_id', 'material_req_id', relation='material.requisition',type='many2one', string='MR',store=True, readonly=True),
                }
    
purchase_requisition()

class purchase_requisition_line(osv.osv):
    _inherit = "purchase.requisition.line"
    
    _columns = {
            'detail'    : fields.text('Detail'),
                }
    
purchase_requisition_line()