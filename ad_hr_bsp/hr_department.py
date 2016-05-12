from osv import osv,fields

class hr_department(osv.osv):
    _inherit = "hr.department"
    _columns = {
                'department_code'       : fields.char('Department Code',size=16),
                'placement'             : fields.selection([('bsp','Kantor Pusat'),
                                                            ('bob','BOB')], 'Placement'),
                'bagian' : fields.selection([('core','Core'),
                                             ('subcore','Sub Core'),
                                             ('support','Support')])
                }
hr_department()

class hr_job(osv.osv):
    _inherit = "hr.job"
    _columns = {
                'placement'             : fields.selection([('bsp','Kantor Pusat'),
                                                            ('bob','BOB')], 'Placement'),
                'section_id'            : fields.many2one('hr.section','Section'),
                }
hr_job()
