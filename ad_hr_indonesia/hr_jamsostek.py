from osv import osv, fields

class hr_employee(osv.osv):
    ''' inherited hr.employee '''
    _inherit = "hr.employee"
    _columns = {
                'emp_status'    : fields.char('Employee Status',size=64),
                'tax_type'      : fields.selection([('k1','K1'),
                                                    ('k2','K2'),
                                                    ('k3','K3')],'Tax Type'),
                'insurance_id'  : fields.char('BPJS No', size=20, required=False, help="Insurance Name or Number"),
                'dpk_number'    : fields.char('DPLK',size=16, help="ID Dana Pensiun Karyawan"),
              }
hr_employee()
