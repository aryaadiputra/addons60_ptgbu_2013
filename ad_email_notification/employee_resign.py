from osv import fields,osv
from tools.translate import _
import tools
import datetime
import time
import re
import pooler

class hr_resign_department(osv.osv):
    _name = "hr.resign.department"
    _columns = {
           'name' : fields.char('Name Department',size=512, required=True),
           }
hr_resign_department()

class hr_resign_type(osv.osv):
    _name = "hr.resign.type"
    _columns = {
           'name' : fields.char('Type',size=512, required=True),
           'resign_department' : fields.many2one("hr.resign.department", 'Department'),
           }
hr_resign_type()

class hr_resign_list_inventory(osv.osv):
    _name = "hr.resign.list.inventory"
    _columns = {
           'type_id' : fields.many2one("hr.resign.type", 'Resign Type'),
           'status' : fields.boolean("Status",help=""),
           'resign_id' : fields.many2one('hr.resign','Resign Type'),
           }
hr_resign_list_inventory()

class hr_resign(osv.osv):
    _name = "hr.resign"
    
    def create(self,cr,uid,data,context=None):
        data['name'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.resign')
        return super(hr_resign,self).create(cr,uid,data,context=context)
    
    def replace_code(self,text,dict):
        for i,j in dict.iteritems():
            text=text.replace(i,j)
        return text
    
    def _get_department(self,cr,uid,ids,field,arg,context={}):
        resigns=self.browse(cr,uid,ids,context=context)
        result = {}
        for resign in resigns :
            result[resign.id] = resign.employee_id and resign.employee_id.department_id and resign.employee_id.department_id.id or False
        return result
    
    def _get_job(self,cr,uid,ids,field,arg,context={}):
        resigns=self.browse(cr,uid,ids,context=context)
        result = {}
        for resign in resigns :
            result[resign.id] = resign.employee_id and resign.employee_id.job_id and resign.employee_id.job_id.id or False
        return result
    
    def _get_job_level(self,cr,uid,ids,field,arg,context={}):
        resigns=self.browse(cr,uid,ids,context=context)
        result = {}
        for resign in resigns :
            result[resign.id] = resign.employee_id and resign.employee_id.current_job_level and resign.employee_id.current_job_level.id or False
        return result
    
    _columns    = {
                   'name'           : fields.char('Resign Reference',size=16,required=True),
                   'employee_id'    : fields.many2one("hr.employee","Employee",required=True),
                   'state'          : fields.selection([('draft',"Draft"),('proposed','Proposed'),('approved',"Approved")],"State",readonly=True),
                   'department_id'  : fields.function(_get_department,method=True,type='many2one',obj="hr.department",string='Department',help="Employee Department",store=True),
                   'job_id'         : fields.function(_get_job,method=True,type='many2one',obj="hr.job",string='Current Job',help="Current Job",store=True),
                   'job_level_id'   : fields.function(_get_job_level,method=True,type='many2one',obj="hr.job.level",string='Job Level',help="Current Job Level",store=True),
                   'send_mail'      : fields.boolean("Send Email Notification?",help="Check this box if you want this retirement announced by email"),
                   'date_retirement': fields.date("Retirement Date",required=True),
                   'date_submission': fields.date("Submission Date",required=True),
                   'reason_summary' : fields.text("Reason Summary",required=True),
                   'date_approved'  : fields.date("Approval Date"),
                   'resign_letter'  : fields.binary('Resignation Letter',required=True),
                   'recipient'      : fields.many2many('hr.employee','retirement_emp_rel','emp_id','retirement_id','Recipient'),
                   'body'           : fields.text('Body',required=True),
                   'resign_list_inv_id' : fields.one2many('hr.resign.list.inventory', 'resign_id', 'Information Type'),
                   'resign_list_inv_id_it' : fields.one2many('hr.resign.list.inventory', 'resign_id', 'Information Type'),
                   'resign_list_inv_id_finance' : fields.one2many('hr.resign.list.inventory', 'resign_id', 'Information Type'),
                   'resign_list_inv_id_hr' : fields.one2many('hr.resign.list.inventory', 'resign_id', 'Information Type'),
                   'status' : fields.boolean("Status",help=""),
                   'serah_terima_file' : fields.boolean("Handover Of Files",help=""),
                   'fasilitas_kerja' : fields.boolean("Office Facility",help=""),
                   'finished_petty_cash_division' : fields.boolean("Finished Petty Cash Division",help=""),
                   'deleted_mail_box' : fields.boolean("Deleted Mail Box",help=""),

                   ####ARYA####
                   # IT division
                   'it_note'                : fields.text("IT Department Notes",required=False),
                   'it_checking_state'      : fields.selection([('draft',"Unconfirm"),('approve','Confirmed')],"Checking State",readonly=True),
                   'deleting_email'      : fields.boolean("Information for removing account email",help="Check this box if you want to delete information for removing email"),
                   'deleting_lotus_note'      : fields.boolean("Information for removing Lotus Notes",help="Check this box if you want to delete information for removing Lotus Notes"),
                   'deleting_userid_pass'      : fields.boolean("Information for removing User ID and Password",help="Check this box if you want to delete information for removing User ID and Password"),
                   # Finance division
                   'finance_note'           : fields.text("Finance Department Notes",required=False),
                   'finance_checking_state' : fields.selection([('draft',"Unconfirm"),('approve','Confirmed')],"Checking State",readonly=True),
                   'advance'      : fields.boolean("Advance",help="Check this box if you want to delete information of advance"),
                   'petty_cash'      : fields.boolean("Petty Cash",help="Check this box if you want to delete information of petty cash"),
                    # GA division
                   'general_affair_note' : fields.text("General Affair Department Notes",required=False),
                   'ga_checking_state' : fields.selection([('draft',"Unconfirm"),('approve','Confirmed')],"Checking State",readonly=True),
                   'motor' : fields.boolean("Motor",help=""),
                   'mobil' : fields.boolean("Mobil",help=""),
                   'pengemudi' : fields.boolean("Driver",help=""),
                   'notebook' : fields.boolean("Notebook",help=""),
                   'handphone' : fields.boolean("Handphone",help=""),
                   'pager': fields.boolean("Pager",help=""),
                   'handy_talky' : fields.boolean("HT",help=""),
                   'kamera' : fields.boolean("Camera",help=""),
                   # HRD division
                   'hrd_note' : fields.text("HRD Department Notes",required=False),
                   'hrd_checking_state' : fields.selection([('draft',"Unconfirm"),('approve','Confirmed')],"Checking State",readonly=True),
                   'saldo_pinjaman' : fields.boolean("Residual Loan",help=""),
                   'saldo_cuti' : fields.boolean("Residual Leaves",help=""),
                   'pass_tlpn' : fields.boolean("Information for deleting Phone Password",help=""),
                   'id_card' : fields.boolean("ID Card & Access Card",help=""),
                   'kartu_nama' : fields.boolean("Bussiness Card",help=""),
                   'kartu_assuransi' : fields.boolean("Assurance Card",help=""),
                   ############
                   }
    
    def button_proposed(self,cr,uid,ids,context={}):
        resign=self.browse(cr,uid,ids,context=context)[0]
        resign.write({'state':'proposed'})
        return True
    
    def button_draft(self,cr,uid,ids,context={}):
        resign=self.browse(cr,uid,ids,context=context)[0]
        resign.write({'state':'draft'})
        return True
    
    def _send_mails(self, cr, uid, ids, context):
        
        data = self.browse(cr, uid, ids[0])
        
        p = pooler.get_pool(cr.dbname)
        smtpserver_id = p.get('email.smtpclient').search(cr, uid, [('type','=','default'),('state','=','confirm'),('active','=',True)], context=False)
        if smtpserver_id:
            smtpserver_id = smtpserver_id[0]
        else:
            raise osv.except_osv(_('Error'), _('No SMTP Server has been defined!'))
    
        sendto = []
        for emp in data.recipient:
            sendto.append(emp.work_email)
        attachments = []
        if data.employee_id.name[-1:]=='s':
            subject=data.employee_id.name+"' Retirement"
        else:
            subject=data.employee_id.name+"'s Retirement"
        state = True
        body=data.body
        
        
        if data.date_retirement:
            ttyme = datetime.datetime.fromtimestamp(time.mktime(time.strptime(data.date_retirement,"%Y-%m-%d")))
            date_retirement = tools.ustr(ttyme.strftime('%d %B %Y'))
        else:
            date_retirement=False

        if data.employee_id.doj:
            ttyme = datetime.datetime.fromtimestamp(time.mktime(time.strptime(data.employee_id.doj,"%Y-%m-%d")))
            tmt = tools.ustr(ttyme.strftime('%d %B %Y'))
        else:
            tmt = False
        
        dict={
              '[name]'                  : data.employee_id.name or "N/A",
              '[nik]'                   : data.employee_id.nik or "N/A",
              '[tmt]'                   : tmt or "N/A",
              '[retirement_date]'       : date_retirement or "N/A",
              '[reason]'                : data.reason_summary
              }
        
        content = self.replace_code(body, dict)
        p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, sendto, subject, content, attachments)

        if not state:
            raise osv.except_osv(_('Error sending email'), _('Please check the Server Configuration!'))
        
    def button_approve(self,cr,uid,ids,context={}):
        resigns=self.browse(cr,uid,ids,context=context)
        for resign in resigns:
            default={'experience_id':[],'non_active':False}
            emp_id=resign.employee_id.id
            res_id=resign.employee_id.resource_id.id
            contract_ids=self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',emp_id),'|',('date_end','>=',time.strftime("%Y-%m-%d")),('date_end','=',False)])
            if not contract_ids:
                raise osv.except_osv(_('No Contract'), _('There is no valid contract for '+resign.employee_id.name))
            contract_data=self.pool.get('hr.contract').browse(cr,uid,contract_ids)[0]
            experience = {
                'name'          : "%s - %s" %(resign.employee_id.type.upper(),resign.employee_id.company_id.name),
                'exp_from'      :contract_data.date_start,
                'exp_to'        :time.strftime("%Y-%m-%d"),
                'address'       :False,
                'note'          :False,
                'wage'          :contract_data.wage,
                'res_id'        :res_id,
                'exp_position'  :resign.employee_id.job_id.name or "N/A",
                         }
            self.pool.get('hr.experience').create(cr,uid,experience)
            structure_id=self.pool.get('res.organization.structures').search(cr,uid,[('job_id','=',resign.employee_id.job_id.id),('head','=',emp_id)])
            
            self.pool.get('res.organization.structures').write(cr,uid,structure_id,{'head':False,})
            #default['experience_id'].append(experience)
            default['non_active']=True
            #print "default====>",default
            self.pool.get('hr.employee').write(cr,uid,emp_id,default)
            self.pool.get('org.structure.history').create(cr,uid,{'employee_id':resign.employee_id.id,'date_changed':time.strftime("%Y-%m-%d"),'structure_id':structure_id})
            exe=False
            exe=self.pool.get('resource.resource').write(cr,uid,res_id,{'active':False, 'non_active':True})
            self.pool.get('hr.contract').write(cr,uid,contract_ids,{'date_end':time.strftime("%Y-%m-%d")})
            if exe:
                if resign.send_mail:
                    self._send_mails(cr, uid, ids, context)
                    resign.write({'state':'approved','date_approved':resign.date_approved or time.strftime("%Y-%m-%d")})
            
        return True
    _defaults   = {
                   'it_checking_state'  : 'draft',
                   'finance_checking_state'  : 'draft',
                   'hrd_checking_state' : 'draft',
                   'ga_checking_state'  : 'draft',
                   'state'              : lambda *a:'draft',
                   'date_submission'    : time.strftime('%Y-%m-%d'),
                   'name'               : '/',
                   'body'               : """
<center><h2>PEMBERITAHUAN</h2></center><br><br>

Kepada Yth,
Bapak / Ibu sekalian<br><br>

Dengan ini diberitahukan:<br><br>

<table>
    <tr>
        <td width="100">Nama</td>
        <td>: [name]</td>    
    </tr>
    <tr>
        <td>NIK</td>
        <td>: [nik]</td>
    </tr>
    <tr>
        <td>TMT</td>
        <td>: [tmt]</td>
    </tr>
</table>
<br>
Telah berhenti dari PT Bumi Siak Pusako per tanggal [retirement_date] dengan alasan [reason] <br><br>

Demikian disampaikan, atas perhatiannya diucapkan terimakasih.<br><br>

<p align='right'><b><i><font color='red'>Open</font></i>ERP</b> HRMS System</p>
                   """,
                   }
    
    def onchange_recipient(self, cr, uid, ids, recipient):
        ids=[]
        mail_to=[]
        nm_list=""
        if recipient:
            c=1
            for r in recipient[0][2]:
                data=self.pool.get('hr.employee').browse(cr,uid,r)
                if data.work_email:
                    ids.append(r)
                    mail_to.append(data.work_email)
                else:
                    nm_list = nm_list + str(c) + ". " + data.name + "\n"
                    c+=1
        rec={'recipient':ids}
        
        warning={}
        no_mail = len(recipient[0][2]) - len(ids)
        if no_mail>0:
            warning['title']="No Email Address"
            warning['message']="Karyawan di bawah ini tidak memiliki alamat email.\nMohon periksa kembali data karyawan.\n\n"+nm_list
        return {'value':rec, 'warning':warning}
    
hr_resign()