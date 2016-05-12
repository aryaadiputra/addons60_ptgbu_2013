from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
import tools
import pooler
import netsvc
import datetime

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    
    def _send_birthday_mails(self, cr, uid, eid, email, ename, ebirthday, context):
        import re
        p = pooler.get_pool(cr.dbname)
        smtpserver_id = p.get('email.smtpclient').search(cr, uid, [('type','=','default'),('state','=','confirm'),('active','=',True)], context=False)
        if smtpserver_id:
            smtpserver_id = smtpserver_id[0]
        else:
            raise osv.except_osv(_('Error'), _('No SMTP Server has been defined!'))
    
        emp = self.pool.get('hr.employee').search(cr,uid,[('type','=','bsp')])
        sendto = []
        for emp in self.pool.get('hr.employee').browse(cr,uid,emp):
            if emp.work_email:
                sendto.append(emp.work_email)
        attachments = []
        if ename[-1:]=='s':
            subject=ename+"' Birthday"
        else:
            subject=ename+"'s Birthday"
        state = True
        
        
        
        body="""
<center>
    <font face="arial">Hari ini adalah hari yang membahagiakan untuk rekan kita """+ename+""" yang sedang berulang tahun.</font>
    <br><br>
    <font face="arial">Kami, atas nama Pimpinan dan segenap jajaran PT Bumi Siak Pusako mengucapkan: </font>
    <h2><font style="color:#390; font-family:'Monotype Corsiva';font-size:22pt;">SELAMAT ULANG TAHUN</font></h2>
    <font face="arial">kepada</font>
    <h3>"""+ename+"""</h3>
    <font face="arial">Semoga panjang umur, sehat dan bahagia selalu. </font>
</center>
<br><br><br>
<p align='right'><b><i><font color='red'>Open</font></i>ERP</b> HRMS System</p>
"""
         
        p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, sendto, subject, body, attachments)

        if state:
            print "Success"
        else:
            raise osv.except_osv(_('Error sending email'), _('Please check the Server Configuration!'))

    def run_task_scheduler(self, cr, uid, context=None):
        cr.execute("""select e.id as id, 
                             e.work_email as email, 
                             r.name as name, 
                             e.birthday as birthday 
                      from hr_employee e, resource_resource r 
                      where e.resource_id=r.id and extract(month from e.birthday)=extract(month from now()) and 
                            extract(day from e.birthday)=extract(day from now()) and 
                            e.type='bsp'""")
        results = cr.fetchall()
        for eid, email, ename, ebirthday in results:
            self._send_birthday_mails(cr, uid, eid, email, ename, ebirthday, context=None)
        return True
    
hr_employee()