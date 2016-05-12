from osv import osv,fields

class hr_section(osv.osv):
    _name   = 'hr.section'
    _columns= {
               'name'       : fields.char('Section Name', size=32, required=True, select=True),
               'department' : fields.many2one('hr.department','Department'),
               'code'       : fields.char('Section Code', size=32),
               'parent_id'  : fields.many2one('hr.section', 'Parent Section', select=True),
               'chief_id'   : fields.many2one('hr.employee', 'Section Leader', select=True),
               'company_id' : fields.many2one('res.company', 'Company', select=True),
               'employee'   : fields.one2many('hr.employee', 'section', 'Member'),
               'placement'  : fields.selection([('bsp','Kantor Pusat'),
                                                ('bob','BOB')], 'Placement'),
               'note'       : fields.text('Notes'),
               }
    _defaults= {
                'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.department', context=c),
                }
    
hr_section()
