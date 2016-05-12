from osv import osv,fields
from tools.translate import _
import calendar
import time
import datetime
from datetime import datetime,timedelta



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
                   # 'holiday_id'     : fields.many2one('outstanding.holiday','Libur'),
                   }
work_day_holiday()

class hr_holidays(osv.osv):
    _inherit        = "hr.holidays"
    
    _columns        = {
                       'holiday_type'   : fields.selection([('employee','By Employee')], 'Allocation Type', help='By Employee: Allocation/Request for individual Employee', required=True),
                       }
    
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
    def onchange_start(self,cr,uid,ids,start,leave):
        start0=start
#        registered_holiday = self.pool.get('hr.holiday.year').search(cr,uid,[('year','=',start0[0:4])])
#        holiday=[]
#        for rhs in registered_holiday:
#            rh = self.pool.get('hr.holiday.year').browse(cr,uid,rhs)
#            rs_date = datetime.fromtimestamp(time.mktime(time.strptime(rh.date,"%Y-%m-%d")))
#            holiday.append(rh.date)
        if not leave:
            return True
        if not start:
            return True
        if leave:
            leave=self.pool.get('hr.holidays.status').browse(cr,uid,leave).name
            dur=0
            dur0=dur
            val={}
            if not start or dur==0:
                val={
#                     'return'   : False,
                     'date_to'      : False,
                     'number_of_days_temp' : 0,
                     }
                return {'value':val}
            if start:
                
                #===================================================================
                # Cuti naik haji, melahirkan dan keguguran
                #===================================================================
                if dur=='haji':
                    val={
#                         'return'   : False,
                         'date_to'  : False,
                         'number_of_days_temp' : 0,
                         }
                    return {'value':val}
                elif dur=='m+3':
                    start=datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
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
                        if back.strftime("%u")=="6" or back.strftime("%u")=="7":
                            back=back+timedelta(1)
                        else:
                            foo=True
                    dur=back-start.date()
                    val={
#                         'return'   : back.strftime("%d/%m/%Y %H:%M:%S"),
                         'date_to'  : end.strftime("%d/%m/%Y %H:%M:%S"),
                         'number_of_days_temp' : dur.days,
                         }
                    return {'value':val}
                elif dur=='m+1,5':
                    start=datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
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
                        if back.strftime("%u")=="6" or back.strftime("%u")=="7":
                            back=back+timedelta(1)
                        else:
                            foo=True
                    dur=end-start.date()
                    val={
#                         'return'   : back.strftime("%d/%m/%Y %H:%M:%S"),
                         'date_to'  : end.strftime("%d/%m/%Y %H:%M:%S"),
                         'number_of_days_temp' : dur.days,
                         }
                    return {'value':val}
                
                start=datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
                
                #=============================================================================================
                # Menentukan tanggal kapan cuti karyawan berakhir
                #=============================================================================================
                datelist = [ start + timedelta(days=x) for x in range(0,dur) ]
                for date in datelist:
                    foo=False
                    while not foo:
                        if date.strftime("%u")=="6" or date.strftime("%u")=="7":
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
                    if end1.strftime("%u")=="6" or end1.strftime("%u")=="7":
                        end1=end1+timedelta(1)
                    else:
                        foo=True
                
                #=============================================================================================
                # Menentukan kapan karyawan seharusnya kembali masuk kerja
                #=============================================================================================
                end=end1+timedelta(1)
                foo=False
                while not foo:
                    if end.strftime("%u")=="6" or end.strftime("%u")=="7":
                        end=end+timedelta(1)
                    else:
                        foo=True
                val={
#                     'return'   : end.strftime("%d/%m/%Y %H:%M:%S"),
                     'date_to'  : end1.strftime("%d/%m/%Y %H:%M:%S"),
                     'number_of_days_temp' : dur0,
                     }
        return {'value':val}
hr_holidays()

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
        registered_holiday = self.pool.get('hr.holiday.year').search(cr,uid,[('year','=',start0[0:4])])
        holiday=[]
        for rhs in registered_holiday:
            rh = self.pool.get('hr.holiday.year').browse(cr,uid,rhs)
            rs_date = datetime.fromtimestamp(time.mktime(time.strptime(rh.date,"%Y-%m-%d")))
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
                
                #=============================================================================================
                # Menentukan tanggal kapan cuti karyawan berakhir
                #=============================================================================================
                datelist = [ start + timedelta(days=x) for x in range(0,dur) ]
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
                   'start'          : fields.date('Dari'),
                   'end'            : fields.date('Sampai'),
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


