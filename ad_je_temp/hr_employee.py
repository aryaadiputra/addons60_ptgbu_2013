from osv import fields, osv

import addons

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    
    _columns = {}
    
    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('SELECT DISTINCT parent_id FROM hr_employee WHERE id IN %s AND parent_id!=id',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True
    
    def _check_department_id(self, cr, uid, ids, context=None):
        for emp in self.browse(cr, uid, ids, context=context):
            if emp.department_id.manager_id and emp.id == emp.department_id.manager_id.id:
                return True
        return True
    
    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive Hierarchy of Employees.', ['parent_id']),
        (_check_department_id, 'Error ! You cannot select a department for which the employee is the managerxxxxxxxx.', ['department_id']),
    ]
hr_employee()