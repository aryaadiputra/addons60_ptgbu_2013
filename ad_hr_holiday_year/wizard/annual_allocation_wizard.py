from osv import osv, fields
from tools.translate import _

class annual_allocation_wizard(osv.osv_memory):
    _name       = "annual.allocation.wizard"
    _columns    = {
                   'name'           : fields.many2one('account.fiscalyear','Year',required=True),
                   'type_id'        : fields.many2one('hr.holidays.status','Leave Type',required=True),
                   'total_allo'     : fields.integer('Total Allocation'),
                   'employee_ids'   : fields.many2many('hr.employee','employee_annual_rel','employee_id','wizard_id','Employee'),
                   }
    
    def create_allocation(self,cr,uid,ids,context=None):
        holidays_obj = self.pool.get('hr.holidays')
        for allocation in self.browse(cr,uid,ids):
            for employee in allocation.employee_ids:
                data = {
                        'name'                  : "Cuti Tahun "+allocation.name.name,
                        'employee_id'           : employee.id,
                        'holiday_status_id'     : allocation.type_id.id,
                        'number_of_days_temp'   : allocation.total_allo,
                        'type'                  : 'add',
                        }
                if employee.department_id:
                    data['department_id'] = employee.department_id.id
                print data
                create=holidays_obj.create(cr,uid,data)
                print create
        
        res = {
            'domain': [('type','=','add')],
            'name': 'Allocation Request',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.holidays',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': [('default_type','=','add')]
        }
        return res
annual_allocation_wizard()