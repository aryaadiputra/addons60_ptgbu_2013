import time
import datetime
from dateutil.relativedelta import relativedelta
import base64, urllib
from osv import osv, fields
import decimal_precision as dp
import pooler
from tools.translate import _

class rosters_schedule_line(osv.osv):
    _name = 'rosters.schedule.line'
    _columns = {
#             'line_id':fields.integer('ID'),
            'start_work_date':fields.date("Start Working Date", required=True),
            'end_work_date':fields.date("End Working Date", required=True),
            'roster_id': fields.many2one("rosters.schedule", 'Roster Schedule'),
            'status_depart' : fields.selection([('ready','Ready'),('not_ready','Not Ready')], 'States Depart'),
            'status_arrival' : fields.selection([('ready','Ready'),('not_ready','Not Ready')], 'States Arrival'),
            'start_holiday_date':fields.date("Start Holidays Date", required=True),
            'end_holiday_date':fields.date("End Holidays Date", required=True),

            'start_work_date_extends':fields.date("Start Working Date Extends", required=False),
            'end_work_date_extends':fields.date("End Working Date Extends", required=False),
            'start_holiday_date_extends':fields.date("Start Holidays Date Extends", required=False),
            'end_holiday_date_extends':fields.date("End Holidays Date Extends", required=False),
            'status_extends': fields.selection([('draft','Draft'),('waiting','Waiting'),('confirm','Confirm')], 'States Depart'),

            'roster_history_ids' : fields.one2many('rosters.history', 'roster_schedule_id', 'Rosters History'),
            }
    
    def generate_ticket(self, cr, uid, ids, context=None):
        date_today = time.strftime('%Y-%m-%d')
        month = (datetime.datetime.strptime(date_today, '%Y-%m-%d').month)+1
        cr.execute('SELECT rscl.id, rsc.employee, rsc.department_id, rscl.start_work_date, rscl.status_depart FROM rosters_schedule_line rscl join rosters_schedule rsc on rscl.roster_id = rsc.id where EXTRACT(month FROM rscl.start_work_date)::text=%s AND rscl.status_depart=%s',(str(month),'not_ready'))
        depart = cr.dictfetchall()
        # cr.execute('SELECT id, start_work_date FROM rosters_schedule_line WHERE EXTRACT(month FROM start_work_date)::text=%s and status_depart=%s',(str(month),'not_ready'))
        # depart = cr.dictfetchall()
        for d in depart:
            print "aaaaaaaaaaaaaaaaaaaa", d['id'], "employee_id", d['employee'], "department_id", d['department_id']
            value_hr_travel = {
                    'journal_id' : '1',
                    'description' : 'departure',
                    'name' : 'departure',
                    'employee_id': d['employee'],
                    'account_id' : '1',
                    'reserve_date': d['start_work_date'],
                    'request_date': date_today,
                    'department_id': d['department_id'],
                    'currency_id': '12',
                    'date_due': date_today,
#                     'partner_id' : '1',
#                     'address_invoice_id': '1',
#                     'date_invoice': datetime.date.today(),
                     }
            hr_travel_id = self.pool.get('hr.travel').create(cr,uid,value_hr_travel,context=context);
            
            value_hr_travel_line = {
                                    'name' : 'departure',
                                    'account_id' : '1',
                                    'account_analytic_id' : False,
                                    'origin': 'departure',
                                    'price_unit': '0',
                                    'quantity' : '1',
                                    'invoice_line_tax_id' : False,
                                    'travel_id' : hr_travel_id,
                                    }
            self.pool.get('hr.travel.line').create(cr,uid,value_hr_travel_line,context=context);
            
            val = {
                   'status_depart': 'ready',
                    }
            self.write(cr,uid,d['id'],val,context=context);

        cr.execute('SELECT rscl.id, rsc.employee, rsc.department_id, rscl.start_work_date, rscl.status_arrival FROM rosters_schedule_line rscl join rosters_schedule rsc on rscl.roster_id = rsc.id where EXTRACT(month FROM rscl.start_holiday_date)::text=%s AND rscl.status_arrival=%s',(str(month),'not_ready'))
        # cr.execute('SELECT id, start_holiday_date FROM rosters_schedule_line WHERE EXTRACT(month FROM start_holiday_date)::text=%s and status_depart=%s',(str(month),'not_ready'))
        arrival = cr.dictfetchall()
        for a in arrival:
            print "aaaaaaaaaaaaaaaaaaaa", a['id'], "employee_id", a['employee'], "department_id", a['department_id']
            value_hr_travel = {
                    'journal_id' : '1',
                    'description' : 'arrival',
                    'name' : 'arrival',
                    'employee_id': a['employee'],
                    'account_id' : '1',
                    'reserve_date': a['start_work_date'],
                    'request_date': date_today,
                    'department_id': a['department_id'],
                    'currency_id': '12',
                    'date_due': date_today,
#                     'partner_id' : '1',
#                     'address_invoice_id': '1',
#                     'date_invoice': datetime.date.today(),
                     }
            hr_travel_id = self.pool.get('hr.travel').create(cr,uid,value_hr_travel,context=context);
            
            value_hr_travel_line = {
                                    'name' : 'arrival',
                                    'account_id' : '1',
                                    'account_analytic_id' : False,
                                    'origin': 'arrival',
                                    'price_unit': '0',
                                    'quantity' : '1',
                                    'invoice_line_tax_id' : False,
                                    'travel_id' : hr_travel_id,
                                    }
            self.pool.get('hr.travel.line').create(cr,uid,value_hr_travel_line,context=context);
            val = {
                   'status_arrival': 'ready',
                    }
            self.write(cr,uid,a['id'],val,context=context);

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
            for m in self.browse(cr, uid, ids):
                r = self.pool.get('rosters.schedule').browse(cr, uid, m.roster_id.id)

                if r.department_id.manager_id.work_email == False or r.employee.work_email == False:
                    raise osv.except_osv(_('Warning!'), _('Please Insert Work Email Employee Or Manager!'))
        
                sendto.append(r.department_id.manager_id.work_email)
                sendto.append(r.employee.work_email)
                name_employee = r.employee.name

                start_work_date_extends = str(m.start_work_date_extends)
                end_work_date_extends = str(m.end_work_date_extends)
                start_holiday_date_extends = str(m.start_holiday_date_extends)
                end_holiday_date_extends = str(m.end_holiday_date_extends)

                start_work_date = str(m.start_work_date)
                end_work_date = str(m.start_work_date)
                start_holiday_date = str(m.start_holiday_date)
                end_holiday_date = str(m.end_holiday_date)


                department = r.department_id.name
                subject = "Pengajuan Extends - "+r.employee.name
                url  = str('%sopenerp/form/view?model=hr.holidays&id=%d&ids=[%d]&db=%s\n'% (host,r.id,r.id,cr.dbname))
                approve_manager = """
                <tr>
                    <td>Approve</td>
                    <td>:</td>
                    <td><a href='%s'>Approve</a></td>
                </tr>
                """% (url)
        
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
</table>
<table border="1">
    <tr>
        <td>Schedule</td>
        <td>current schedule</td>
        <td>extends schedule</td>
    </tr>
    <tr>
        <td>Start Working Date</td>
        <td>%s</td>
        <td>%s</td>
    </tr>
    <tr>
        <td>End Working Date</td>
        <td>%s</td>
        <td>%s</td>
    </tr>
    <tr>
        <td>Start Holidays Date</td>
        <td>%s</td>
        <td>%s</td>
    </tr>
    <tr>
        <td>End Holidays Date</td>
        <td>%s</td>
        <td>%s</td>
    </tr>
</table>
<table>
    %s
</table>
<br>

Demikian disampaikan, atas perhatiannya diucapkan terimakasih.<br><br>

<p align='right'><b><i><font color='red'>Open</font></i>ERP</b> HRMS System</p>
"""% (name_employee,department,start_work_date,start_work_date_extends,end_work_date,end_work_date_extends,start_holiday_date,start_holiday_date_extends,end_holiday_date,end_holiday_date_extends,approve_manager)
        
        p = pooler.get_pool(cr.dbname)
        p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, sendto, subject, body, attachments)

    def confirm_extends(self, cr, uid, ids, context=None):
        data_ext = self.browse(cr, uid, ids, context=context)
        for r in data_ext:
            # roster1 = self.pool.get('rosters.schedule').browse(cr, uid, r.roster_id.id, context=context)
        
            data_extends = {
                        'start_work_date' : r.start_work_date_extends,
                        'end_work_date' : r.end_work_date_extends,
                        'start_holiday_date' : r.start_holiday_date_extends,
                        'end_holiday_date': r.end_holiday_date_extends,
                        'status_extends': 'confirm',
                         }
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",r.start_work_date
            first_data = {
                        'start_work_date_history': r.start_work_date,
                        'end_work_date_history': r.end_work_date,
                        'start_holiday_date_history': r.start_holiday_date,
                        'end_holiday_date_history': r.end_holiday_date,
                        'roster_schedule_id' : r.id,
            }

        self.write(cr,uid,ids,data_extends)
        self.pool.get('rosters.history').create(cr,uid,first_data)

    def ask_extends(self, cr, uid, ids, context=None):
        status = "confirm"
        self._send_mails(cr, uid, ids, status)
        return self.write(cr, uid, ids,  {'status_extends': 'waiting'})

    def depart(self, cr, uid, ids, context=None):
#         print "aaaaaaaaaaaaaaaaaaaaaaaaaaa",ids
        rosline_id = self.browse(cr, uid, ids, context=context)
#         print "bbbbbbbbbbbbbbbbbbbbbbbb",rosline_id.roster_id
        for a in rosline_id:
            print "zzzzzzzzzzzzzzzzzzzzzzzzzz",a.roster_id, a.roster_id.id
#             rosline = self.pool.get('rosters.schedule').search(cr, uid, [('id','=',a.roster_id)], context)
            roster1 = self.pool.get('rosters.schedule').browse(cr, uid, a.roster_id.id, context=context)
            print "cccccccccccccccccccccccccccc",roster1.employee
            print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",roster1.start_work_date, "aaaaaaaaaaa", roster1.department_id
#         idsros = self.pool.get('rosters.schedule').search(cr, uid, [('line_ids', '=', rosline.id)], context)
        
#             for roster in roster1:
            
            value_hr_travel = {
                    'journal_id' : '1',
                    'description' : 'departure',
                    'name' : 'departure',
                    'employee_id': roster1.employee.id,
#                     'partner_id' : '1',
#                     'address_invoice_id': '1',
                    'account_id' : '1',
#                     'date_invoice': datetime.date.today(),
                    'reserve_date': a.start_work_date,
                    'request_date': datetime.date.today(),
                    'department_id': roster1.department_id.id,
                    'currency_id': '12',
                    'date_due': datetime.date.today(),
                     }
            hr_travel_id = self.pool.get('hr.travel').create(cr,uid,value_hr_travel,context=context);
            
            value_hr_travel_line = {
                                    'name' : 'departure',
                                    'account_id' : '1',
                                    'account_analytic_id' : False,
                                    'origin': 'departure',
                                    'price_unit': '0',
                                    'quantity' : '1',
                                    'invoice_line_tax_id' : False,
                                    'travel_id' : hr_travel_id,
                                    }
            self.pool.get('hr.travel.line').create(cr,uid,value_hr_travel_line,context=context);
            
        val = {
               'status_depart': 'ready',
                }
        self.write(cr,uid,ids,val,context=context);
        
            
    def arrival(self, cr, uid, ids, context=None):
        rosline_id = self.browse(cr, uid, ids, context=context)
        for a in rosline_id:
            roster1 = self.pool.get('rosters.schedule').browse(cr, uid, a.roster_id.id, context=context)
            
            value_hr_travel = {
                    'journal_id' : '1',
                    'description' : 'arrival',
                    'name' : 'arrival',
                    'employee_id': roster1.employee.id,
#                     'partner_id' : '1',
#                     'address_invoice_id': '1',
                    'account_id' : '1',
#                     'date_invoice': datetime.date.today(),
                    'reserve_date': a.start_holiday_date,
                    'request_date': datetime.date.today(),
                    'department_id': roster1.department_id.id,
                    'currency_id': '12',
                    'date_due': datetime.date.today(),
                     }
            hr_travel_id = self.pool.get('hr.travel').create(cr,uid,value_hr_travel,context=context);
            
            value_hr_travel_line = {
                                    'name' : 'arrival',
                                    'account_id' : '1',
                                    'account_analytic_id' : False,
                                    'origin': 'departure',
                                    'price_unit': '0',
                                    'quantity' : '1',
                                    'invoice_line_tax_id' : False,
                                    'travel_id' : hr_travel_id,
                                    }
            self.pool.get('hr.travel.line').create(cr,uid,value_hr_travel_line,context=context);
            
        val = {
               'status_arrival': 'ready',
                }
        self.write(cr,uid,ids,val,context=context);

    _defaults = {
            'status_depart': 'not_ready',
            'status_arrival': 'not_ready',
            'status_extends': 'draft',
                }

rosters_schedule_line()

class rosters_schedule(osv.osv):
    _name = 'rosters.schedule'

    def compute(self, cr, uid, ids, context={}):
        print"COMPUTE", ids
        
        obj_rosters = self.pool.get('rosters.schedule')
        obj_rosters_type = self.pool.get('rosters.schedule.type')
        
        tes = obj_rosters.search(cr,uid,[('id','=',ids)])
        hasil = obj_rosters.browse(cr,uid, tes)
        
#        rosters_type = obj_rosters_type.search(cr, uid, [])
#        rosters_type_id = obj_rosters_type.browse(cr, uid, rosters_type)
#        
#        for x in rosters_type_id:
#            print "ID : ", x.id
        
        for check in hasil:
            print "tes", check.type
            
            check_id = check.id
            check_work_type = check.type.working_time
            check_leave_type = check.type.leave_time
            
            work_time_week = (check_work_type * 7) - 1
            leave_time_week = work_time_week + (check_leave_type * 7)
            
            total_week_in_period = check_work_type + check_leave_type
            
            print "INI TYPE", work_time_week
            print "INI TYPE2", leave_time_week
            
            obj_rosters_line = self.pool.get('rosters.schedule.line')
            old_rosters_line_ids = obj_rosters_line.search(cr, uid, [('roster_id', '=', check.id),])
             
            if old_rosters_line_ids:
                 print "ADA"
                 obj_rosters_line.unlink(cr, uid, old_rosters_line_ids, context=context)
           
        get_field = self.browse(cr,uid,ids)
        value = []
        for get in get_field:
            start_date = get['start_work_date']
            
            date1   = time.strptime(start_date,"%Y-%m-%d")
            print"1", date1
            date11  = time.strftime("%Y%m%d",date1)
            print"2", date11
            year    = int(date11[:4])
            month   = int(date11[4:6])
            day     = int(date11[6:])
            date111 = datetime.datetime(year, month, day)
            
            
         
                
            end_date = get['end_work_date']
            
            date2   = time.strptime(end_date,"%Y-%m-%d")
            date22  = time.strftime("%Y%m%d",date2)
            year    = int(date22[:4])
            month   = int(date22[4:6])
            day     = int(date22[6:])
            date222 = datetime.datetime(year, month, day, 0, 0, 0)
            
            diff = date222 - date111
            
            diffDay = int(diff.days) + 1
            print "HARIAN", diffDay
            
            week = int(diffDay) / 7
            #print "WEEEEEEEEEEEEEEEEEEEEEEEEEK", week
#            =======================================================
            period = int(week / total_week_in_period)
            
            rest_of_the_day = diffDay - (period * (leave_time_week + 1))
            print "HARIAN", rest_of_the_day
            rest_of_the_week = int(rest_of_the_day / 7)
            print "WEEK", rest_of_the_week
            
            rest_of_the_day = rest_of_the_day - (rest_of_the_week * 7)
            
            if rest_of_the_week > 1:
                week = "Weeks"
            else:
                week = "Week"
            
            if rest_of_the_day > 1:
                day = "Days"
            else:
                day = "Day"
            
            
            if rest_of_the_week == 0 and rest_of_the_day == 0:
                rest_of_the_day = "No Rest of The day Number"
            elif rest_of_the_week == 0:
                rest_of_the_day = "%d %s" %(rest_of_the_day, day)
            elif rest_of_the_day == 0:
                rest_of_the_day = "%d %s" %(rest_of_the_week, week)
            else:
                rest_of_the_day = "%d %s & %d %s" %(rest_of_the_week, week, rest_of_the_day, day)
            
            print "WEEK", rest_of_the_week
            print "DAYS", rest_of_the_day
            print "SISA HARI : ", rest_of_the_day
            
            print "++++++++++",period
            for hr in range(0,period):
                wkt_kerja = date111 + datetime.timedelta (days = work_time_week)
                wkt_libur = date111 + datetime.timedelta (days = leave_time_week)
                
                start_kerja = date111
                
                print "MULAI KERJA DARI", start_kerja
                
                print "MULAI KERJA S/D", wkt_kerja
                
                start_libur = wkt_kerja + datetime.timedelta (days = 1)
                
                print "MULAI LIBUR DARI", start_libur
                
                print "MULAI LIBUR S/D", wkt_libur
                print "==================================================================================="
                
                tes = self.pool.get('rosters.schedule').search(cr,uid,[('id','=',ids)])
                hasil = self.pool.get('rosters.schedule').browse(cr,uid, tes)
               
                for id in hasil:
                    
                    print "rtrtrtrtrt", id.id
                    
                    
                    obj_rosters_line.create(cr, uid, {
                                                'roster_id' : id.id,
                                                'start_work_date' : start_kerja,
                                                'end_work_date' : wkt_kerja,
                                                'start_holiday_date' : start_libur,
                                                'end_holiday_date' : wkt_libur,
                                                })
                    obj_rosters.write(cr, uid, [id.id], {
                                                'rest_of_the_day' : rest_of_the_day,
                                                
                                                })
                    
                date111 = wkt_libur
                
                date111 = date111 + datetime.timedelta (days = 1)

        return True
    
    def button_draft(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"draft"})
        return True
    
    def button_confirm(self, cr, uid, ids, context={}):
#        ===================================================================================        
        print"COMPUTE", ids
        
        obj_rosters = self.pool.get('rosters.schedule')
        obj_rosters_type = self.pool.get('rosters.schedule.type')
        
        tes = obj_rosters.search(cr,uid,[('id','=',ids)])
        hasil = obj_rosters.browse(cr,uid, tes)
        
#        rosters_type = obj_rosters_type.search(cr, uid, [])
#        rosters_type_id = obj_rosters_type.browse(cr, uid, rosters_type)
#        
#        for x in rosters_type_id:
#            print "ID : ", x.id
        
        for check in hasil:
            print "tes", check.type
            
            check_id = check.id
            check_work_type = check.type.working_time
            check_leave_type = check.type.leave_time
            
            work_time_week = (check_work_type * 7) - 1
            leave_time_week = work_time_week + (check_leave_type * 7)
            
            total_week_in_period = check_work_type + check_leave_type
            
            print "INI TYPE", work_time_week
            print "INI TYPE2", leave_time_week
            
            obj_rosters_line = self.pool.get('rosters.schedule.line')
            old_rosters_line_ids = obj_rosters_line.search(cr, uid, [('roster_id', '=', check.id),])
             
            if old_rosters_line_ids:
                 print "ADA"
                 obj_rosters_line.unlink(cr, uid, old_rosters_line_ids, context=context)
           
        get_field = self.browse(cr,uid,ids)
        value = []
        for get in get_field:
            start_date = get['start_work_date']
            
            date1   = time.strptime(start_date,"%Y-%m-%d")
            print"1", date1
            date11  = time.strftime("%Y%m%d",date1)
            print"2", date11
            year    = int(date11[:4])
            month   = int(date11[4:6])
            day     = int(date11[6:])
            date111 = datetime.datetime(year, month, day)
            
            
         
                
            end_date = get['end_work_date']
            
            date2   = time.strptime(end_date,"%Y-%m-%d")
            date22  = time.strftime("%Y%m%d",date2)
            year    = int(date22[:4])
            month   = int(date22[4:6])
            day     = int(date22[6:])
            date222 = datetime.datetime(year, month, day, 0, 0, 0)
            
            diff = date222 - date111
            
            diffDay = int(diff.days) + 1
            print "HARIAN", diffDay
            
            week = int(diffDay) / 7
            #print "WEEEEEEEEEEEEEEEEEEEEEEEEEK", week
#            =======================================================
            period = int(week / total_week_in_period)
            
            rest_of_the_day = diffDay - (period * (leave_time_week + 1))
            print "HARIAN", rest_of_the_day
            rest_of_the_week = int(rest_of_the_day / 7)
            print "WEEK", rest_of_the_week
            
            rest_of_the_day = rest_of_the_day - (rest_of_the_week * 7)
            
            if rest_of_the_week > 1:
                week = "Weeks"
            else:
                week = "Week"
            
            if rest_of_the_day > 1:
                day = "Days"
            else:
                day = "Day"
            
            
            if rest_of_the_week == 0 and rest_of_the_day == 0:
                rest_of_the_day = "No Rest of The day Number"
            elif rest_of_the_week == 0:
                rest_of_the_day = "%d %s" %(rest_of_the_day, day)
            elif rest_of_the_day == 0:
                rest_of_the_day = "%d %s" %(rest_of_the_week, week)
            else:
                rest_of_the_day = "%d %s & %d %s" %(rest_of_the_week, week, rest_of_the_day, day)
            
            print "WEEK", rest_of_the_week
            print "DAYS", rest_of_the_day
            print "SISA HARI : ", rest_of_the_day
            
            print "++++++++++",period
            for hr in range(0,period):
                wkt_kerja = date111 + datetime.timedelta (days = work_time_week)
                wkt_libur = date111 + datetime.timedelta (days = leave_time_week)
                
                start_kerja = date111
                
                print "MULAI KERJA DARI", start_kerja
                
                print "MULAI KERJA S/D", wkt_kerja
                
                start_libur = wkt_kerja + datetime.timedelta (days = 1)
                
                print "MULAI LIBUR DARI", start_libur
                
                print "MULAI LIBUR S/D", wkt_libur
                print "==================================================================================="
                
                tes = self.pool.get('rosters.schedule').search(cr,uid,[('id','=',ids)])
                hasil = self.pool.get('rosters.schedule').browse(cr,uid, tes)
               
                for id in hasil:
                    
                    print "rtrtrtrtrt", id.id
                    
                    
                    obj_rosters_line.create(cr, uid, {
                                                'roster_id' : id.id,
                                                'start_work_date' : start_kerja,
                                                'end_work_date' : wkt_kerja,
                                                'start_holiday_date' : start_libur,
                                                'end_holiday_date' : wkt_libur,
                                                })
                    obj_rosters.write(cr, uid, [id.id], {
                                                'rest_of_the_day' : rest_of_the_day,
                                                
                                                })
                    
                date111 = wkt_libur
                
                date111 = date111 + datetime.timedelta (days = 1)

#        ===================================================================================
        
        
        #print "lkkkkkkkkkkkkkkkkk"
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"confirm"})
        return True
    
    def button_approve(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"approved"})
        return True
    
    def button_cancel(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"cancelled"})
        return True
    
    
    def onchange_department_id(self, cr, uid, ids, employee):
        if not employee:
            val={
                'department_id':False,
                'type': False,
            }
            
            return {'value':val}
        addr = self.pool.get('hr.employee').browse(cr, uid, employee)
        print "============", addr
        val = {
            'department_id': addr.department_id.id,
            'type': addr.rosters_type_id.id,
                }
        
        return {'value': val}
    
    _columns = {
                
                'employee':fields.many2one('hr.employee','Employee name',size=4, required=True, select=1, readonly= True ,states={"draft":[("readonly", False)]}),
                'department_id': fields.many2one('hr.department', 'Department', required=True, select=2 ,readonly= True ,states={"draft":[("readonly", False)]}),
                #'rosters_line':fields.one2many('rosters.line','start_date','Rosters Line',readonly= True ,states={"draft":[("readonly", False)]}),
                
                #'work_leave': fields.selection([('work','Working'),('leave','Leave')], 'Work/Leave', readonly=False),
                'start_work_date':fields.date("Start Date", required=True, readonly= True,states={"draft":[("readonly", False)]}),
                'end_work_date':fields.date("End Date", required=True, readonly= True,states={"draft":[("readonly", False)]}),
                'line_ids': fields.one2many('rosters.schedule.line', 'roster_id', 'Rosters Lines', required=True, readonly= True ,states={"draft":[("readonly", False)]}),
                
                'type': fields.many2one('rosters.schedule.type','Rosters Type',size=4, required=True, select=3,readonly= True ,states={"draft":[("readonly", False)]}),
          
                'rest_of_the_day':fields.char("Rest of The Day", size=64 ,readonly=True , help="This is Rest of The Day"),
                
                'end_ext_date':fields.date("Extends Date"),
                'reason': fields.text('Reason'),
                
                'state': fields.selection([
                        ('draft', 'Draft'),
                        ('confirm', 'Waiting Approval'),
                        ('approved', 'Approved'),
                        ('cancelled', 'Cancelled')],
                        'State', readonly=True, ),
                }
    _defaults = {
        'state': lambda * a: 'draft',
        'start_work_date': lambda obj, cr, uid, context: time.strftime('%Y-%m-%d'),
        #'type' : lambda * a: 1,
                }
rosters_schedule()
