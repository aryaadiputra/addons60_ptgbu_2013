from osv import fields, osv

class hr_family_relation (osv.osv):
    _name = 'hr.family.relation'
    _description = 'Relation Family of Employee'

    _columns = {
    
        'name': fields.char('Relation', size=30, required=True),
        'notes': fields.text('Description'),
    
                }

hr_family_relation()

class hr_family (osv.osv):
    _name = 'hr.family'
    _description = 'Family of Employee'

    _columns = {
                'employee'          : fields.many2one('hr.employee','Employee'),
                'res_id'            : fields.integer('Resource ID', select=1, readonly=True),
                'name'              : fields.char('Name', size=30, required=True),
                'gender'            : fields.selection([('male','Male'),
                                                        ('female','Female')], 'Gender'),
                'relation'          : fields.many2one('hr.family.relation', 'Relation'),
                'place_of_birth'    : fields.char ('Place of Birth', size=30, required=False),
                'birthday'          : fields.date('Birthday'),
                'job'               : fields.many2one('family.job','Job',size=32),
                'religion'          : fields.many2one('res.religion','Religion'),
                'address'           : fields.text('Address'),
                'city'              : fields.char('City',size=32),
                'phone'             : fields.char('Phone',size=20),
                'father'            : fields.char('Father', size=32),
                'mother'            : fields.char('Mother', size=32),
                'education'         : fields.selection([('tk','TK'),
                                                        ('sd','SD'),
                                                        ('smp','SMP'),
                                                        ('sma','SMA'),
                                                        ('pelajar','Pelajar'),
                                                        ('mahasiswa','Mahasiswa'),
                                                        ('d1','Diploma 1'),
                                                        ('d2','Diploma 2'),
                                                        ('d3','Diploma 3'),
                                                        ('d4','Diploma 4'),
                                                        ('s1','S1'),
                                                        ('s2','S2'),
                                                        ('s3','S3'),
                                                        ('others','Others')], 'Education'),
                'is_borned'         : fields.boolean('Is borned',help='Check this box if this person is borned by the employee.'),
                'photo': fields.binary('Photo'),
                }
    _order = 'birthday'

    def copy(self, cr, uid, id, default={}, context=None):
        previous_name = self.browse(cr, uid, id, context=context)
        if not default:
            default = {}
        default = default.copy()
        default['name'] = (previous_name['name'] or '') + '(copy)'
        print default['name']
        return super(hr_family, self).copy(cr, uid, id, default, context=context)
hr_family()

class hr_employee(osv.osv):
    """ HR Employee """
    _inherit = "hr.employee"
    _columns = {
        'family_id': fields.one2many('hr.family', 'res_id', 'Employee Family', required=False),
              }

hr_employee()
