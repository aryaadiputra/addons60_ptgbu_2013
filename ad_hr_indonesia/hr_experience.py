from osv import fields, osv

class hr_experience (osv.osv):
    _name = 'hr.experience'
    _description= 'Experience List of Employee'

    #Check whether the course title and the course description are not the same
    _columns = {
        'exp_from'      : fields.char('From', size=30, required = True),
        'exp_to'        : fields.char('To', size=30, required = True),
        'name'          : fields.char('Company Name', size=64, required = True), 
        'address'       : fields.char('Address',size=128),
        'exp_position'  : fields.char('Latest Position', size=64, required = False),
        'wage'          : fields.integer('Last Wage'),
        'exp_notes'     : fields.text('Notes'),
        'res_id'        : fields.integer('Resource ID', select=1, readonly=True),
                }
    _order = 'exp_from'

    #Allow to make a duplicate Course
    def copy(self, cr, uid, id, default={}, context=None):
        previous_name = self.browse(cr, uid, id, context=context)
        if not default:
            default = {}
        default = default.copy()
        default['exp_from'] = (previous_name['exp_from'] or '') + '(copy)'
        print default['exp_from']
        return super(hr_experience, self).copy(cr, uid, id, default, context=context)

hr_experience()

class hr_employee(osv.osv):
    """ HR Employee """
    _inherit = "hr.employee"
    _columns = {
        'experience_id': fields.one2many('hr.experience', 'res_id', 'Experiences', required=True ),
              }

hr_employee()

