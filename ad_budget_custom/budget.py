from osv import fields, osv

class hr_division(osv.osv):
    _name = 'hr.division'
    _description = 'Human Resource Division'
    
    _columns = {
        'name': fields.char('Division Name', size=64, required=True),
        #'complete_name': fields.function(_dept_name_get_fnc, method=True, type="char", string='Name'),
        'company_id': fields.many2one('res.company', 'Company', select=True, required=False),
        'parent_id': fields.many2one('hr.division', 'Parent Division', select=True),
        'child_ids': fields.one2many('hr.division', 'parent_id', 'Child Divisions'),
        #'department_ids': fields.one2many('hr.department', 'division_id', 'Department'),
        'manager_id': fields.many2one('hr.employee', 'Manager'),
        'note': fields.text('Note'),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.department', context=c),
    }
    
hr_division()