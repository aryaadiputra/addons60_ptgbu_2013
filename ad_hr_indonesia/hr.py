from osv import osv, fields
import datetime
from mx import DateTime
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tools.translate import _

class hr_employee(osv.osv):
    _inherit = "hr.employee"
        

    def _get_pension_date(self, cr, uid, ids, name, arg, context={}):
        result={}
        for emp in self.browse(cr, uid, ids, context=context):
            if emp.birthday and emp.retiring_age:
                dob=datetime.strptime(emp.birthday,'%Y-%m-%d')
                pension=dob+relativedelta(years=emp.retiring_age)
                pension=pension.strftime('%Y-%m-%d')
                result[emp.id]=pension
            else:
                result[emp.id]=False
        return result
    
    def _compute_age(self, cr, uid, ids, name, arg, context={}):
        def compute_age_from_dates (birthday):
            now=datetime.now()
            if (birthday):
                dob=datetime.strptime(birthday,'%Y-%m-%d')
                delta=relativedelta (now, dob)
                if delta.months==0:
                    years_months_days = str(delta.years) +" years"
                else:
                    years_months_days = str(delta.years) +" years and "+ str(delta.months) +" months"
            else:
                years_months_days = "No Date of birth !"
            return years_months_days
        result={}
        for emp in self.browse(cr, uid, ids, context=context):
            result[emp.id] = compute_age_from_dates (emp.birthday)
        return result
    
    def _compute_dur(self, cr, uid, ids, name, arg, context={}):
        def compute_dur_from_age (birthday,retired):
            now=datetime.now()
            if (birthday):
                dob=datetime.strptime(birthday,'%Y-%m-%d')
                delta=relativedelta (now, dob)
                age_year = delta.years
                age_month= delta.months
                if (retired<>0):
                    if age_month==0:
                        dur_year    = str(retired-age_year)
                        dur_year_month  = dur_year+" years remaining"
                    else:
                        dur_year    = str(retired - age_year - 1)
                        dur_month   = str(12 - age_month)
                        dur_year_month  = dur_year+" years and "+dur_month+" months remaining"
                    if int(dur_year)<0:
                        dur_year_month  = "Retired"
                else:
                    dur_year_month  = "No Retired Age"
            else:
                dur_year_month = "No Date of birth !"
            return dur_year_month
        result={}
        for emp in self.browse(cr, uid, ids, context=context):
            result[emp.id] = compute_dur_from_age (emp.birthday,emp.retiring_age)
        return result
    
    _columns = {
                'nik'               : fields.char('NIK', size=20, required=False, help="Nomor Induk Karyawan / Employee ID"),
                'blood_type'        : fields.selection([('a','A'),
                                                        ('b','B'),
                                                        ('ab','AB'),
                                                        ('o','O')], 'Blood Type'),
                'marriage_date'     : fields.date('Marriage Date'),
                'extension'         : fields.char('Extension',size=8),
                'admission_letter'  : fields.char('Admission Letter',size=32),
                'admission_date'    : fields.date('Admission Date'),
                'retiring_age'      : fields.integer('Pensiun Plan Age'),
                'mpp_date'          : fields.date('MPP Start Date'),
                'mpp'               : fields.boolean('Active'),
                'retiring_date'     : fields.function(_get_pension_date, method=True,store=True, type='date', string='Pension Date'),
                'retiring'          : fields.boolean('Active'),
                'birthplace'        : fields.char('Birth Place',32),
                'parent'            : fields.char('Parent',size=32),
                'duration2retire'   : fields.function(_compute_dur, method=True, type='char', size=32, string='Duration to Pension'),
                'emp_age'           : fields.function(_compute_age, method=True, type='char', size=32, string='Employee Age',help="It shows the age of the employee"),
                }
    _sql_constraints = [
        ('nik_uniq', 'unique (nik)', 'NIK must be unique per employee !')
    ]
    def name_get(self, cr, uid, ids, context=None):
        res = []
        for emp in self.browse(cr, uid, ids, context=context):
            if emp.nik==False:
                nik=""
            else:
                nik=" ("+emp.nik+")"
            name=emp.name+nik
            res.append((emp.id, name or emp.name))
        return res
hr_employee()