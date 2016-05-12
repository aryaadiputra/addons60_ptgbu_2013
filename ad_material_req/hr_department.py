#from osv import fields, osv
#
#import addons

import time
import netsvc
import pooler
import datetime
from dateutil.relativedelta import relativedelta
import base64, urllib
from osv import osv, fields
import decimal_precision as dp
from tools.translate import _

class hr_department(osv.osv):
    _description = "Department"
    _inherit = 'hr.department'
    _columns = {
        'dept_general': fields.boolean('Budget General'),
    }
    
    def onchange_dept_general(self, cr, uid, ids, dept_general, division_id, context=None):
        print "sssss"
        print "--------------",dept_general, division_id
        
        check_dept = self.search(cr, uid, [('dept_general','=',True),('division_id','=',division_id)])
        print "check_dept", check_dept
        if dept_general == True:
            if check_dept:
                print "wwwwwwwwwww"
                value = {'dept_general':''}
                warning = {
                            "title": ("Account Expense Product No Define"),
                            "message": ("xxxxxxxxxxxxxxxxxx")
                        }
                return {'warning': warning ,'value': value}
        
hr_department()