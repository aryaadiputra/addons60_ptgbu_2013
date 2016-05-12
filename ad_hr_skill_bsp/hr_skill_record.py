from osv import osv,fields

class hr_skill_category(osv.osv):
    _name   = "hr.skill.category"
    _description = "Category of employee's Skill"
    _columns    = {
                   'name'   : fields.char('Category', size=32, required=True),
                   'code'   : fields.char('Code', size=24),
                   }

hr_skill_category()


class hr_skill_record(osv.osv):
    _name       = "hr.skill.record"
    _columns    = {
                   'category'       : fields.many2one('hr.skill.category', 'Category', select=True),
                   'name'           : fields.char('Skill',size=32,required=True,select=True),
                   'desc'           : fields.text('Deskripsi',select=True),
                   'employee_ids'   : fields.many2many('hr.employee','skill_employee_rel','skill_id','emp_id','Karyawan'),
                   'level'          : fields.selection([('beginner','Beginner'),
                                                        ('intermediate','Intermediate'),
                                                        ('advance','Advance'),
                                                                            ],'Level')
                   }
hr_skill_record()

class hr_employee(osv.osv):
    _inherit    = "hr.employee"
    _columns    = {
                   'skill_ids'      : fields.many2many('hr.skill.record','skill_employee_rel','emp_id','skill_id','Skill'),
                   }
hr_employee()