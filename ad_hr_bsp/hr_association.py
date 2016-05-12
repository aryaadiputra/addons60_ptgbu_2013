from osv import osv,fields

class hr_association(osv.osv):
    _name           = "hr.association"
    _description    = "Keanggotaan Profesional"
    _columns        = {
                       'name'           : fields.many2one('hr.employee','Name'),
                       'from'           : fields.char('From (year)',size=4,required=True),
                       'to'             : fields.char('To (year)',help="If the membership is unlimited, leave it empty",size=4),
                       'association'    : fields.char('Association',size=64,requried=True),
                       'position'       : fields.char('Position',size=32),
                       'notes'          : fields.text('Notes'),
                       }
hr_association()

class hr_employee(osv.osv):
    _inherit        = "hr.employee"
    _columns        = {
                       'association'   : fields.one2many('hr.association','name','Association')
                       }
hr_employee()