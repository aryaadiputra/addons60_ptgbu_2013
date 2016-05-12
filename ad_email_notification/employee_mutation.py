from osv import osv,fields
from tools.translate import _
import datetime
import time
import tools

class mutation_history(osv.osv):
    _name       = "mutation.history"
    _columns    = {
                   'name'           : fields.many2one('hr.employee','Employee',required=True,readonly=True,help="Please select employee that is being mutated"),
                   'mutation_date'  : fields.date('Mutation Date', required=True),
                   'old_position'   : fields.many2one('hr.job','Position',readonly=True),
                   'old_level'      : fields.many2one('hr.job.level','Grade',readonly=True),
                   'old_department' : fields.many2one('hr.department','Department',readonly=True),
                   'old_section'    : fields.many2one('hr.section','Section',readonly=True),
                   'new_position'   : fields.many2one('hr.job','New Position'),
                   'new_level'      : fields.many2one('hr.job.level','New Grade'),
                   'new_department' : fields.many2one('hr.department','New Department'),
                   'old_type'       : fields.selection([('bob','BOB'),
                                                    ('bsp','BSP')], 'Old Placement',readonly=True),
                   'new_type'       : fields.selection([('bob','BOB'),
                                                    ('bsp','BSP')], 'New Placement'),
                   'new_section'    : fields.many2one('hr.section','New Section'),
                   'send_mail'      : fields.boolean('Send Mail Notification?',help="Check this box if you want this mutation announced by email"),
                   'recipient'      : fields.many2many('hr.employee','mutation_emp_rel','emp_id','mutation_id','Recipient'),
                   'approved'       : fields.date('Approval Date',readonly=True),
                   'body'           : fields.text('Body',required=True),
                   'state'          : fields.selection([('draft','Draft'),
                                                        ('waiting','Waiting Approval'),
                                                        ('approved','Approved'),
                                                        ('done','Done')], 'Status',readonly=True),
                   }
    
    _defaults   = {
                   'body'           : """
<center><h2>PEMBERITAHUAN</h2></center>
<br><br>
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
Telah dimutasikan dari:
<table>
    <tr>
        <td width="150">Jabatan</td>
        <td>: [past_position]</td>    
    </tr>
    <tr>
        <td>Golongan</td>
        <td>: [past_grade]</td>
    </tr>
    <tr>
        <td>Departemen</td>
        <td>: [past_department]</td>
    </tr>
    <tr>
        <td>Seksi</td>
        <td>: [past_section]</td>
    </tr>
</table>
<br>
Per tanggal [date] ke:
<table>
    <tr>
        <td width="150">Jabatan</td>
        <td>: [current_position]</td>    
    </tr>
    <tr>
        <td>Golongan</td>
        <td>: [current_grade]</td>
    </tr>
    <tr>
        <td>Departemen</td>
        <td>: [current_department]</td>
    </tr>
    <tr>
        <td>Seksi</td>
        <td>: [current_section]</td>
    </tr>
</table>
<br>
Demikian disampaikan, atas perhatiannya diucapkan terimakasih.<br><br>

<p align='right'><b><i><font color='red'>Open</font></i>ERP</b> HRMS System</p>
"""
                   }
    
    def replace_code(self,text,dict):
        for i,j in dict.iteritems():
            text=text.replace(i,j)
        return text
    
    def _send_mails(self, cr, uid, ids, context):
        import re
        import pooler
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
        if data.name.name[-1:]=='s':
            subject=data.name.name+"' Mutation"
        else:
            subject=data.name.name+"'s Mutation"
        state = True
        body=data.body
        
        
        if data.mutation_date:
            ttyme = datetime.datetime.fromtimestamp(time.mktime(time.strptime(data.mutation_date,"%Y-%m-%d")))
            mutation_date = tools.ustr(ttyme.strftime('%d %B %Y'))
        else:
            mutation_date=False

        if data.name.doj:
            ttyme = datetime.datetime.fromtimestamp(time.mktime(time.strptime(data.name.doj,"%Y-%m-%d")))
            tmt = tools.ustr(ttyme.strftime('%d %B %Y'))
        else:
            tmt = False
	        
	admission_date = 'N/A'
	if data.name.admission_date:
	    admission = datetime.datetime.fromtimestamp(time.mktime(time.strptime(data.name.admission_date,"%Y-%m-%d")))
	    admission_date = tools.ustr(admission.strftime('%d %B %Y'))
 
        dict={
              '[name]'                  : data.name.name or "N/A",
              '[nik]'                   : data.name.nik or "N/A",
              '[tmt]'                   : tmt or "N/A",
              '[past_position]'         : data.old_position.name or "N/A",
              '[past_grade]'            : data.old_level.name or "N/A",
              '[past_department]'       : data.old_department.name or "N/A",
              '[past_section]'          : data.old_section.name or "N/A",
              '[current_position]'      : data.new_position.name or "N/A",
              '[current_grade]'         : data.new_level.name or "N/A",
              '[current_department]'    : data.new_department.name or "N/A",
              '[current_section]'       : data.new_section.name or "N/A",
              '[date]'         		: mutation_date or "N/A",
	      #'[date]'			: tmt or "N/A",#admission_date or "N/A",
              }
        
        content = self.replace_code(body, dict)
        p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, sendto, subject, content, attachments)

        if not state:
            raise osv.except_osv(_('Error sending email'), _('Please check the Server Configuration!'))
    
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
            emp=ol.name
            update={
                    'job_id'            : ol.new_position.id,
                    'department_id'     : ol.new_department.id,
                    'section'           : ol.new_section.id,
                    'current_job_level' : ol.new_level.id,
                    }
            write= emp.write(update)
            #print "==========",ol.old_position.id,ol.name.id
            structure_pool=self.pool.get('res.organization.structures')
            structure_history_pool=self.pool.get('org.structure.history')
            structure_old_id=structure_pool.search(cr,uid,[('job_id','=',ol.old_position.id),('head','=',ol.name.id)])
            structure_new_id=structure_pool.search(cr,uid,[('job_id','=',ol.new_position.id)])
            #print "==========",structure_old_id,structure_new_id
            if structure_old_id:
                history_structure={
                    'employee_id':ol.name.id,
                    'date_changed':time.strftime("%Y-%m-%d"),
                    'structure_id':structure_old_id[0]
                           }
                structure_history_pool.create(cr,uid,history_structure)
                structure_pool.write(cr,uid,structure_old_id,{'head':False})
            if structure_new_id:
                for employee_in_new_structure in structure_pool.browse(cr,uid,structure_new_id):
                    self.pool.get('hr.employee').write(cr,uid,employee_in_new_structure.head.id,{'department_id':False,'section':False,'job_id':False})
                    structure_pool.write(cr,uid,structure_new_id,{'head':ol.name.id})
            
            if write:
                if ol.send_mail:
                    self._send_mails(cr, uid, ids, context)
                ol.write({"state":"done",
                          "approved":time.strftime('%Y-%m-%d')})
            else:
                raise osv.except_osv(_('Update Error'), _('Update is not successfull !'))
        return True
mutation_history()

class employee_mutation(osv.osv_memory):
    _name       = "employee.mutation"
    _description= "Send Notification for Employee Mutation"
    _columns    = {
                   'name'           : fields.many2one('hr.employee','Employee',required=True,help="Please select employee that is being mutated"),
                   'old_position'   : fields.related('name', 'job_id', type='many2one', relation='hr.job', string='Last Position', store=True, readonly=True),
                   'old_department' : fields.related('name', 'department_id', type='many2one', relation='hr.department', string='Last Department', store=True, readonly=True),
                   'old_section'    : fields.related('name', 'section', type='many2one', relation='hr.section', string='Last Section', store=True, readonly=True),
                   'old_level'      : fields.related('name', 'current_job_level', type='many2one', relation='hr.job.level', string='Last Level', store=True, readonly=True),
                   'old_type'       : fields.related('job_id','placement', type='selection', selection=[('bob','BOB'),
                                                    ('bsp','BSP')], string='Old Placement',readonly=True,store=True),
                   'new_position'   : fields.many2one('hr.job','New Position'),
                   'new_department' : fields.many2one('hr.department','New Department'),
                   'new_section'    : fields.many2one('hr.section','New Section'),
                   'new_level'      : fields.many2one('hr.job.level','New Grade'),
                   'new_type'       : fields.selection([('bob','BOB'),
                                                    ('bsp','BSP')], 'New Placement'),
                   'mutation_date'  : fields.date('Mutation Date',required=True),
                   'send_mail'      : fields.boolean('Send Mail Notification?',help="Check this box if you want this mutation announced by email"),
                   }
    
    def onchange_new_position(self,cr,uid,ids,new_position,context={}):
        if new_position:
            job_data=self.pool.get('hr.job').browse(cr,uid,new_position,context=context)
            #print "=====================",job_data
            return{'value':{'new_position':new_position,'new_section':job_data.section_id.id or False,'new_department':job_data.department_id.id or False,'new_type':job_data.placement or False}}
        else:
            return{'value':{'new_position':False,'new_department':False,'new_section':False,'new_type':False}}
    
    def onchange_employee(self,cr,uid,ids,employee,context=None):
        diction={}
        if employee:
            employee = self.pool.get('hr.employee').browse(cr,uid,employee)
            if employee.job_id:
                diction['old_position']    = employee.job_id.id
            if employee.department_id:
                diction['old_department']  = employee.department_id.id
            if employee.section:
                diction['old_section']     = employee.section.id
            if employee.type:
                diction['old_type']        = employee.type
            if employee.current_job_level:
                diction['old_level']       = employee.current_job_level.id
        return {'value':diction}
    
    def default_get(self, cr, uid, fields, context={}):
        result = super(osv.osv_memory, self).default_get(cr, uid, fields, context=context)
        if context['active_model']!='ir.ui.menu':
            id=context.get('active_id', None)
            result['name'] =  context.get('active_id', None)
            result['old_position'] = self.pool.get('hr.employee').browse(cr,uid,id).job_id.id
            result['old_department'] = self.pool.get('hr.employee').browse(cr,uid,id).department_id.id
            result['old_section'] = self.pool.get('hr.employee').browse(cr,uid,id).section.id
            result['old_type'] = self.pool.get('hr.employee').browse(cr,uid,id).type
        return result
    
    def mutate_employee(self,cr,uid,ids,context):
        form=self.browse(cr,uid,ids)[0]
        data={
              'name'            : form.name.id,
              'old_position'    : form.name.job_id.id,
              'old_department'  : form.name.department_id.id,
              'old_section'     : form.name.section.id,
              'old_type'        : form.name.type,
              'old_level'       : form.name.current_job_level.id,
              'new_position'    : form.new_position.id,
              'new_department'  : form.new_department.id,
              'new_section'     : form.new_section.id,
              'new_type'        : form.new_type,
              'new_level'       : form.new_level.id,
              'mutation_date'   : form.mutation_date,
              'send_mail'       : form.send_mail,
              'state'           : 'draft'
              }
        #print "data===========>",data
        mh_id = self.pool.get('mutation.history').create(cr,uid,data)
        ret= {
                'domain': str([]),
                'name':"Employee Mutation",
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': 'mutation.history',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': '[]',
                'res_id': mh_id,
                'context': context
            }
        
        return ret
employee_mutation()

class hr_employee(osv.osv):
    _inherit="hr.employee"
    _columns = {
        'mutation_ids':fields.one2many("mutation.history","name","Mutation History")
                }
hr_employee()
