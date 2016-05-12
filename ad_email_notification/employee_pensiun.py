import pooler
import netsvc
import datetime
import tools
import time
import decimal_precision as dp
from osv import fields, osv
from tools.translate import _
from dateutil.relativedelta import relativedelta

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    
    def _get_warning_date(self):
        today           = datetime.date.today()
        warning_delta   = relativedelta(months=1,days=15)
        warning_date    = today+warning_delta
        warning_date    = warning_date.strftime('%Y-%m-%d')
        return warning_date
    
    def _run_pensiun_checker(self, cr, uid, context=None):
        dep_obj = self.pool.get('hr.department')
        sec_obj = self.pool.get('hr.section')
        #=======================================================================
        # Send to department manager
        #=======================================================================
        sendto=[]
        dep_ids = dep_obj.search(cr,uid,[('placement','=','bsp')])
        for dep in dep_obj.browse(cr,uid,dep_ids):
            if dep.manager_id.work_email:
                sendto.append(dep.manager_id.work_email)
        #=======================================================================
        # Send to section head
        #=======================================================================
        sec_ids = sec_obj.search(cr,uid,[('placement','=','bsp')])
        for sec in sec_obj.browse(cr,uid,sec_ids):
            if sec.chief_id.work_email:
                sendto.append(sec.chief_id.work_email)
        
        sendto  = ['togar@adsoft.co.id']
        emp_ids = self.search(cr,uid,[('retiring_date','=',self._get_warning_date())])
        employee= self.read(cr,uid,emp_ids,['nik','name','doj','retiring_date'])
        
        for emp in employee:
            self._send_mails(cr, uid, emp['nik'], emp['name'], emp['doj'], emp['retiring_date'], sendto, context=None)
        return True
    
    def _send_mails(self, cr, uid, nik, ename, doj, epensiun, sendto, context):
        import re
        p = pooler.get_pool(cr.dbname)
        user = p.get('res.users').browse(cr, uid, uid, context)
        smtpserver_id = p.get('email.smtpclient').search(cr, uid, [('type','=','default'),('state','=','confirm'),('active','=',True)], context=False)
        if smtpserver_id:
            smtpserver_id = smtpserver_id[0]
        else:
            raise osv.except_osv(_('Error'), _('No SMTP Server has been defined!'))
    
        attachments = []
        subject="Notifikasi Pensiun: "+ename+""
        state = True
        
        if doj:
            ttyme = datetime.datetime.strptime(doj,"%Y-%m-%d")
            tmt = tools.ustr(ttyme.strftime('%d %B %Y'))
        else:
            tmt = False
            
        if epensiun:
            ttyme = datetime.datetime.strptime(epensiun,"%Y-%m-%d")
            retire = tools.ustr(ttyme.strftime('%d %B %Y'))
        else:
            retire = False
            
        body="""
<center><h2>PEMBERITAHUAN</h2></center><br><br>

Kepada Yth,
Bapak / Ibu sekalian<br><br>

Dengan ini diberitahukan:<br><br>

<table>
    <tr>
        <td width="100">Nama</td>
        <td>: """+ename+"""</td>    
    </tr>
    <tr>
        <td>NIK</td>
        <td>: """+nik+"""</td>
    </tr>
    <tr>
        <td>TMT</td>
        <td>: """+tmt+"""</td>
    </tr>
</table>
<br>
Akan memasuki masa pensiun pada tanggal """+retire+""" <br><br>

Demikian disampaikan, atas perhatiannya diucapkan terimakasih.<br><br>

<p align='right'><b><i><font color='red'>Open</font></i>ERP</b> HRMS System</p>
"""
        print body
        p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, sendto, subject, body, attachments)

        if state:
            print "Success"
        else:
            raise osv.except_osv(_('Error sending email'), _('Please check the Server Configuration!'))
hr_employee()