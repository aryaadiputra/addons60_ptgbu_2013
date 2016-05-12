from report import report_sxw
#from datetime import date
#from datetime import datetime
import datetime
import time
import tools
#from tools.translate import _

class hr_cv(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(hr_cv, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                                  'get_object'      : self._get_object,
                                  'get_date'        : self._get_date,
                                  'get_gender'      : self._get_gender,
                                  'get_blood'       : self._get_blood,
                                  'get_current_date': self._get_current_date,
                                  })
        
    def _get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['id']])
        return obj_data
    
    def _get_gender(self,gender):
        if gender=='male':
            gender='Laki-laki'
        elif gender=='female':
            gender='Perempuan'
        return gender
    
    def _get_blood(self,blood):
        if blood=='o':
            blood='O'
        elif blood=='a':
            blood='A'
        elif blood=='b':
            blood='B'
        elif blood=='ab':
            blood='AB'
        return blood
    
    def _get_date(self, date):
        tmt=""
        if date:
            try:
                ttyme = datetime.datetime.strptime(date,"%Y-%m-%d")
            except:
                ttyme = ''#datetime.datetime.strptime(date,"%d-%m-%Y") or False
            if ttyme:
                tmt = tools.ustr(ttyme.strftime('%d %B %Y'))
        return tmt 
    
    def _get_current_date(self):
        current = datetime.date.today()
        ttyme = datetime.datetime.strptime(current,"%Y-%m-%d")
        tmt = tools.ustr(ttyme.strftime('%d %B %Y'))
        return tmt
    
report_sxw.report_sxw('report.hr.employee.cv', 'hr.employee', 'addons/hr_experience/report/hr_cv_report.mako', parser=hr_cv, header=False)
