from osv import fields, osv

class hr_education (osv.osv):
    _name = 'hr.education'
    _description= 'Education Background List of Employee'

    #Check whether the course title and the course description are not the same
    _columns = {
                'edu_from'          : fields.char("Start (year)", size=4,  help="Education start"),
                'edu_to'            : fields.char("Finish (year)", size=4, help="Education finish"),
                'type'          : fields.selection([('formal','Formal'),
                                                ('informal','Informal')],'Type'),
                'name'          : fields.char('Edu Name', size=64, required=False, help="Education name (ie. School/University Name)"),
                'subject'       : fields.char('Department', size=64, required=False, help="Education subject"),
                'notes'         : fields.text('Notes'),
                'res_id'        : fields.integer('Resource ID', select=1, readonly=True),
                'employee'      : fields.many2one('hr.employee','Employee'),
                'passed'        : fields.selection([('yes','Lulus'),
                                                ('no','Tidak lulus'),
                                                ('move','Pindah')], 'Status'),
                'degree'        : fields.char('Degree',size=16),
                'certificate'   : fields.binary('Attachment'),
                }

hr_education()

class hr_employee(osv.osv):
    """ HR Employee """
    _inherit = "hr.employee"
    _columns = {
                'education_id': fields.one2many('hr.education', 'employee', 'Education background', required=True ),
                #'message_ids': fields.one2many('mailgate.message', 'res_id', 'Messages', domain=[('model','=',_name)]),
                }

hr_employee()
