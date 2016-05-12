from osv import fields,osv
import time
import datetime


class res_date(osv.osv):
    _name = "res.date"
    _description = "Res Date"
    _columns = {
        'name': fields.char('Date', size=64),
        'period_id': fields.many2one('account.period', 'Period'),
        'date': fields.date('Date of Period'),
        'day': fields.char('Day', size=32),
    }
    _defaults = {
        #'state': 'draft',
    }
    _order = "date"
    
res_date()

class hr_attendance_report(osv.osv_memory):
    _name="hr.attendance.report.wizard"
    _columns={
        'rep_type':fields.selection([('daily','Daily'),('monthly','Monthly')],"Report Type"),
        'employee_ids':fields.many2many("hr.employee","attendance_employee_rel","attendance_id","employee_id","Employee",required=True),
        "date_print":fields.date("Attendance Date",required=False),
        "month_print":fields.many2one('account.period',"Period",required=False),
              }
    _defaults={
        'date_print': lambda *a:time.strftime("%Y-%m-%d"),
        'rep_type':lambda *b:'daily',
               }
    
    def report_hr_attendance(self, cr, uid, ids, context):
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'hr.attendance.report.wizard'
        datas['form'] = self.read(cr, uid, ids)[0]
        if datas['form']['rep_type']=='daily':
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.attendance',
                    'report_type': 'webkit',
                    'datas': datas,
                    }
        else:
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.attendance.monthly',
                    'report_type': 'webkit',
                    'datas': datas,
                    }
        
hr_attendance_report()
