from osv import osv, fields

class form_f2a(osv.osv):
    _name       = "form.f2a"
    _columns    = {
                   'name'           : fields.many2one('res.partner', 'Company', required=True),
                   'npp'            : fields.char('NPP', size=16),
                   'nuk'            : fields.char('Nama Unit Kerja', size=16),
                   'period_id'      : fields.many2one('account.period','Period',required=True),
                   'jamsostek'      : fields.many2many('hr.jamsostek','jamsostek_f2a_rel','jamsostek_id','f2a_id','Jamsostek'),
                   }
form_f2a()