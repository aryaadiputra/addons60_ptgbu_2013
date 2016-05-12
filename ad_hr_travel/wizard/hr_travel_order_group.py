import time

from osv import fields, osv
import netsvc
import pooler
from osv.orm import browse_record, browse_null
from tools.translate import _

class hr_travel_order_group(osv.osv_memory):
    _name = "hr.travel.order.group"
    _description = "Hr Travel Order Merge"

    def merge_orders(self, cr, uid, ids, context=None):
        
        wizard = self.browse(cr, uid, ids[0], context)
#         print "dateeeeeeeeeeeeeeeee_invoiceeeeeeeeeee", wizard.date_invoice
        
        order_obj = self.pool.get('hr.travel')
#         print "bbbbbbbbbbbbbbbbbbbbbbbb", order_obj
#         proc_obj = self.pool.get('procurement.order')
#         print "aaaaaaaaaaaaaaaaaaaaaaaa",proc_obj
        mod_obj =self.pool.get('ir.model.data')
#         print "ccccccccccccccccccccccccc", mod_obj
        if context is None:
            context = {}
        
#         context = {
#                    'date_invoice' : wizard.date_invoice,
#                    }

        date_invoice =  wizard.date_invoice
        partner_id = wizard.partner_id.id

        partner = self.pool.get('res.partner.address').search(cr, uid, [('partner_id','=',partner_id)], context=context)
        # print "partneeeeeeeeeeeeeer", partner
        # print "partneeeeeeeeeeeeeer", partner.id
        data = self.pool.get('res.partner.address').browse(cr, uid, partner)
        address_invoice_id = ""
        for a in data:
            address_invoice_id = a.id
        
        result = mod_obj._get_id(cr, uid, 'purchase', 'view_purchase_order_filter')
#         print "dddddddddddddddddddddddd", result
        id = mod_obj.read(cr, uid, result, ['res_id'])
        print "eeeeeeeeeeeeeeeeeeeeeeee", id
        print "'active_ids',[].>>>>>>>>>>>>>>>>>>>>>>>>>", context.get('active_ids',[])
        #allorders = order_obj.do_merge(cr, uid, context.get('active_ids',[]), context)
        allorders = order_obj.action_merge(cr, uid, context.get('active_ids',[]), date_invoice, partner_id, address_invoice_id, context)
        
        return {
            'name'      : 'Hr Travel Notification',
            'view_type' : 'form',
            'view_mode' : 'form',
            'res_model' : 'hr.travel.notification',
            'type'      : 'ir.actions.act_window',
            'target'    : 'new',
            'context'   : context
            }
#         }

    _columns = {
                'date_invoice' : fields.date('Date Invoice'),
                'partner_id': fields.many2one('res.partner', 'Travel Agent'),
                # 'address_invoice_id': fields.many2one('res.partner.address', 'Travel Address'),
                }

hr_travel_order_group()

class hr_travel_notification(osv.osv_memory):
    _name = "hr.travel.notification"
    _description = "Hr Travel Notification"
    _columns = {
       
                }
hr_travel_notification()