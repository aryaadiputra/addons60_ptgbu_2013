from osv import osv, fields

class hr_employee(osv.osv):
    ''' inherited hr.employee '''
    _inherit = "hr.employee"
    _columns = {
        'ktp' : fields.char('KTP No', size=20, required=False, help="Indonesian ID Card Number / Kartu Tanda Penduduk"),
              }

    def _check_ktp(self,cr,uid,ids,context=None):
        for employees in self.browse(cr, uid, ids, context=context):
            if not employees.ktp:
                continue
            if len(employees.ktp) < 10:
                return False
        return True 
    
    _constraints = [(_check_ktp, "KTP number is invalid. The format should be like this: 01.855.081.4-005.000", "ktp")]

hr_employee()
