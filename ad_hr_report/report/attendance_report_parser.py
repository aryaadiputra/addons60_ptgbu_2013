from report import report_sxw
from osv import osv
import pooler
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tools.translate import _
#import timeutils as tu

class report_attendance_parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_attendance_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_employee':self._get_employee,
            'get_work_time':self._get_work_time,
            'get_work_time_monthly':self._get_work_time_monthly,
            'get_period': self._get_period,
        })
    
    def _get_period(self, period):
        bulan = ''
        if period:
            bulan = self.pool.get('account.period').browse(self.cr,self.uid,period).date_start
        return bulan

    def _get_employee(self,employee_ids):
        if employee_ids:
            return self.pool.get('hr.employee').browse(self.cr,self.uid,employee_ids)
        else: 
            return False
        
    def _get_work_time(self, employee_id, date_print):
        sign_in='%s 00:00:00'%date_print
        sign_out='%s 23:59:59'%date_print
        
        if employee_id:
            employee=[]
            #attendance_ids=self.pool.get('hr.attendance').search(self.cr,self.uid,[('employee_id','=',employee_id),('name','>=',sign_in),('name','<=',sign_out)],order="employee_id,name ASC")
            attendance_ids=self.pool.get('hr.attendance').search(self.cr,self.uid,[('employee_id','=',employee_id),('name','>=',sign_in),('name','<=',sign_out)],order="employee_id,name ASC")
            #print 'attendance_ids==================',attendance_ids
            attendance_datas=self.pool.get('hr.attendance').browse(self.cr, self.uid, attendance_ids)
            dummy = []
#            self.cr.execute("""
#                select a.card_id, b.id as employee_id, a.date, min(a.name) as sign_in, max(a.name) as sign_out, max(a.name)-min(a.name) as total
#                from hr_attendance_virtual a, hr_employee b 
#                where b.otherid = a.card_id and b.id = %s and a.date::timestamp = '"""+ date_print +"""' and a.card_id != '1'
#                group by a.date, a.card_id, b.id 
#                order by a.date asc""", (employee_id,))
            self.cr.execute("""
                select b.id as employee_id, a.day as day, min(a.name) as sign_in, max(a.name) as sign_out, max(a.name)-min(a.name) as total
                from hr_attendance a, hr_employee b 
                where b.id = a.employee_id and b.id = %s and a.day::timestamp = '"""+ date_print +"""' and b.otherid != '1'
                group by a.day, b.id
                order by a.day
                """, (employee_id,))
            #if self.cr.fetchall():
            for employee_id, day, sign_in, sign_out, total in self.cr.fetchall():
                res = {}
                #res['card_id'] = card_id
                res['employee_id'] = employee_id
                res['day'] = day
                res['sign_in'] = sign_in
                res['sign_out'] = sign_out
                res['total'] = total
                employee.append(res)
            return employee
                
        else:
            return False
    
    def _get_work_time_monthly(self, employee_id, month_print):
        import datetime
        import time
        period = self.pool.get('account.period').browse(self.cr, self.uid, month_print)
        date_obj = self.pool.get('res.date')
        #print "month_print",month_print,period.date_start,period.date_stop
        sign_in='%s 00:00:00'%period.date_start
        sign_out='%s 23:59:59'%period.date_stop
        #date_ids = date_obj.search(self.cr, self.uid, [('date','>=',period.date_start),('date','<=',period.date_stop)])
        date_ids = date_obj.search(self.cr, self.uid, [])
	date_unlink = date_obj.unlink(self.cr, self.uid, date_ids)
	day = datetime.datetime.strptime(period.date_start, '%Y-%m-%d')
        while day <= datetime.datetime.strptime(period.date_stop, '%Y-%m-%d'):
            #print "day",time.strftime('%H:%M:%S', datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S'))
            hari = str(day)
            x = time.strftime('%w', time.strptime(hari[:10],'%Y-%m-%d'))# time.strftime(hari[:10])
            if x == '1':
                w = 'Senin'
            elif x == '2':
                w = 'Selasa'
            elif x == '3':
                w = 'Rabu'
            elif x == '4':
                w = 'Kamis'
            elif x == '5':
                w = 'Jumat'
            elif x == '6':
                w = 'Sabtu'
            else:
                w = 'Minggu'
            #print "day",day
            #date_ids = date_obj.search(self.cr, self.uid, [('date','=',hari[:10])])
            #if not date_ids:
	    date_obj.create(self.cr, self.uid, {'name': w, 'period_id': period.id, 'date': day, 'day': hari[:10]})
            #datetime.datetime.strptime(period.date_start, '%Y-%m-%d') + datetime.timedelta(days=1)
            day += datetime.timedelta(days=1)
        #print sign_in, sign_out
        if month_print and employee_id:
            employee=[]
            #attendance_ids=self.pool.get('hr.attendance').search(self.cr,self.uid,[('employee_id','=',employee_id),('name','>=',sign_in),('name','<=',sign_out)],order="employee_id,name ASC")
            attendance_ids=self.pool.get('hr.attendance').search(self.cr,self.uid,[('employee_id','=',employee_id),('name','>=',sign_in),('name','<=',sign_out)],order="employee_id,name ASC")
            #print 'attendance_ids==================',attendance_ids
            attendance_datas=self.pool.get('hr.attendance').browse(self.cr, self.uid, attendance_ids)
            dummy = []
#            self.cr.execute("""
#                select a.card_id, b.id as employee_id, a.date, min(a.name) as sign_in, max(a.name) as sign_out, max(a.name)-min(a.name) as total
#                from hr_attendance_virtual a, hr_employee b 
#                where b.otherid = a.card_id and b.id = %s and a.date::timestamp >= %s and a.date::timestamp <= %s and a.card_id != '1'
#                group by a.date, a.card_id, b.id 
#                order by a.date asc""", (employee_id, sign_in, sign_out,))
#            self.cr.execute("""
#                select b.id as employee_id, a.day as day, min(a.name) as sign_in, max(a.name) as sign_out, max(a.name)-min(a.name) as total 
#                from hr_attendance a, hr_employee b
#                where b.id = a.employee_id and b.id = %s and a.day::timestamp >= %s and a.day::timestamp <= %s and b.otherid != '1' 
#                group by a.day, b.id 
#                order by a.day 
#                """,(employee_id, sign_in, sign_out,))
            self.cr.execute("""
                select b.day, b.name, a.employee_id, min(a.name) as sign_in, max(a.name) as sign_out, max(a.name)-min(a.name) as total 
                from res_date b
                left join hr_attendance a on a.day = b.day and a.employee_id = %s 
		where a.day::timestamp >= %s and a.day::timestamp <= %s 
                group by b.day, b.name, a.employee_id 
                order by b.day 
                """,(employee_id, sign_in, sign_out,))
            #if self.cr.fetchall():
            for day, name, employee_id, sign_in, sign_out, total in self.cr.fetchall():
                res = {}
                #res['card_id'] = card_id
                res['day'] = day
                res['name'] = name
                res['employee_id'] = employee_id
                res['sign_in'] = sign_in
                res['sign_out'] = sign_out
                res['total'] = total
                employee.append(res)
            return employee
                
        else:
            return False
    
report_sxw.report_sxw('report.report.hr.attendance', 'hr.attendance.report.wizard', 'addons/ad_hr_report/report/attendance_report.mako', parser = report_attendance_parser, header = True)    
report_sxw.report_sxw('report.report.hr.attendance.monthly', 'hr.attendance.report.wizard', 'addons/ad_hr_report/report/attendance_report_monthly.mako', parser = report_attendance_parser, header = True)

