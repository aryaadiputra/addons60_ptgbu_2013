from osv import osv,fields

class hr_rate(osv.osv):
    _name       = "hr.rate"
    _description= "Penilaian Karyawan"
    _columns    = {
                   'name'       : fields.many2one('hr.employee','Name'),
                   'year'       : fields.char('Periode (year)',size=4,required=True),
                   'rate'       : fields.selection([('1','1'),
                                                    ('2','2'),
                                                    ('3','3'),
                                                    ('4','4'),
                                                    ('5','5'),
                                                    ('6','6'),
                                                    ('7','7')], 'Rating', help="Rate",required=True),
                   'notes'      : fields.text('Notes'),
                   }
hr_rate()

class hr_employee(osv.osv):
    _inherit        = "hr.employee"
    _columns        = {
                       'rate'   : fields.one2many('hr.rate','name','Rate')
                       }
hr_employee()