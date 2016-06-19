import time

from osv import fields, osv
import netsvc
import pooler
from osv.orm import browse_record, browse_null
from tools.translate import _

class cash_advance_report(osv.osv_memory):
    _name = "cash.advance.report"
    _description = "Cash Advance Report"

    def merge_orders(self, cr, uid, ids, context=None):
        
        wizard = self.browse(cr, uid, ids[0], context)       
        order_obj = self.pool.get('cash.advance')
        mod_obj =self.pool.get('ir.model.data')

        if context is None:
            context = {}
        x = {}
        active_ids = context.get('active_ids',[])
        print "aaaaaaaaaa"
        print "'active_ids',[].>>>>>>>>>>>>>>>>>>>>>>>>>", context.get('active_ids',[])
        # allorders = order_obj.do_merge(cr, uid, context.get('active_ids',[]), context)
        # allorders = order_obj.action_merge(cr, uid, context.get('active_ids',[]), date_invoice, partner_id, address_invoice_id, context)
        x['ids'] = ids
        x['model'] = 'cash.advance'
        x['id_cash'] = active_ids
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'print.cash.advance',
            'report_type': 'webkit',
            'datas': x,
                }

    _columns = {}

cash_advance_report()

class cash_advance_report_notification(osv.osv_memory):
    _name = "cash.advance.report.notification"
    _description = "Cash Advance Report Notification"
    _columns = {
       
                }
cash_advance_report_notification()