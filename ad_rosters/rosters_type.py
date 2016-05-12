import time
import datetime
from dateutil.relativedelta import relativedelta
import base64, urllib
from osv import osv, fields
import decimal_precision as dp

class rosters_schedule_type(osv.osv):
    _name = 'rosters.schedule.type'
    _columns = {
            'name':fields.char('Rosters Schedule Name',size=50,required=True,select=1,help="Rosters Schedule Name."),
            'working_time':fields.integer("Working Times on Weeks",required=True , help="Working Times on Weeks"),
            'leave_time':fields.integer("Leave Times on Weeks",required=True , help="Leave Times on Weeks"),
            
            }
rosters_schedule_type()