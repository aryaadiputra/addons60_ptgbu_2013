from osv import osv, fields

class family_job(osv.osv):
    _name   = 'family.job'
    _columns= {
               'name'   : fields.char('Job',size=32,required=True),
               'note'   : fields.text('Note'),
               }
family_job()