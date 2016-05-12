from osv import osv,fields
import decimal_precision as dp
from tools.translate import _
from datetime import datetime
from datetime import date
import tools
import time

class hr_overtime(osv.osv):
    _name = "hr.overtime"
    
    def _get_total(self, cr, uid, ids, field_names, arg, context=None):
        vals={}
        duration=0
        paid=0
        for ot in self.browse(cr,uid,ids):
            line_ids    = self.pool.get('overtime.lines').search(cr,uid,[('name','=',ids[0])])
            for line in self.pool.get('overtime.lines').browse(cr,uid,line_ids):
                duration    +=line.duration
                paid        +=line.paid
        vals[ot.id] = {
                       'total_dur'  : duration,
                       'total_paid' : paid
                       }
        return vals
    
    _columns = {
        'name'      : fields.many2one('hr.employee','Employee Name',required=True,domain=['|',('type','=','bsp'),('status','=','outsource'),('current_job_level.job_level','in',(1,2,3,4,5,6))]),
        'department': fields.many2one('hr.department','Department'),
        'manager'   : fields.many2one('hr.employee','Manager'),
        'date'      : fields.date('Date'),
        'state'     : fields.selection([('draft','Draft'),
                                        ('proposed','Proposed - Waiting for Approval'),
                                        ('approved','Approved'),
                                        ('done','Done')],'State',readonly=True),
        'note'      : fields.char('Note', size=84),
        'periode'   : fields.many2one('account.period', 'Periode', states={'new': [('readonly', False)]}),
        #'periode'   : fields.char('Periode', size=32, readonly=True, states={'new': [('readonly', False)]}),
        'line_ids'  : fields.one2many('overtime.lines','name','Overtime Lines'),
        "total_dur" : fields.function(_get_total,method=True,store=True,multi='ot',string="Total Hour", type='float'),
        "total_paid": fields.function(_get_total,method=True,store=True,multi='ot',string="Total Paid", type='float'),
        "contract_id":fields.many2one('hr.contract','Contract No')
    }
    _defaults = {
         'state'    : 'draft',
         'date'     : time.strftime('%Y-%m-%d'),
     }
    
    def onchange_employee(self,cr,uid,ids,data):
        val={}
        if data:
            employee=self.pool.get('hr.employee').browse(cr,uid,data)
            print employee,data
            if employee.department_id:
                val['department']=employee.department_id.id
                val['manager']=employee.department_id.manager_id.id
            contract_ids=self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',data),'|',('date_end','>=',time.strftime("%Y-%m-%d")),('date_end','=',False)])
            if contract_ids:
                val['contract_id']=contract_ids[0]
            
        return {'value':val}
    
    def button_proposed(self, cr, uid, ids, context={}):
        period_pool = self.pool.get('account.period')
        for chk in self.browse(cr, uid, ids):
            ttyme = datetime.fromtimestamp(time.mktime(time.strptime(chk.date,"%Y-%m-%d")))
            pids = period_pool.find(cr, uid, chk.date, context)
            record = {
              'state'       : 'proposed',
              'periode'     : pids and pids[0],#tools.ustr(ttyme.strftime('%B %Y')),
              }
            chk.write(record)
        return True
    
    def button_approved(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"approved"})
        return True
    
    def button_draft(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"draft"})
        return True
    
    def button_cancel(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"cancelled"})
        return True

    def button_done(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"done"})
        return True
    
hr_overtime()

class overitme_lines(osv.osv):
    _name       = 'overtime.lines'
    def onchange_time_start(self,cr,uid,ids,start,end):
        val={}
        if start:
            mulai   = datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
            if end:
                selesai = datetime.strptime(end,"%Y-%m-%d %H:%M:%S")
                diff    = selesai - mulai
                diff_minute = (diff.seconds/60)%60
                diff_hour   = int((diff.seconds/60)/60)
                if diff_minute <= 15:
                    diff_hour += 0
                elif diff_minute >= 30 and diff_minute < 45:
                    diff_hour += 0.5
                elif diff_minute >= 45:
                    diff_hour+=1
                val['duration']=diff_hour
        return {'value':val}
    
    def _calculate_duration(self, cr, uid, ids, field_names, arg, context=None):
        res={}
        record={}
        for rs in self.browse(cr, uid, ids, context=context):
            #print rs,"******************8"
            if rs.time_start:
                mulai       = datetime.strptime(rs.time_start,"%Y-%m-%d %H:%M:%S")
                
                #periode     = mulai.strftime('%b %Y')
                #record['periode']=periode
                
                d_mulai     = mulai.strftime('%Y-%m-%d')
                dayofweek   = mulai.strftime('%A')
                year        = mulai.strftime('%Y')
                if dayofweek=='Senin' or dayofweek=='Monday':
                    dayofweek='0'
                elif dayofweek=='Selasa' or dayofweek=='Tuesday':
                    dayofweek='1'
                elif dayofweek=='Rabu' or dayofweek=='Wednesday':
                    dayofweek='2'
                elif dayofweek=='Kamis' or dayofweek=='Thursday':
                    dayofweek='3'
                elif dayofweek=='Jumat' or dayofweek=='Friday':
                    dayofweek='4'
#                elif dayofweek=='Sabtu' or dayofweek=='Saturday':
#                    dayofweek='5'
#                elif dayofweek=='Minggu' or dayofweek=='Sunday':
#                    dayofweek='6'
                #print "dayofweek",dayofweek
                registered_holiday = self.pool.get('hr.holiday.year').search(cr,uid,[('year','=',str(year))])
                holiday=[]
                for rhs in registered_holiday:
                    rh = self.pool.get('hr.holiday.year').browse(cr,uid,rhs)
                    rs_date = datetime.strptime(rh.date,"%Y-%m-%d")
                    holiday.append(rh.date)
                
                if rs.time_end:
                    selesai = datetime.strptime(rs.time_end,"%Y-%m-%d %H:%M:%S")
                    diff    = selesai - mulai
                    diff_minute = (diff.seconds/60)%60
                    diff_hour   = int((diff.seconds/60)/60)
                    #print "diff_minute",diff_minute,diff_hour
                    if diff_minute <= 15:
                        diff_hour += 0
                    elif diff_minute >= 30 and diff_minute < 45:
                        diff_hour += 0.5
                    elif diff_minute >= 45:
                        diff_hour+=1
                    record['duration']=diff_hour
                    if diff_hour>0:
                        
                        contract=self.pool.get('hr.contract').search(cr,uid,[('id','=',rs.name.name.contract_id.id)])
                        if len(contract)==0:
                            raise osv.except_osv(_('No Contract'), _('You must define Contract for this employee'))
                        contract=self.pool.get('hr.contract').browse(cr,uid,contract[0])
                        if not contract.working_hours:
                            raise osv.except_osv(_('No Working Schedule'), _('You must define Working Schedule for this employee\'s contract'))
                        weekdayindex=[]
                        for wtime in contract.working_hours.attendance_ids:
                            weekdayindex.append(wtime.dayofweek)
                        if dayofweek in weekdayindex and d_mulai not in holiday:
                            #print "if"
                            if rs.manual and not rs.libur:
                                paid=1.5*rs.x1_5#((diff_hour-1)*2)
                                record['paid']=(1.5*rs.x1_5)+(2.0*rs.x2_0) 
                            else:
                                paid=1.5+((diff_hour-1)*2)
                                record['paid']=1.5+(diff_hour-1)*2
                        else:
                            working_day = len(contract.working_hours.attendance_ids)
                            #print "else",working_day
                            if rs.manual and rs.libur:
                                paid=(2.0*rs.x2)+(3.0*rs.x3)+(4.0*rs.x4)
                            else:
                                if working_day == 5:            #Jika karyawan bekerja 5 hari seminggu 
                                    if diff_hour<=8:            ##Jika lemburnya sampai 8 jam, hitungannya 2x
                                        paid=2*diff_hour
                                    elif diff_hour==9:          ##Jika lemburnya 9 jam, hitungannya = 19 jam
                                        paid=19
                                    else:
                                        paid=19+(diff_hour-9)*4 ##Jika lemburnya di atas 9 jam, hitungannya = 19+4xsisa
                                    #print "xxxx",paid
                                elif working_day == 6:          #Jika karyawan bekerja 6 hari seminggu
                                    if diff_hour<=7:            ##Jika lemburnya sampai 7 jam, hitungannya 2x
                                        paid=2*diff_hour
                                    elif diff_hour==8:          ##Jika lemburnya 8 jam, hitungannya = 17 jam
                                        paid=17
                                    else:
                                        paid=17+(diff_hour-8)*4 ##Jika lemburnya di atas 8 jam, hitungannya = 17+4xsisa
                                
                            record['paid']=paid
        res[rs.id]=record
        return res
    
    _columns    = {
                   'name'       : fields.many2one('hr.overtime','ID'),
                   'time_start' : fields.datetime('Time Start',required=True),
                   'time_end'   : fields.datetime('Time End',required=True),
                   'manual'     : fields.boolean('Manual', help='Checklist untuk perhitungan manual'),
                   'libur'      : fields.boolean('Libur?', help='Checklist untuk hari libur'),
                   'x1_5'       : fields.float('1,5x Hari Kerja', digits_compute=dp.get_precision('Sale Price')),
                   'x2_0'         : fields.float('2,0x Hari Kerja', digits_compute=dp.get_precision('Sale Price')),
                   'x2'         : fields.float('2,0x Hari Libur', digits_compute=dp.get_precision('Sale Price')),
                   'x3'         : fields.float('3,0x Hari Libur', digits_compute=dp.get_precision('Sale Price')),
                   'x4'         : fields.float('4,0x Hari Libur', digits_compute=dp.get_precision('Sale Price')),
                   'note'       : fields.text('Note'),
                   'duration'   : fields.function(_calculate_duration, method=True, store=True, multi='dc', string='Duration (hours)', digits_compute=dp.get_precision('Sale Price'),help="Overtime duration (hours)"),
                   'paid'       : fields.function(_calculate_duration, method=True, store=True, multi='dc', string='Paid (hours)', digits_compute=dp.get_precision('Sale Price'),help="Paid overtime duration, according to Indonesian Labor Laws 2004 (hours)"),
                   }
overitme_lines()