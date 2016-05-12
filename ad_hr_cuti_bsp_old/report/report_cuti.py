from report import report_sxw
from datetime import datetime
from osv import osv
import time
import pooler
import tools
from tools.translate import _
from datetime import date
from dateutil.rrule import rrule, DAILY, MONTHLY
from dateutil import parser

class report_cuti(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        
        super(report_cuti, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'track_days':self._track_days,
            'track_date':self._track_date,
            'get_employees_data':self._get_employees_data,
            'get_colspan_month':self._get_colspan_month,
            'get_dep':self._get_dep,
            'get_emp_ids':self._get_emp_ids,
        })
    
    def _track_days(self,date_start,date_end):
        days=[]
        date_start=parser.parse(date_start)
        date_end=parser.parse(date_end)
        for dt in rrule(DAILY, dtstart=date_start, until=date_end):
            #print dt.strftime("%Y-%m-%d")
            days.append(dt.strftime("%a"))
        return days
    
    def _track_date(self,date_start,date_end):
        days=[]
        date_start=parser.parse(date_start)
        date_end=parser.parse(date_end)
        for dt in rrule(DAILY, dtstart=date_start, until=date_end):
            vals={'date':dt.strftime("%Y-%m-%d"),'d':dt.strftime("%d")}
            days.append(vals)
        return days
    
    def _get_employees_data(self,start,end,employee_ids):
        emp_pool=self.pool.get('hr.employee')
        holiday_pool=self.pool.get('hr.holidays')
        osl_pool=self.pool.get('outstanding.leave')
        osh_pool=self.pool.get('outstanding.holiday')
#        emp=emp_pool.search(self.cr,self.uid,[])
        emp_data=emp_pool.browse(self.cr, self.uid, employee_ids)
        employee=[]
        for e in emp_data:
            data_cuti={}
            data_holiday={}
            data_osl={}
            data_osh={}
            holidays = holiday_pool.search(self.cr,self.uid,[('employee_id','=',e.id),('state','=','validate'),('type','=','remove'),('date_from','>=',start),('date_to','<=',end)])
            outstanding_leave = osl_pool.search(self.cr,self.uid,[('state','in',('done','approve')),('start','>=',start),('end','<=',end)])
            outstanding_holiday = osh_pool.search(self.cr,self.uid,[('state','in',('done','approve')),('start','>=',start),('end','<=',end)])
            
            holidays_data = holiday_pool.browse(self.cr,self.uid,holidays)
            osl_data = osl_pool.browse(self.cr,self.uid,outstanding_leave)
            osh_data = osh_pool.browse(self.cr,self.uid,outstanding_holiday)
            
            for hd in holidays_data:
                date_start = parser.parse(hd.date_from)
                date_end = parser.parse(hd.date_to)
                for dt in rrule(DAILY, dtstart=date_start, until=date_end):
                    data_holiday.update({dt.strftime("%Y-%m-%d") : "".join([x[0] for x in hd.holiday_status_id.name.split()]).upper()})
            
            for osl in osl_data:
                date_start = parser.parse(osl.start)
                date_end = parser.parse(osl.end)
                for dt in rrule(DAILY, dtstart=date_start, until=date_end):
                    data_osl.update({dt.strftime("%Y-%m-%d") : "".join([x[0] for x in osl.name.split()]).upper()})
                    
            for osh in osh_data:
                date_start = parser.parse(osh.start)
                date_end = parser.parse(osh.end)
                for dt in rrule(DAILY, dtstart=date_start, until=date_end):
                    data_osh.update({dt.strftime("%Y-%m-%d") :  "".join([x[0] for x in osh.name.split()]).upper()})

            data_cuti.update(data_holiday)
            data_cuti.update(data_osl)
            data_cuti.update(data_osh)
            value=[{'name':e.resource_id.name,'nik':e.nik,'cuti':data_cuti}]
            employee += value
#            if e.resource_id.name == 'Budi Susanto':
#                print "employee===============>",employee
        return employee
    
    def _get_cols(self,date_start,date_end,month):
#        date_start=parser.parse(start)
#        date_end=parser.parse(end)
        y=0
        for a in rrule(DAILY, dtstart=date_start, until=date_end):
            if a.strftime("%B")==month.strftime("%B"):
                y+=1
        return y
    
    def _get_colspan_month(self,start,end):
        date_start=parser.parse(start)
        date_end=parser.parse(end)
        string=""
        month=rrule(MONTHLY, dtstart=date_start, until=date_end)
        x=0
        for a in month:
            #cols=self._get_cols(a,month[x+1] or rrule(MONTHLY, rrule(MONTHLY, dtstart=date_start, until=date_end)[0], until=date_end))
            cols=self._get_cols(date_start,date_end,a)
            #print "==========================",cols
            label=a.strftime("%B")
#            print "==========================*",label
            string+="""<td align="center" colspan="""+str(cols)+""">"""+a.strftime("%B")+"""</td>"""
            x+=1
        return string
    
    def _get_dep(self,dept_id):
        a=self.pool.get('hr.department').browse(self.cr,self.uid,dept_id)
        return a
    
    def _get_emp_ids(self,dept_id):
        return self.pool.get('hr.employee').search(self.cr,self.uid,[('department_id','=',dept_id)])
    
report_sxw.report_sxw('report.report.cuti.bsp', 'hr.employee', 'addons/ad_hr_cuti_bsp/report/report_cuti.mako', parser = report_cuti, header = False)
report_sxw.report_sxw('report.report.cuti.bsp.department', 'hr.employee', 'addons/ad_hr_cuti_bsp/report/report_cuti_department.mako', parser = report_cuti, header = False)