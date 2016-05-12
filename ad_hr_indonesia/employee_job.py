from osv import osv,fields
import datetime
from mx import DateTime
from datetime import datetime
import pooler
from itertools import groupby
from operator import itemgetter
import netsvc
import re
from tools.translate import _
import pooler

class hr_employee(osv.osv):
    _inherit    = "hr.employee"
    _columns    = {
               'current_job_level' : fields.many2one('hr.job.level','Current job level'),
               }


    # sending email after contract more than 2 month
    def _send_mails_schedule(self, cr, uid, ids, employee_id):
        print "aaaaaaaaaaaaaaa", employee_id
        
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
        start_work  = ""
        subject = ""
        sendto = []
        attachments = []

        for d in self.browse(cr,uid,ids):
        	employee_ids = self.search(cr, uid, [])
        	employee_hr = self.browse(cr, uid, employee_ids)
        	for e in employee_hr:
        		if e.department_id.name == "Human Resource":
        			print "eeeeeeeeeeeeeeeeeeeeeeeeeee_hr", e.department_id.name, e.user_id.name, e.work_email
	        		if e.work_email:
	        			sendto.append(e.work_email)

		employee_data = self.browse(cr, uid, employee_id)
		print "aaaaaaaaaaaaaaaadata", employee_data
		name_employee = employee_data.user_id.name
		print "namaaaaaaaaaaaaaa", name_employee
		department = employee_data.department_id.name
		start_work = datetime.strptime(employee_data.doj,'%Y-%m-%d')
		subject = "Masa Kontrak sudah mencapai 2 Bulan"

        print ">>>>>>>>>>>", sendto , "name", name_employee, "department", department, "start_work", start_work
        
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
        <td>Mulai Bekerja</td>
        <td>:</td>
        <td>%s</td>
    </tr>
</table>
<br>

Demikian disampaikan, atas perhatiannya diucapkan terimakasih.<br><br>

<p align='right'><b><i><font color='red'>Open</font></i>ERP</b> HRMS System</p>
"""% (name_employee,department,start_work)

        p = pooler.get_pool(cr.dbname)
        p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, sendto, subject, body, attachments)


    def check_employee_contract(self, cr, uid, ids, arg, context={}):
        employee_ids = self.search(cr, uid, [('status','=','contract')])
        employee = self.browse(cr, uid, employee_ids)
        today = datetime.today().strftime('%Y-%m-%d')
        print "todaaaaaaaaaaaaaaaaaaaaaaaaaay", today
        for e in employee:
	        doj = datetime.strptime(e.doj,'%Y-%m-%d')
	        print "sekarang", doj
	        day = doj.day
	        month = doj.month + 2
	        year = doj.year

	        add2month = datetime(year, month, day)
	        add2month = add2month.strftime('%Y-%m-%d')
	        if add2month == today:
	        	print "berhasil mendatang", add2month
	        	employee_id = e.id
	        	print "aaaaaaaaaaaaaaa", employee_id
	        	self._send_mails_schedule(cr, uid, ids, employee_id)

hr_employee()