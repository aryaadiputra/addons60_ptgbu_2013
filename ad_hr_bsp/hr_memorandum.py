from osv import osv,fields
import datetime
import calendar

class hr_memorandum(osv.osv):
    _name           = "hr.memorandum"
    _description    = "Memorandum (Surat Peringatan)"
    
    def onchange_date_issued(self,cr,uid,ids,var):
        val = {}
        if var:
            var=var.split('-')
            issued = datetime.datetime(int(var[0]), int(var[1]), int(var[2]), 0, 0, 0)
            y=int(var[0])
            m=int(var[1])+6
            d=int(var[2])
            if m>12:
                y+=1
                m%=12
            semester = datetime.datetime(y,m,d,0,0,0)
            one_day  = datetime.timedelta(1)
            
#            foo=False
#            while not foo:
#                if calendar.monthrange(y, m)<d-1:
#                    d=calendar.monthrange(y, m)[1]
#                    foo=True
            
            valid=(semester-one_day).strftime('%Y-%m-%d')
            val['valid_until']=valid
        return {'value':val}
    
    _columns        = {
                       'name'       : fields.many2one('hr.employee','Employee',required=True),
                       'date_issued': fields.date('Date Issued'),
                       'valid_until': fields.date('Valid Until'),
                       'wl'         : fields.selection([('one','1'),
                                                        ('two','2'),
                                                        ('three','3'),
                                                        ('final','Final Warning')], 'Warning Letter'),
                       'reason'     : fields.text('Reason','Alasan dikeluarkannya SP (Surat Peringatan)'),
                       'letter'     : fields.binary('Attachment'),
                       }
hr_memorandum()

class hr_employee(osv.osv):
    _inherit        = "hr.employee"
    _columns        = {
                       'memorandum' : fields.one2many('hr.memorandum','name','Memorandum')
                       }
hr_employee()