# -*- encoding: utf-8 -*-

from osv import fields, osv
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta

class hr_job_level(osv.osv):
    _name = "hr.job.level"
    #_description = "This object allows to add different levels (qualification/seniority)"
    _columns = {
        'job_id'	: fields.many2one('hr.job', 'Job'),
        'name' 		: fields.char('Level Name', size=64, required=True),
        'job_level'	: fields.integer('Level'),
        'mini_wage'	: fields.float('Level minimum wage', digits=(10, 2)),
        'max_wage'  : fields.float('Level Maximum Wage', digits=(10, 2)),
        'sal_struc'	: fields.many2one('hr.payroll.structure', 'Salary Structure'),
        'allowance' : fields.float('Allowance'),
        'deduction' : fields.float('Deduction'),
        }
    
     
    def onchange_sal_structure(self, cr, uid, ids, sal_struc, context={}):
        allowance=0
        deduction=0
        if sal_struc:
            sal_data=self.pool.get('hr.payroll.structure').browse(cr,uid,sal_struc)
            for x in sal_data.line_ids:
                if x.type=='allowance':
                    allowance+=x.amount
                elif x.type == 'deduction':
                    deduction+= x.amount
                    
            val = {
                   'allowance': allowance,
                   'deduction': deduction,
                }
            print "value===",val
            return {'value':val}
    
    
    
    
hr_job_level()

class hr_employee(osv.osv):
	_name = "hr.employee"
	_description = "Employee extension"
	_inherit = "hr.employee"

	def _current_employee_age(self, cr, uid, ids, field_name, arg, context):
		res = {}
		today = datetime.now()
		dob = today
		for employee in self.browse(cr, uid, ids):			
			if employee.birthday:
				dob = datetime.strptime(employee.birthday, '%Y-%m-%d')
				res[employee.id] = relativedelta (today, dob).years
		return res
												
	_columns = {
 		'age' : fields.function(_current_employee_age, method=True, string='Age', type='integer', store=True),
	 	'can_use_perso_email' : fields.boolean('Can use personal email'),
		'emergency_contact' : fields.char('Emergency contact', size=64),
        'emergency_relation' : fields.char('Relation', size=64),
		'emergency_phone' : fields.char('Emergency phone', size=64),
	}
		
hr_employee()
