from osv import osv,fields

class mutation_history(osv.osv):
    _name = "mutation_history"
    _description = "Mutation History of Employee"
    _columns = {
                'name'      : fields.many2one('hr.employee','Employee Name'),
                'department': fields.many2one('hr.department','Department'),
                'duedate'   : fields.date('Mutation Date'),
                }
mutation_history()

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _columns = {
                'employement_history'   : fields.one2many('employment.history','name'),
                }
hr_employee()