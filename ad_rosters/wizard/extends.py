import time

from osv import fields, osv
import netsvc
import pooler
from osv.orm import browse_record, browse_null
from tools.translate import _

class hr_travel_order_group(osv.osv_memory):
    _name = "wizard.extends"
    _description = "Wizard Extends"

    def insert_extends(self, cr, uid, ids, context=None):
        data_ext = self.browse(cr, uid, ids[0], context=context)
        data_extends = {
                    'start_work_date_extends' : data_ext.start_work_date_extends,
                    'end_work_date_extends' : data_ext.end_work_date_extends,
                    'start_holiday_date_extends' : data_ext.start_holiday_date_extends,
                    'end_holiday_date_extends': data_ext.end_holiday_date_extends,
                    'status_extends' : 'draft',
                     }
        id_rosters_schedule = context['record_id']
        self.pool.get('rosters.schedule.line').write(cr,uid,id_rosters_schedule,data_extends);
        return {'type': 'ir.actions.act_window_close'}
        
    _columns = {
                'start_work_date_extends':fields.date("Start Working Date Extends", required=False),
                'end_work_date_extends':fields.date("End Working Date Extends", required=False),
                'start_holiday_date_extends':fields.date("Start Holidays Date Extends", required=False),
                'end_holiday_date_extends':fields.date("End Holidays Date Extends", required=False),
                'status_extends': fields.selection([('draft','Draft'),('waiting','Waiting'),('confirm','Confirm')], 'States Depart'),
                }

hr_travel_order_group()