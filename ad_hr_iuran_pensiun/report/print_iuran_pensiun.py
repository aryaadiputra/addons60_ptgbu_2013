from report import report_sxw
from datetime import date
from datetime import datetime
from osv import osv
import time
import pooler
import tools
from tools.translate import _
import decimal_precision as dp

class iuran_pensiun(report_sxw.rml_parse):


    def __init__(self, cr, uid, name, context):
        super(iuran_pensiun, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_employee'      : self._get_employee,
            'get_gender'        : self._get_gender,
            'get_object'        : self._get_object,
            'get_periode'       : self._get_periode,
            'get_birthday'      : self._get_birthday,
            'get_payslip'       : self._get_payslip,
        })
        
    def _get_employee(self, data):
        emp = self.pool.get('hr.employee').browse(self.cr, self.uid, data)
        return emp
    
    def _get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['id']])
        #print "data===================>",obj_data
        return obj_data
    
    def _get_gender(self, data):
        if data=='male':
            gender='L'
        else:
            gender='P'
        return gender
    
    def _get_periode(self, data):
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(data.date_start,"%Y-%m-%d")))
        periode = tools.ustr(ttyme.strftime('%B %Y'))
        return periode
    
    def _get_birthday(self, data):
        if data:
            ttyme = datetime.fromtimestamp(time.mktime(time.strptime(data,"%Y-%m-%d")))
            birthday = tools.ustr(ttyme.strftime('%e %B %Y'))
        else:
            birthday = "-"
        return birthday
    
    def _get_payslip(self, data, emp):
        now = time.strftime('%Y-%m-%d')
        period      = data.period
        payslip_ids = self.pool.get('hr.payslip').search(self.cr,self.uid,[('employee_id','=',emp.id)])
        #print "payslip_ids =======>",payslip_ids
        for payslip in self.pool.get('hr.payslip').browse(self.cr,self.uid,payslip_ids):
            if payslip.date>=period.date_start and payslip.date<=period.date_stop:
                print payslip.date,period.date_stop,period.date_start
                return payslip
            else:
                return False
    
report_sxw.report_sxw('report.print.iuran.pensiun', 'hr.employee', 'ad_hr_iuran_pensiun/report/iuran_pensiun.mako', parser=iuran_pensiun)
