import time
import datetime
from dateutil.relativedelta import relativedelta
import base64, urllib
from osv import osv, fields
import decimal_precision as dp

class rosters_history(osv.osv):
    _name = 'rosters.history'
    _columns = {
            'start_work_date_history':fields.date("Start Working Date History", required=False),
            'end_work_date_history':fields.date("End Working Date History", required=False),
            'start_holiday_date_history':fields.date("Start Holidays Date History", required=False),
            'end_holiday_date_history':fields.date("End Holidays Date History", required=False),
            'roster_schedule_id': fields.many2one("rosters.schedule.line", "Rosters Schedule"),
            }
rosters_history()