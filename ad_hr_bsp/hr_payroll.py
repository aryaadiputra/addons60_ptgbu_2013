from osv import osv,fields

class hr_payroll_structure(osv.osv):
    _inherit        = "hr.payroll.structure"
    _columns        = {
                       'level_id'       : fields.many2one('hr.job.level','Level')
                       }
hr_payroll_structure()