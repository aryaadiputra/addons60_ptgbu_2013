from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
import pooler
import netsvc
import datetime

class ir_attachment(osv.osv):
    _inherit = "ir.attachment"
    _columns = {
        'date_expired' : fields.date('Expired Date', required=True),
        'date_issued' : fields.date('Date Issued'),
        'recipient' : fields.many2many('res.users', 'recipient_rel', 'attachment_id','recipient_id','Recipient'),
		}
    
    def run_task_scheduler(self, cr, uid, context=None):
        task_obj = self.pool.get('project.task')
        cr.execute('select id, name, user_id, company_id, description, date_expired from ir_attachment')
        self.results = cr.fetchall()
        for self.aid, self.aname, self.user, self.acompany, self.desc, self.adate_expired in self.results:
            today = datetime.date.today()
            self.remain = {
                      'thirty':30,
                      'fifteen':15,
                      'one':1,
                      'due':0,
                      }
            for self.key in self.remain:
                print "self.key",self.key," self.remain[self.key]",self.remain[self.key]
                remaining_day = datetime.timedelta(days=self.remain[self.key])
                future = today + remaining_day
                self.expire = str(self.adate_expired)
                self.future = str(future)
                task_name="Reminder for Updating Document "+self.aname
                print "remaining_day===>>>",remaining_day,"future===>>>",future
                print "self.expire",self.expire
                print "self.future",self.future
                if self.expire == self.future:
                    task_id = task_obj.create(cr, uid, {
                        'name': task_name,
                        'date_deadline': self.expire,
                        'user_id': self.user,
                        'notes': self.desc,
                        'description': self.desc,
                        'company_id': self.acompany,
                    },context=context)
                    data = []
                    self._send_mails(cr, uid, data, context=None)
                else:
                    continue
        return True
    
    def _send_mails(self, cr, uid, data, context):
        import re
        p = pooler.get_pool(cr.dbname)
        user = p.get('res.users').browse(cr, uid, uid, context)
        default_smtpserver_id = p.get('email.smtpclient').search(cr, uid, [('type','=','task'),('state','=','confirm'),('active','=',True)], context=False)
        print default_smtpserver_id
        smtpserver_id = default_smtpserver_id
        if smtpserver_id:
            smtpserver_id = smtpserver_id[0]
        else:
            raise osv.except_osv(_('Error'), _('No SMTP Server has been defined!'))
    
        attachments = []
        company=self.pool.get('res.company').browse(cr,uid,self.acompany)
        owner=self.pool.get('res.users').browse(cr,uid,self.user)
        subject="Document Reminder for "+self.aname
        att_id=str(self.aid)
        query="select attachment_id,recipient_id from recipient_rel where attachment_id='"+att_id+"'"
        cr.execute(query)
        result = cr.fetchall()
        
        print "user email=======>>>",owner.user_email
        state = True
        
        sendto = []
        sendto.append(owner.user_email)
        if self.remain[self.key]==30:
            body = "Dear <b>"+owner.name+"</b>, <br /><br />Masa berlaku dokumen <b>"+self.aname+"</b> untuk perusahaan <b>"+company.name+"</b> akan berakhir dalam waktu <b>30 hari</b> ke depan. <br />Silahkan menuju menu Knowledge > Documents > Documents untuk memperbaharui dokumen tersebut.<br /><br /><b><i><font color='red'>Open</font></i>ERP</b> System"
        elif self.remain[self.key]==15:
            body = "Dear <b>"+owner.name+"</b>, <br /><br />Masa berlaku dokumen <b>"+self.aname+"</b> untuk perusahaan <b>"+company.name+"</b> akan berakhir dalam waktu <b>15 hari</b> ke depan. <br />Silahkan menuju menu Knowledge > Documents > Documents untuk memperbaharui dokumen tersebut.<br /><br /><b><i><font color='red'>Open</font></i>ERP</b> System"
        elif self.remain[self.key]==1:
            body = "Dear <b>"+owner.name+"</b>, <br /><br />Masa berlaku dokumen <b>"+self.aname+"</b> untuk perusahaan <b>"+company.name+"</b> akan berakhir <b>besok</b>. <br />Silahkan menuju menu Knowledge > Documents > Documents untuk memperbaharui dokumen tersebut.<br /><br /><b><i><font color='red'>Open</font></i>ERP</b> System"
        p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, sendto, subject, body, attachments)

        for att, rec in result:
            recipient = self.pool.get('res.users').browse(cr,uid,rec)
            sendto = []
            sendto.append(recipient.user_email)
            if recipient.user_email:
                if self.remain[self.key]==30:
                    body = "Dear <b>"+recipient.name+"</b>, <br /><br />Masa berlaku dokumen <b>"+self.aname+"</b> untuk perusahaan <b>"+company.name+"</b> akan berakhir dalam waktu <b>30 hari</b> ke depan. <br />Silahkan menuju menu Knowledge > Documents > Documents untuk memperbaharui dokumen tersebut.<br /><br /><b><i><font color='red'>Open</font></i>ERP</b> System"
                elif self.remain[self.key]==15:
                    body = "Dear <b>"+recipient.name+"</b>, <br /><br />Masa berlaku dokumen <b>"+self.aname+"</b> untuk perusahaan <b>"+company.name+"</b> akan berakhir dalam waktu <b>15 hari</b> ke depan. <br />Silahkan menuju menu Knowledge > Documents > Documents untuk memperbaharui dokumen tersebut.<br /><br /><b><i><font color='red'>Open</font></i>ERP</b> System"
                elif self.remain[self.key]==1:
                    body = "Dear <b>"+recipient.name+"</b>, <br /><br />Masa berlaku dokumen <b>"+self.aname+"</b> untuk perusahaan <b>"+company.name+"</b> akan berakhir <b>besok</b>. <br />Silahkan menuju menu Knowledge > Documents > Documents untuk memperbaharui dokumen tersebut.<br /><br /><b><i><font color='red'>Open</font></i>ERP</b> System"
            p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, sendto, subject, body, attachments)
            print "sendto dalemmmmmm",sendto
        print body
        print "sendto",sendto
        
#        print state
        if state:
            print "Success"
        else:
            raise osv.except_osv(_('Error sending email'), _('Please check the Server Configuration!'))
ir_attachment()
