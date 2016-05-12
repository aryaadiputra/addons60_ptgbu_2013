from osv import osv,fields
from tools.translate import _
import calendar
import time
import datetime
from datetime import datetime,timedelta, date
import pooler
from itertools import groupby
from operator import itemgetter
import netsvc
import re
import pooler

class hr_outstanding_holiday(osv.osv):
    _name       = "outstanding.holiday"
    
    def button_proposed(self, cr, uid, ids, context={}):
        for ol in self.browse(cr, uid, ids):
            ol.write({"state":"waiting"})
        return True
    def button_draft(self, cr, uid, ids, context={}):
        for ol in self.browse(cr, uid, ids):
            ol.write({"state":"draft"})
        return True
    def button_approved(self, cr, uid, ids, context={}):
        for ol in self.browse(cr, uid, ids):
            ol.write({"state":"approved"})
        return True
    def button_done(self, cr, uid, ids, context={}):
        for ol in self.browse(cr, uid, ids):
            ol.write({"state":"done",
                      "approved":time.strftime('%Y-%m-%d'),
                      "approve_by":uid})
        return True
    
    def onchange_employee(self,cr,uid,ids,emp):
        val={}
        if emp:
            employee_pool   = self.pool.get('hr.employee')
            val = {}
            emp             = employee_pool.browse(cr,uid,emp)
            val             = {
                               'department_id'  : emp.department_id.id,
                               'section_id'     : emp.section.id
                               }
        return {'value':val}
    
    def onchange_start(self,cr,uid,ids,start,leave):
        start0=start
        registered_holiday = self.pool.get('hr.holiday.year').search(cr,uid,[])
        holiday=[]
        for rhs in registered_holiday:
            rh = self.pool.get('hr.holiday.year').browse(cr,uid,rhs)
            rs_date = datetime.fromtimestamp(time.mktime(time.strptime(rh.date,"%Y-%m-%d")))
            holiday.append(rh.date)
        if leave:
            dur=0
            if leave=='melahirkan':
                dur='m+3'
            elif leave=='keguguran':
                dur='m+1,5'
            dur0=dur
            val={}
            if not start or dur==0:
                val={
                     'return'   : False,
                     'end'      : False,
                     'duration' : 0,
                     }
                return {'value':val}
            if start:
                
                #===================================================================
                # Cuti naik haji, melahirkan dan keguguran
                #===================================================================
                if dur=='m+3':
                    start=datetime.strptime(start,"%Y-%m-%d")
                    year=start.year
                    month=start.month+3
                    day=start.day
                    if month>12:
                        year+=1
                        month%=12
                    if day>calendar.monthrange(year, month)[1]:
                        day=calendar.monthrange(year, month)[1]
                    back=datetime(year,month,day).date()
                    end=back-timedelta(1)
                    foo=False
                    while not foo:
                        if back.strftime("%u")=="6" or back.strftime("%u")=="7" or back.strftime("%Y-%m-%d") in holiday:
                            back=back+timedelta(1)
                        else:
                            foo=True
                    dur=back-start.date()
                    val={
                         'return'   : back.strftime("%Y-%m-%d"),
                         'end'      : end.strftime("%Y-%m-%d"),
                         'duration' : dur.days,
                         }
                    return {'value':val}
                elif dur=='m+1,5':
                    start=datetime.strptime(start,"%Y-%m-%d")
                    year=start.year
                    month=start.month+1
                    day=start.day+15
                    if month>12:
                        year+=1
                        month%=12
                    if day>calendar.monthrange(year, month)[1]:
                        month+=1
                        day-=calendar.monthrange(year, month)[1]
                    back=datetime(year,month,day).date()
                    end=back-timedelta(1)
                    foo=False
                    while not foo:
                        if back.strftime("%u")=="6" or back.strftime("%u")=="7" or back.strftime("%Y-%m-%d") in holiday:
                            back=back+timedelta(1)
                        else:
                            foo=True
                    dur=end-start.date()
                    val={
                         'return'   : back.strftime("%Y-%m-%d"),
                         'end'      : end.strftime("%Y-%m-%d"),
                         'duration' : dur.days,
                         }
                    return {'value':val}
                
        return {'value':val}
    
    def generate_days(self, cr, uid, ids, context={}):
        current=self.pool.get('work.day.holiday').search(cr,uid,[('holiday_id','=',ids[0])])
        self.pool.get('work.day.holiday').unlink(cr,uid,current)
        for holiday in self.browse(cr,uid,ids):
            start   = datetime.strptime(holiday.start,"%Y-%m-%d").date()
            end     = datetime.strptime(holiday.end, "%Y-%m-%d").date()
            datelist=[]
            while start<=end:
                datelist.append(start)
                start+=timedelta(days=1)
            workdays_ids=["1","2","3","4","5"]
            for date in datelist:
                if date.strftime("%u") in workdays_ids:
                    val={
                         'name'         : date.strftime("%Y-%m-%d"),
                         'name_day'     : date.strftime("%u"),
                         'holiday_id'   : ids[0]
                         }
                    self.pool.get('work.day.holiday').create(cr,uid,val)
        return True    
    
    _columns    = {
                   'name'           : fields.selection([('melahirkan','Melahirkan'),
                                                        ('keguguran','Keguguran')], 'Alasan cuti'),
                   'created'        : fields.date('Tanggal Diajukan'),
                   'approved'       : fields.date('Tanggal Disetujui',readonly=True),
                   'approve_by'     : fields.many2one('res.users','Disetujui Oleh',readonly=True),
                   'employee_id'    : fields.many2one('hr.employee','Karyawan',domain=[('gender','=','female'),('type','=','bsp')],required=True),
                   'department_id'  : fields.many2one('hr.department','Departemen'),
                   'manager_id'     : fields.many2one('hr.employee','Manajer'),
                   'section_id'     : fields.many2one('hr.section','Seksi'),
                   'section_lead_id': fields.many2one('hr.employee','Kasie'),
                   'start'          : fields.date('Dari'),
                   'end'            : fields.date('Sampai'),
                   'return'         : fields.date('Masuk'),
                   'duration'       : fields.integer('Lama cuti (hari)'),
                   'workdays_ids'   : fields.one2many('work.day.holiday','holiday_id','Hari Kerja'),
                   'notes'          : fields.text('Catatan'),
                   'state'          : fields.selection([('draft','Draft'),
                                                        ('waiting','Menunggu Persetujuan'),
                                                        ('approved','Disetujui'),
                                                        ('done','Selesai')], 'Status',readonly=True),
                   }
    _defaults   = {
                   'state'      : 'draft',
                   'created'    : time.strftime('%Y-%m-%d'),
                   }
hr_outstanding_holiday()

class hr_outstanding_leave(osv.osv):
    _name       = "outstanding.leave"
    
    def button_proposed(self, cr, uid, ids, context={}):
        for ol in self.browse(cr, uid, ids):
            ol.write({"state":"waiting"})
        return True
    def button_draft(self, cr, uid, ids, context={}):
        for ol in self.browse(cr, uid, ids):
            ol.write({"state":"draft"})
        return True
    def button_approved(self, cr, uid, ids, context={}):
        for ol in self.browse(cr, uid, ids):
            ol.write({"state":"approved"})
        return True
    def button_done(self, cr, uid, ids, context={}):
        for ol in self.browse(cr, uid, ids):
            ol.write({"state":"done",
                      "approved":time.strftime('%Y-%m-%d'),
                      "approve_by":uid})
        return True
    
    def onchange_employee(self,cr,uid,ids,emp):
        if emp:
            employee_pool   = self.pool.get('hr.employee')
            val = {}
            emp             = employee_pool.browse(cr,uid,emp)
            val             = {
                               'department_id'  : emp.department_id.id,
                               'section_id'     : emp.section.id
                               }
        return {'value':val}
    
    def onchange_start(self,cr,uid,ids,start,leave):
        start0=start
        print "aaaaaaaaaaaaaaaaa",start0
        print "aaaaaaaaaaaaaaaaa",start0[0:4]
        registered_holiday = self.pool.get('hr.holiday.year').search(cr,uid,[('year','=',start0[0:4])])
        print "aaaaaaaaaaaaaaaaa",registered_holiday
        holiday=[]
        for rhs in registered_holiday:
            print "bbbbbbbbbbbbbbbbb",rhs
            rh = self.pool.get('hr.holiday.year').browse(cr,uid,rhs)
            print "bbbbbbbbbbbbbbbbb",rh
            rs_date = datetime.fromtimestamp(time.mktime(time.strptime(rh.date,"%Y-%m-%d")))
            print "bbbbbbbbbbbbbbbbb",rs_date
            print "bbbbbbbbbbbbbbbbb",rh.date
            holiday.append(rh.date)
        if leave:
            dur=0
            if leave=='nikah':
                dur=3
            elif leave=='nikah_anak':
                dur=2
            elif leave=='khitanan':
                dur=2
            elif leave=='babtis':
                dur=2
            elif leave=='natalitas':
                dur=2
            elif leave=='mortalitas':
                dur=2
            elif leave=='mortalitas_serumah':
                dur=1
            elif leave=='melahirkan':
                dur='m+3'
            elif leave=='keguguran':
                dur='m+1,5'
            elif leave=='haji':
                dur='haji'
            dur0=dur
            val={}
            if not start or dur==0:
                val={
                     'return'   : False,
                     'end'      : False,
                     'duration' : 0,
                     }
                return {'value':val}
            if start:
                
                #===================================================================
                # Cuti naik haji, melahirkan dan keguguran
                #===================================================================
                if dur=='haji':
                    val={
                         'return'   : False,
                         'end'      : False,
                         'duration' : 0,
                         }
                    return {'value':val}
                elif dur=='m+3':
                    start=datetime.strptime(start,"%Y-%m-%d")
                    year=start.year
                    month=start.month+3
                    day=start.day
                    if month>12:
                        year+=1
                        month%=12
                    if day>calendar.monthrange(year, month)[1]:
                        day=calendar.monthrange(year, month)[1]
                    back=datetime(year,month,day).date()
                    end=back-timedelta(1)
                    foo=False
                    while not foo:
                        if back.strftime("%u")=="6" or back.strftime("%u")=="7" or back.strftime("%Y-%m-%d") in holiday:
                            back=back+timedelta(1)
                        else:
                            foo=True
                    dur=back-start.date()
                    val={
                         'return'   : back.strftime("%Y-%m-%d"),
                         'end'      : end.strftime("%Y-%m-%d"),
                         'duration' : dur.days,
                         }
                    return {'value':val}
                elif dur=='m+1,5':
                    start=datetime.strptime(start,"%Y-%m-%d")
                    year=start.year
                    month=start.month+1
                    day=start.day+15
                    if month>12:
                        year+=1
                        month%=12
                    if day>calendar.monthrange(year, month)[1]:
                        day=calendar.monthrange(year, month)[1]
                    back=datetime(year,month,day).date()
                    end=back-timedelta(1)
                    foo=False
                    while not foo:
                        if back.strftime("%u")=="6" or back.strftime("%u")=="7" or back.strftime("%Y-%m-%d") in holiday:
                            back=back+timedelta(1)
                        else:
                            foo=True
                    dur=end-start.date()
                    val={
                         'return'   : back.strftime("%Y-%m-%d"),
                         'end'      : end.strftime("%Y-%m-%d"),
                         'duration' : dur.days,
                         }
                    return {'value':val}
                
                start=datetime.strptime(start,"%Y-%m-%d")
                print "staaaaaaaaaaaaart", start
                #=============================================================================================
                # Menentukan tanggal kapan cuti karyawan berakhir
                #=============================================================================================
                datelist = [ start + timedelta(days=x) for x in range(0,dur) ]
                print "dateeeeeeeeelist",datelist
                for date in datelist:
                    foo=False
                    while not foo:
                        if date.strftime("%u")=="6" or date.strftime("%u")=="7" or date.strftime("%Y-%m-%d") in holiday:
                            dur=dur+1
                            break
                        else:
                            foo=True
                end1=start+timedelta(dur-1)
                
                #=============================================================================================
                # Selama hari terakhir cuti adalah hari libur, MAJUKAN sampai bukan hari libur
                #=============================================================================================
                foo=False
                while not foo:
                    if end1.strftime("%u")=="6" or end1.strftime("%u")=="7" or end1.strftime("%Y-%m-%d") in holiday:
                        end1=end1+timedelta(1)
                    else:
                        foo=True
                print "eeeeeeeeeeeeeeeeend",end1
                #=============================================================================================
                # Menentukan kapan karyawan seharusnya kembali masuk kerja
                #=============================================================================================
                end=end1+timedelta(1)
                foo=False
                while not foo:
                    if end.strftime("%u")=="6" or end.strftime("%u")=="7" or end.strftime("%Y-%m-%d") in holiday:
                        end=end+timedelta(1)
                    else:
                        foo=True
                val={
                     'return'   : end.strftime("%Y-%m-%d"),
                     'end'      : end1.strftime("%Y-%m-%d"),
                     'duration' : dur0,
                     }
        return {'value':val}
    
    def create(self,cr,uid,data,context):
        if data['start'] and data['end']:
            start=datetime.strptime(data['start'], "%Y-%m-%d")
            end=datetime.strptime(data['end'], "%Y-%m-%d")
            dur=end-start
            dur_min=dur.seconds/60
            dur_hour=dur_min/60
            rest_min=dur_min%60
            if dur_hour==2 and rest_min>0:
                raise osv.except_osv(_('Warning'), _('Karyawan tidak boleh meninggalkan perusahaan lebih dari dua jam!'))
            if rest_min>=30:
                dur_hour=+1
            if dur_hour>2:
                raise osv.except_osv(_('Warning'), _('Karyawan tidak boleh meninggalkan perusahaan lebih dari dua jam!'))
        else:
            raise osv.except_osv(_('Warning'), _('Silahkan masukkan tanggal cuti.'))
        return super(hr_outstanding_leave,self).create(cr,uid,data,context=context)
    
    def onchange_start_end(self,cr,uid,ids,start,end):
        val={}
        if start and end:
            print start,type(start)
            print end,type(end)
            start=datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            end=datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            dur=end-start
            dur_min=dur.seconds/60
            dur_hour=dur_min/60
            rest_min=dur_min%60
            if rest_min>=30:
                dur_hour=+1
            val['dur_hour']=dur_hour
        return {'value':val}
    
    def generate_days(self, cr, uid, ids, context={}):
        current=self.pool.get('work.day.holiday').search(cr,uid,[('leave_id','=',ids[0])])
        self.pool.get('work.day.holiday').unlink(cr,uid,current)
        for leave in self.browse(cr,uid,ids):
            if leave.start and leave.end:
                start   = datetime.strptime(leave.start,"%Y-%m-%d").date()
                end     = datetime.strptime(leave.end, "%Y-%m-%d").date()
                datelist=[]
                while start<=end:
                    datelist.append(start)
                    start+=timedelta(days=1)
                workdays_ids=["1","2","3","4","5"]
                for date in datelist:
                    if date.strftime("%u") in workdays_ids:
                        val={
                             'name'     : date.strftime("%Y-%m-%d"),
                             'name_day' : date.strftime("%u"),
                             'leave_id' : ids[0]
                             }
                        self.pool.get('work.day.holiday').create(cr,uid,val)
            else:
                raise osv.except_osv(_('Warning'), _('Silahkan masukkan tanggal cuti.'))
        return True
    
    _columns    = {
                   'name'           : fields.selection([('nikah','Pernikahan karyawan'),
                                                        ('nikah_anak','Pernikahan anak'),
                                                        ('khitanan','Khitanan anak'),
                                                        ('babtis','Babtisan anak'),
                                                        ('natalitas','Istri melahirkan/keguguran'),
                                                        ('mortalitas','Sanak keluarga meninggal'),
                                                        ('mortalitas_serumah','Keluarga serumah meninggal'),
                                                        ('sakit','Sakit'),
                                                        ('sakit_haid','Sakit haid'),
                                                        ('keluar','Keluar perusahaan'),
                                                        ('tugas_negara','Tugas negara'),
                                                        ('haji','Naik Haji Karyawan'),
                                                        ('no_pay','Ijin tanpa upah'),], 'Alasan Ijin'),
                   'created'        : fields.date('Tanggal Diajukan'),
                   'approved'       : fields.date('Tanggal Disetujui',readonly=True),
                   'approve_by'     : fields.many2one('res.users','Disetujui Oleh',readonly=True),
                   'employee_id'    : fields.many2one('hr.employee','Karyawan',required=True),
                   'department_id'  : fields.many2one('hr.department','Departemen'),
                   'manager_id'     : fields.many2one('hr.employee','Manajer'),
                   'section_id'     : fields.many2one('hr.section','Seksi'),
                   'section_lead_id': fields.many2one('hr.employee','Kasie'),
                   'start'          : fields.datetime('Dari'),
                   'end'            : fields.datetime('Sampai'),
                   'start_time'     : fields.datetime('Dari'),
                   'end_time'       : fields.datetime('Sampai'),
                   'return'         : fields.date('Masuk'),
                   'workdays_ids'   : fields.one2many('work.day.holiday','leave_id','Hari Kerja'),
                   'duration'       : fields.integer('Lama ijin (hari)'),
                   'dur_hour'       : fields.integer('Lama ijin (jam)'),
                   'notes'          : fields.text('Catatan'),
                   'state'          : fields.selection([('draft','Draft'),
                                                        ('waiting','Menunggu Persetujuan'),
                                                        ('approved','Disetujui'),
                                                        ('done','Selesai')], 'Status',readonly=True),
                   }
    _defaults   = {
                   'state'      : 'draft',
                   'created'    : time.strftime('%Y-%m-%d'),
                   }
hr_outstanding_leave()

class work_day_holiday(osv.osv):
    _name       = "work.day.holiday"
    _columns    = {
                   'name'           : fields.date('Tanggal'),
                   'name_day'       : fields.selection([('1','Monday'),
                                                        ('2','Tuesday'),
                                                        ('3','Wednesday'),
                                                        ('4','Thursday'),
                                                        ('5','Friday')],'Nama Hari'),
                   'leave_id'       : fields.many2one('outstanding.leave','Cuti'),
                   'holiday_id'     : fields.many2one('outstanding.holiday','Libur'),
                   }
work_day_holiday()

class hr_holidays(osv.osv):
    _inherit        = "hr.holidays"

    def _user_left_days(self, cr, uid, ids, name, args, context=None):
        res = {}
        if not context: context={}
        res = dict.fromkeys(ids, {'available_leave': 0.0, 'remaining_leave': 0.0})

        for employee in self.browse(cr, uid, ids, context=context):
            if employee:
                employee_id = employee.employee_id.id

                holidays_ids = self.search(cr,uid,[('employee_id','=',employee_id)])

                holidays_id = self.browse(cr,uid,holidays_ids)
                total_days = 0.0
                for i in holidays_id:
                    if i.type == 'add' and i.state == 'validate':
                        total_days += i.number_of_days_temp
                    elif i.type == 'remove' and i.state == 'validate':
                        total_days -= i.number_of_days_temp

                remaining = total_days - employee.number_of_days_temp
                res[employee.id] = { 'available_leave'  : total_days, 'remaining_leave' : remaining }
            else:
                res[employee.id] = { 'available_leave'  : 0.0, 'remaining_leave' : 0.0}
        return res


    _columns        = {
                       'holiday_type'   : fields.selection([('employee','By Employee')], 'Allocation Type', help='By Employee: Allocation/Request for individual Employee', required=True),
                       'available_leave': fields.function(_user_left_days, method=True, multi="all", store=True, type='float', string='Available Leave', digits=(16, 2)),
                       'remaining_leave': fields.function(_user_left_days, method=True, multi="all", store=True, type='float', string='Remaining Leave', digits=(16, 2)),
                       'employee_subs_id' : fields.many2one('hr.employee', 'Employee Substitute'),
                       #'remaining_leave': fields.float('Remaining Leave', method=True, multi="all", store=True, type='float', digits=(16, 2)),
                       #'available_leave': fields.float('Available Leave', method=True, multi="all", store=True, type='float', digits=(16, 2)),
                       }
    
    def holidays_validate(self, cr, uid, ids, *args):
        self.check_holidays(cr, uid, ids)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        holiday_id = self.search(cr, uid, [])[0]
        holiday = self.browse(cr, uid, holiday_id)
        if holiday.type == "add":
            status = "validate"
            self._send_mails(cr, uid, ids, status)
        return self.write(cr, uid, ids, {'state':'validate1', 'manager_id': manager})

    def holidays_validate2(self, cr, uid, ids, *args):
        self.check_holidays(cr, uid, ids)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate', 'manager_id2': manager})
        data_holiday = self.browse(cr, uid, ids)
        for record in data_holiday:
            if record.holiday_type == 'employee' and record.type == 'remove':
                meeting_obj = self.pool.get('crm.meeting')
                vals = {
                    'name': record.name,
                    'categ_id': record.holiday_status_id.categ_id.id,
                    'duration': record.number_of_days_temp * 8,
                    'note': record.notes,
                    'user_id': record.user_id.id,
                    'date': record.date_from,
                    'end_date': record.date_to,
                    'date_deadline': record.date_to,
                }
                case_id = meeting_obj.create(cr, uid, vals)
                self.write(cr, uid, ids, {'case_id': case_id})
            elif record.holiday_type == 'category':
                emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [record.category_id.id])])
                leave_ids = []
                for emp in obj_emp.browse(cr, uid, emp_ids):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=None))
                wf_service = netsvc.LocalService("workflow")
                for leave_id in leave_ids:
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
                    
        holiday_id = self.search(cr, uid, [])[0]
        holiday = self.browse(cr, uid, holiday_id)
        if holiday.type == "add":
            status = "validate"
            self._send_mails(cr, uid, ids, status)
        return True

    def holidays_confirm(self, cr, uid, ids, *args):
        self.check_holidays(cr, uid, ids)
        holiday_id = self.search(cr, uid, [])[0]
        holiday = self.browse(cr, uid, holiday_id)
        if holiday.type == "add":
            status = "confirm"
            self._send_mails(cr, uid, ids, status)
        return self.write(cr, uid, ids, {'state':'confirm'})


    # sending email for leave employee
    def _send_mails(self, cr, uid, ids, status):
            
        smtp = self.pool.get('email.smtpclient')
        smtpserver_id = self.pool.get('email.smtpclient').select(cr, uid, 'default')

        company_id = self.pool.get('res.company').search(cr, uid, [])[0]
        company = self.pool.get('res.company').browse(cr, uid, company_id)

        host = str(company.web_client or 'http://localhost:8070')

        if smtpserver_id:
            smtpserver_id = smtpserver_id
        else:
            raise osv.except_osv(_('Error'), _('No SMTP Server has been defined!'))
        
        name_employee = ""
        department = ""
        start_date  = ""
        end_date = ""
        subject = ""
        sendto = []
        attachments = []
        if status == "confirm":
            for m in self.browse(cr,uid,ids):
                # print "bbbbbbbbbbbbbbb", m.employee_subs_id.id

                if not m.department_id.manager_id.work_email:
                    raise osv.except_osv(_('Warning!'), _('Please Insert Work Email Manager!'))

                sendto.append(m.department_id.manager_id.work_email)
                name_employee = m.employee_id.name
                department = m.department_id.name
                start_date = datetime.strptime(m.date_from, '%Y-%m-%d %H:%M:%S').date()
                end_date = datetime.strptime(m.date_to, '%Y-%m-%d %H:%M:%S').date()
                subject = "pengajuan "+m.holiday_status_id.name+" - "+m.employee_id.name
                reason = m.name
                url         = str('%sopenerp/form/view?model=hr.holidays&id=%d&ids=[%d]&db=%s\n'% (host,m.id,m.id,cr.dbname))
                approve_manager = """
                <tr>
                    <td>Approve</td>
                    <td>:</td>
                    <td><a href='%s'>Approve</a></td>
                </tr>
                """% (url)

        elif status == "validate":
            for m in self.browse(cr,uid,ids):
                print "bbbbbbbbbbbbbbb", m.employee_subs_id.id

                if not m.employee_subs_id.work_email:
                    raise osv.except_osv(_('Warning!'), _('Please Insert Work Email Employee!'))

                sendto.append(m.employee_subs_id.work_email)
                name_employee = m.employee_id.name
                department = m.department_id.name
                start_date = datetime.strptime(m.date_from, '%Y-%m-%d %H:%M:%S').date()
                end_date = datetime.strptime(m.date_to, '%Y-%m-%d %H:%M:%S').date()
                subject = "pengajuan "+m.holiday_status_id.name+" - "+m.employee_id.name
                reason = m.name
                # url         = str('%sopenerp/form/view?model=hr.holidays&id=%d&ids=[%d]&db=%s\n'% (host,m.id,m.id,cr.dbname))
                # print "url------------------->>", url
                # href        = str('<a href=%s>Approve</a>')%  url
                approve_manager = """
                <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
                """
            print ">>>>>>>>>>>", sendto , "name", name_employee, "department", department, "start_date", start_date, "end_date", end_date
        
        body="""
<center><h2>PEMBERITAHUAN</h2></center><br><br>

Kepada Yth,
Bapak / Ibu sekalian<br><br>

Dengan ini diberitahukan:<br><br>

<table>
    <tr>
        <td width="100">Nama</td>
        <td>:</td>
        <td>%s</td>    
    </tr>
    <tr>
        <td>Departemen</td>
        <td>:</td>
        <td>%s</td>
    </tr>
    <tr>
        <td>Tanggal Cuti</td>
        <td>:</td>
        <td>%s Until %s</td>
    </tr>
    <tr>
        <td>Alasan Cuti</td>
        <td>:</td>
        <td>%s</td>
    </tr>
    %s
</table>
<br>

Demikian disampaikan, atas perhatiannya diucapkan terimakasih.<br><br>

<p align='right'><b><i><font color='red'>Open</font></i>ERP</b> HRMS System</p>
"""% (name_employee,department,start_date,end_date,reason,approve_manager)

        p = pooler.get_pool(cr.dbname)
        p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, sendto, subject, body, attachments)


    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        for a in (date_from,date_to):
            print a,type(a)
        result = {}
        if date_to and date_from:
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value'] = {
                'number_of_days_temp': round(diff_day)+1
            }
            return result
        result['value'] = {
            'number_of_days_temp': 0,
        }
        return result
    
    def write(self,cr,uid,ids,data,context=None):
        if 'date_to' in data.keys():
            holidays        = self.browse(cr,uid,ids[0])
            other_holidays  = self.search(cr,uid,[('employee_id','=',holidays.employee_id.id)])
            other_holidays.remove(ids[0])
            for others in self.browse(cr,uid,other_holidays):
                if data['date_to'] >= others.date_from and data['date_to'] <= others.date_to:
                    raise osv.except_osv(_('Overlap Date End'), _('Date End is overlap with the other leave !\n[%s - %s:\n%s - %s]') % (others.name, others.employee_id.name, others.date_from, others.date_to))
                if data['date_to']==False:
                    if others.date_to>time.strftime("%Y-%m-%d") or others.date_to==False:
                        raise osv.except_osv(_('Overlap Date End'), _('Date End is overlap with the other leave !\n[%s - %s:\n%s - %s]') % (others.name, others.employee_id.name, others.date_from, others.date_to))
        
        if 'date_from' in data.keys():
            holidays        = self.browse(cr,uid,ids[0])
            other_holidays  = self.search(cr,uid,[('employee_id','=',holidays.employee_id.id)])
            other_holidays.remove(ids[0])
            for others in self.browse(cr,uid,other_holidays):
                print others
                if data['date_from'] <= others.date_to and data['date_from'] >= others.date_from:
                    raise osv.except_osv(_('Overlap Date Start'), _('Date Start is overlap with the other leave !\n[%s - %s:\n%s - %s]') % (others.name, others.employee_id.name, others.date_from, others.date_to))
        return super(hr_holidays,self).write(cr,uid,ids,data,context=context)
    
    def create(self,cr,uid,data,context=None):
        #other_holidays  = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',data['employee_id'])])
	other_holidays  = self.pool.get('hr.holidays').search(cr,uid,[('employee_id','=',data['employee_id'])])
        #print "data=========================+>",data
        if 'date_to' in data:
            for others in self.browse(cr,uid,other_holidays):
                if data['date_to'] >= others.date_from and data['date_to'] <= others.date_to:
                    raise osv.except_osv(_('Overlap Date End'), _('Date End is overlap with the other leave !\n[%s - %s:\n%s - %s]') % (others.name, others.employee_id.name, others.date_from, others.date_to))
        else:
            for others in self.browse(cr,uid,other_holidays):
                if others.date_to>time.strftime("%Y-%m-%d") or others.date_to==False:
                    raise osv.except_osv(_('Overlap Date End'), _('Date End is overlap with the other leave !\n[%s - %s:\n%s - %s]') % (others.name, others.employee_id.name, others.date_from, others.date_to))
        
        if 'date_from' in data:
            #other_holidays  = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',data['employee_id'])])
	    other_holidays  = self.pool.get('hr.holidays').search(cr,uid,[('employee_id','=',data['employee_id'])])
            for others in self.browse(cr,uid,other_holidays):
                if data['date_from'] <= others.date_to and data['date_from'] >= others.date_from:
                    raise osv.except_osv(_('Overlap Date Start'), _('Date Start is overlap with the other leave !\n[%s - %s:\n%s - %s]') % (others.name, others.employee_id.name, others.date_from, others.date_to))

        return super(hr_holidays,self).create(cr,uid,data,context=context)
    
    def onchange_date_from_new(self, cr, uid, ids, date_to, date_from, employee_id):
        result = {}
        # res = {}
        if date_to and date_from:
            end = datetime.strptime(date_to,"%Y-%m-%d %H:%M:%S")
            start = datetime.strptime(date_from,"%Y-%m-%d %H:%M:%S")
            print "eeeeeeeeeeeeeeeend", start ,"aaaaaaaaaaa>>>>>>>>>", end
            dur = end - start
            dur = dur.days
            print "duuuuuuuuuuuuuuuuur", dur
            print "staaaaartb", start
            #=============================================================================================
            # Selama hari terakhir cuti adalah hari libur, MAJUKAN sampai bukan hari libur
            #=============================================================================================
            datelist = [ start + timedelta(days=x) for x in range(0,dur) ]
            libur = 0
            for date in datelist:
                foo=False
                while not foo:
                    if date.strftime("%u")=="6" or date.strftime("%u")=="7":
                        libur = libur+1
                        break
                    else:
                        foo=True
            end1=start+timedelta(dur-1)
            print "selisih", (dur+1)-libur
            
            # ===========================================================================================
            total_days = 0.0
            if employee_id:
                holidays_ids = self.search(cr,uid,[('employee_id','=',employee_id)])
                print "hiddddddddddddddddddddd", holidays_ids
                holidays_id = self.browse(cr,uid,holidays_ids)
                days = 0
                for i in holidays_id:
                    print "totaaaaaaaaaaaaaaa", i.number_of_days_temp, "----", i.type
                    if i.type == 'add' and i.state == 'validate':
                        days += i.number_of_days_temp
                    elif i.type == 'remove' and i.state == 'validate':
                        days -= i.number_of_days_temp
                print "======================aaaaaaaaaaaaaaa========================", days
                total_days = days
            print "======================aaaaaaaaaaaaaaa========================", total_days
            result['value'] = {
                'number_of_days_temp': (dur+1)-libur,
                'remaining_leave': total_days-((dur+1)-libur),
                'available_leave': total_days,
            }
            return result

        result['value'] = {
            'number_of_days_temp': 0,
            'remaining_leave': 0,
            'available_leave': 0,
        }
        return result

#     def onchange_start(self,cr,uid,ids,start,leave):
#         start0=start
# #        registered_holiday = self.pool.get('hr.holiday.year').search(cr,uid,[('year','=',start0[0:4])])
# #        holiday=[]
# #        for rhs in registered_holiday:
# #            rh = self.pool.get('hr.holiday.year').browse(cr,uid,rhs)
# #            rs_date = datetime.fromtimestamp(time.mktime(time.strptime(rh.date,"%Y-%m-%d")))
# #            holiday.append(rh.date)
#         print "staaaaart", start0
#         if not leave:
#             return True
#         if not start:
#             return True
#         if leave:
#             leave=self.pool.get('hr.holidays.status').browse(cr,uid,leave).name
#             dur=0
#             dur0=dur
#             val={}
#             if not start or dur==0:
#                 val={
#                      'return'   : False,
#                      'date_to'      : False,
#                      'number_of_days_temp' : 0,
#                      }
#                 return {'value':val}
#             if start:
                
#                 #===================================================================
#                 # Cuti naik haji, melahirkan dan keguguran
#                 #===================================================================
#                 if dur=='haji':
#                     val={
#                          # 'return'   : False,
#                          'date_to'  : False,
#                          'number_of_days_temp' : 0,
#                          }
#                     return {'value':val}
#                 elif dur=='m+3':
#                     start=datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
#                     year=start.year
#                     month=start.month+3
#                     day=start.day
#                     if month>12:
#                         year+=1
#                         month%=12
#                     if day>calendar.monthrange(year, month)[1]:
#                         day=calendar.monthrange(year, month)[1]
#                     back=datetime(year,month,day).date()
#                     end=back-timedelta(1)
#                     foo=False
#                     while not foo:
#                         if back.strftime("%u")=="6" or back.strftime("%u")=="7":
#                             back=back+timedelta(1)
#                         else:
#                             foo=True
#                     dur=back-start.date()
#                     val={
#                          # 'return'   : back.strftime("%d/%m/%Y %H:%M:%S"),
#                          'date_to'  : end.strftime("%d/%m/%Y %H:%M:%S"),
#                          'number_of_days_temp' : dur.days,
#                          }
#                     return {'value':val}
#                 elif dur=='m+1,5':
#                     start=datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
#                     year=start.year
#                     month=start.month+1
#                     day=start.day+15
#                     if month>12:
#                         year+=1
#                         month%=12
#                     if day>calendar.monthrange(year, month)[1]:
#                         day=calendar.monthrange(year, month)[1]
#                     back=datetime(year,month,day).date()
#                     end=back-timedelta(1)
#                     foo=False
#                     while not foo:
#                         if back.strftime("%u")=="6" or back.strftime("%u")=="7":
#                             back=back+timedelta(1)
#                         else:
#                             foo=True
#                     dur=end-start.date()
#                     val={
#                          # 'return'   : back.strftime("%d/%m/%Y %H:%M:%S"),
#                          'date_to'  : end.strftime("%d/%m/%Y %H:%M:%S"),
#                          'number_of_days_temp' : dur.days,
#                          }
#                     return {'value':val}
                
#                 start=datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
#                 print "staaaaartb", start
#                 #=============================================================================================
#                 # Menentukan tanggal kapan cuti karyawan berakhir
#                 #=============================================================================================
#                 datelist = [ start + timedelta(days=x) for x in range(0,dur) ]
#                 print "dateeeeeeeeeeeeeeelist",datelist
#                 for date in datelist:
#                     foo=False
#                     while not foo:
#                         if date.strftime("%u")=="6" or date.strftime("%u")=="7":
#                             dur=dur+1
#                             break
#                         else:
#                             foo=True
#                 end1=start+timedelta(dur-1)
                
#                 #=============================================================================================
#                 # Selama hari terakhir cuti adalah hari libur, MAJUKAN sampai bukan hari libur
#                 #=============================================================================================
#                 foo=False
#                 while not foo:
#                     if end1.strftime("%u")=="6" or end1.strftime("%u")=="7":
#                         end1=end1+timedelta(1)
#                     else:
#                         foo=True
#                 print "eeeeeeeeeeeeeeeeend",end1
#                 #=============================================================================================
#                 # Menentukan kapan karyawan seharusnya kembali masuk kerja
#                 #=============================================================================================
#                 end=end1+timedelta(1)
#                 foo=False
#                 while not foo:
#                     if end.strftime("%u")=="6" or end.strftime("%u")=="7":
#                         end=end+timedelta(1)
#                     else:
#                         foo=True
#                 val={
#                      # 'return'   : end.strftime("%d/%m/%Y %H:%M:%S"),
#                      'date_to'  : end1.strftime("%d/%m/%Y %H:%M:%S"),
#                      'number_of_days_temp' : dur0,
#                      }
#         return {'value':val}
    
hr_holidays()


