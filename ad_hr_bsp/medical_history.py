from osv import osv,fields
import time

class medical_history(osv.osv):
    _name           = "medical.history"
    _columns        = {
                       'name'           : fields.text('Summary Medical Check Up'),
                       'date'           : fields.date('Date'),
                       'periode'        : fields.char('Year',size=4),
                       'place'          : fields.many2one('res.partner','Hospital Name'),
                       'address'        : fields.many2one('res.partner.address', 'Address'),
                       'status'         : fields.boolean('Done'),
                       'medical_record' : fields.binary('Medical Record'),
                       'employee_id'    : fields.many2one('hr.employee','Employee'),
                       'height'         : fields.float ('Height'),
                       'weight'         : fields.float('Weight'),
                       'blood_pressure'     : fields.char('Blood Pressure', size=8)
                       }








medical_history()









class hr_employee(osv.osv):
    _inherit        = "hr.employee"
    _columns        = {
                       'medical_ids'    : fields.one2many('medical.history','employee_id','Medical History'),
                       }
hr_employee()