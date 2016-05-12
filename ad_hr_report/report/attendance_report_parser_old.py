from report import report_sxw
from osv import osv
import pooler
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tools.translate import _

class report_attendance_parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_attendance_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_employee':self._get_employee,
            'get_work_time':self._get_work_time,
        })
    
    def _get_employee(self,employee_ids):
        if employee_ids:
            return self.pool.get('hr.employee').browse(self.cr,self.uid,employee_ids)
        else: 
            return False
        
    def _get_work_time(self,employee_id,date_print):
        sign_in='%s 00:00:00'%date_print
        sign_out='%s 23:59:59'%date_print
        
        if employee_id:
            employee=[]
            attendance_ids=self.pool.get('hr.attendance').search(self.cr,self.uid,[('employee_id','=',employee_id),('name','>=',sign_in),('name','<=',sign_out)],order="employee_id,name ASC")
            #print 'attendance_ids==================',attendance_ids
            attendance_datas=self.pool.get('hr.attendance').browse(self.cr,self.uid,attendance_ids)
            dummy={
                   'sign_in': False,
                   'sign_out':False,
                   }
            for y in attendance_datas:
                dummy={
                       'sign_in':dummy['sign_in']==False and y.action == 'sign_in' and y.name,
                       'sign_out':dummy['sign_out']==False and y.action == 'sign_out' and y.name,
                       }
                #print "===========>",dummy
                if dummy['sign_in'] and dummy['sign_out']:
                    employee.append(dummy)
                    dummy={
                           'sign_in': False,
                           'sign_out':False,
                           }
            return employee
        else:
            return False
    
    
    
report_sxw.report_sxw('report.report.hr.attendance', 'hr.attendance.report.wizard', 'addons/ad_hr_report/report/attendance_report.mako', parser = report_attendance_parser, header = True)
