# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com) All Rights Reserved.
#     vishnu@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import datetime
from osv import fields,osv
from email.Utils import COMMASPACE
import pooler
from tools.translate import _


def comp_dates2(d1, d2):
         # Date format: %Y-%m-%d %H:%M:%S
        return time.mktime(time.strptime(d2,"%Y-%m-%d %H:%M:%S"))-time.mktime(time.strptime(d1, "%Y-%m-%d %H:%M:%S"))


class task(osv.osv):
    _inherit = "project.task"
    
    _columns = {
                'create_uid': fields.many2one('res.users', 'Created User', readonly=True),
                }
    
    def do_open(self, cr, uid, ids, *args):
        super(task, self).do_open(cr, uid, ids, args)
        cr.commit()
        self.send_mail(cr, uid, ids)
        return True

    def do_reopen(self, cr, uid, ids, context=None):
        super(task, self).do_reopen(cr, uid, ids, context=None)
        cr.commit()
        sub="Task Reactivated in OpenERP :"
        self.send_mail(cr, uid, ids, [], sub)
        return True

    def do_close(self, cr, uid, ids, context=None):
        super(task, self).do_close(cr, uid, ids, context=None)
        cr.commit()
        self.send_mail(cr, uid, ids)
        return True

    def do_pending(self, cr, uid, ids, *args):
        super(task, self).do_pending(cr, uid, ids, args)
        cr.commit()
        self.send_mail(cr, uid, ids)
        return True

    def do_cancel(self, cr, uid, ids, *args):
        super(task, self).do_cancel(cr, uid, ids, args)
        cr.commit()
        self.send_mail(cr, uid, ids)
        return True

    def write(self, cr, uid, ids, vals, context=None):
#        if type(ids) == type(1):
#            ids = [ids]
#        print ids,type(ids)
        if type(ids) != type([]):
            ids = [ids]
        
        for tasks in self.browse(cr, uid, ids):
            user_rec=tasks.user_id.id
            des_rec=tasks.description
            wrk_rec=tasks.work_ids
            if tasks.project_id:
                pm=tasks.project_id.user_id.id


        if len(ids)<>1:
            return super(task, self).write(cr, uid, ids, vals, context)
        else:

            result= super(task, self).write(cr, uid, ids, vals, context)
            cr.commit()
            for _task in self.browse(cr, uid, ids):
                if _task.state not in ['draft','cancelled']:
                    if 'user_id' in vals:
                        if vals['user_id']!=user_rec:
                            e_users=[]
                            e_cc=[]
                            e_users.append(_task.user_id.id)
                            if _task.user_id.id!=_task.project_id.user_id.id: e_cc.append(_task.project_id.user_id.id)
                            sub="Task Re Assigned :"
                            self.send_mail(cr, uid, ids, e_users, sub, e_cc)
                    if 'description' in vals:
                        if vals['description']!=des_rec:
                            e_users=[]
                            e_cc=[]
                            e_users.append(_task.user_id.id)
                            if _task.user_id.id!=_task.project_id.user_id.id: e_cc.append(_task.project_id.user_id.id)
                            sub="Task Description Changed :"
                            self.send_mail(cr, uid, ids, e_users, sub, e_cc)
                    if 'work_ids' in vals:
                        if vals['work_ids']!=[]:
                            e_users=[]
                            e_cc=[]
                            e_users.append(_task.project_id.user_id.id)
                            if _task.project_id.user_id.id!=_task.user_id.id: e_cc.append(_task.user_id.id)
                            sub="Task Work Updated :"
                            self.send_mail(cr, uid, ids, e_users, sub, e_cc)
                    elif 'members' in vals:
                        send_mail_users=[]
                        for v in vals['members'][0][2]:
                            if v not in members:
                                send_mail_users.append(v)
                        if send_mail_users:
                            self.send_mail(cr, uid, ids,send_mail_users)

            return result

    def send_mail(self, cr, uid, ids, filtered_users=[], sub="", cc=[]):
        pool = self.pool

        result=None
        context=None

        emp_ids=  pool.get('hr.employee').search(cr, uid, [('user_id','in',cc)])
        mail_cc=[]
        for emp in pool.get('hr.employee').browse(cr, uid, emp_ids):
            if emp.work_email: mail_cc.append(emp.work_email.encode('utf-8'))


        #Collect company Info to get web client URL
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company_id =user.company_id
        if not company_id:
            company_id=self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
            company_id=self.pool.get('res.company').browse(cr, uid, company_id)

        smtp = self.pool.get('email.smtpclient')
        smtpserver_id = self.pool.get('email.smtpclient').select(cr, uid, 'task')

        for task in self.browse(cr, uid, ids):
            # Collect Email List
            email_users=[]
            email_cc=[]
            assigned_user=task.user_id or False
            project_manager=task.project_id.user_id or False
            if assigned_user:
                if sub=="Task Work Updated :" :
                    email_cc.append(assigned_user.id)
                else:
                    email_users.append(assigned_user.id)

            if project_manager:
                if sub=="Task Work Updated :" :
                    email_users.append(project_manager.id)
                else:
                    if project_manager.id!=assigned_user.id: email_cc.append(project_manager.id)


            if sub=='Warning,  Task "Ending Date" has been reached :' :
                email_users=[]
                email_cc=[]
                assigned_user=task.user_id or False
                project_manager=task.project_id.user_id or False
                if project_manager: email_users.append(project_manager.id)
                if assigned_user:
                    if assigned_user.id!=project_manager.id :email_cc.append(assigned_user.id)


            if task.state=='done':
                email_users=[]
                email_cc=[]
                assigned_user=task.user_id or False
                delegate_user=task.delegate_id or False
                project_manager=task.project_id.user_id or False
                if project_manager: email_users.append(project_manager.id)
                if assigned_user or delegate_user:
                    if assigned_user.id!=project_manager.id :
                        email_cc.append(assigned_user.id)
                        email_cc.append(delegate_user.id)


            #pending
            if task.state=='pending' and sub=="":
                email_users=[]
                email_cc=[]
                assigned_user=task.user_id or False
                project_manager=task.project_id.user_id or False
                if project_manager: email_users.append(project_manager.id)
                if assigned_user:
                    if assigned_user.id!=project_manager.id :email_cc.append(assigned_user.id)



            if task.state=='cancelled':
                email_users=[]
                email_cc=[]
                assigned_user=task.user_id or False
                project_manager=task.project_id.user_id or False
                if project_manager: email_users.append(project_manager.id)
                if assigned_user:
                    if assigned_user.id!=project_manager.id :email_cc.append(assigned_user.id)



            emp_ids=  pool.get('hr.employee').search(cr, uid, [('user_id','in',email_users)])
            email=[]
            for emp in pool.get('hr.employee').browse(cr, uid, emp_ids):
                if emp.work_email: email.append(emp.work_email)

            emp_ids=  pool.get('hr.employee').search(cr, uid, [('user_id','in',email_cc)])
            email_cc=[]
            for emp in pool.get('hr.employee').browse(cr, uid, emp_ids):
                if emp.work_email: email_cc.append(emp.work_email)
                

            if email:
                if smtpserver_id is False:
                    raise Exception, _('Please check the Server Configuration!')

                body=False
                subject=""

                if task.state=='done':
                    body= self.pool.get('email.smtpclient.email.template').select(cr, uid, 'task_complete')
                    subject="Task Done in OpenERP : "
                elif task.state=='pending':
                    body= self.pool.get('email.smtpclient.email.template').select(cr, uid, 'task_pending')
                    subject="Task Pending in OpenERP : "
                elif task.state=='open':
                    if sub:
                        if sub=='Warning,  Task "Ending Date" has been reached :' :
                            body= self.pool.get('email.smtpclient.email.template').select(cr, uid, 'task_warning')
                            subject=sub
                    else:
                        body= self.pool.get('email.smtpclient.email.template').select(cr, uid, 'task')
                        subject="New Task in OpenERP : "
                elif task.state=='cancelled':
                    body= self.pool.get('email.smtpclient.email.template').select(cr, uid, 'task_cancelled')
                    subject="Task Cancelled in OpenERP : "
                if sub:
                    if sub=="Task Re Assigned :" :
                        body= self.pool.get('email.smtpclient.email.template').select(cr, uid, 'task_reassigned')
                        subject=sub
                        email_cc=email_cc+mail_cc
                    if sub=="Task Description Changed :" :
                        body= self.pool.get('email.smtpclient.email.template').select(cr, uid, 'task_des_changed')
                        subject=sub
                        email_cc=email_cc+mail_cc
                    if sub=="Task Reactivated in OpenERP :" :
                        body= self.pool.get('email.smtpclient.email.template').select(cr, uid, 'task_reopen')
                        subject=sub
                        email_cc=email_cc+mail_cc
                    if sub=="Task Work Updated :" :
                        body= self.pool.get('email.smtpclient.email.template').select(cr, uid, 'task_work_summary')
                        subject=sub
                        email_cc=email_cc+mail_cc

                smtpserver = self.pool.get('email.smtpclient').browse(cr, uid, smtpserver_id, context=False)
                email=COMMASPACE.join(email)
                email_cc=COMMASPACE.join(email_cc)
                

                task_id=self.pool.get('project.task').search(cr, uid, [('id','=',task.id)])
                u_id=self.pool.get('project.task').browse(cr, uid, task_id, context=False )
                
                created_user=u_id[0].create_uid.name
                current_action_user = self.pool.get('res.users').browse(cr, uid, uid, context=False )

                loc=4-int(task.priority)
                priority=task._columns['priority'].selection[loc][1]
                body = (body or smtpserver.body) or ''
                body = body and body.replace('__created_user__', created_user or '')
                body = body and body.replace('__current_action_user__', current_action_user.name or '')
                body = body and body.replace('__assigned_user__', assigned_user and assigned_user.name or '')
                body = body and body.replace('__project_manager__', project_manager and project_manager.name or '')
                body = body and body.replace('__web_url1__', str(company_id.web_client or 'http://localhost:8080/')+
                     "openerp/form/view?model=project.task&id=%d&ids=[%d]&domain=[('id','=',%d)]&db=%s"%(task.id,task.id,task.id,cr.dbname))
                body = body and body.replace('__task_summary__', task.name)
                body = body and body.replace('__task_description__', task.description or '')
                body = body and body.replace('__priority__', priority)
                if task.project_id:
                    body = body and body.replace('__project__', task.project_id.name)
                body = body and body.replace('__planned_hours__', str(task.planned_hours))
                body = body and body.replace('__hours_spent__', str(task.effective_hours))
                body = body and body.replace('__date_deadline__', task.date_deadline or '')
                body = body and body.replace('__start_date__', task.date_start or '')
                body = body and body.replace('__end_date__', task.date_end or '')
                body = body.replace('\n','<br/>')
                
                if subject=='Warning,  Task "Ending Date" has been reached :' :state = self.pool.get('email.smtpclient').send_email( cr,  uid, smtpserver_id,
                            email, 'Attention : '+' Task not completed :'+' '+'[' +task.project_id.name.encode('utf-8')+']'+' '+task.name.encode('utf-8'), body.encode('utf-8'), email_cc=email_cc )

                else:
                    if task.project_id:
                        state = self.pool.get('email.smtpclient').send_email( cr,  uid, smtpserver_id,
                                email, _(subject)+' '+'[' +task.project_id.name.encode('utf-8')+']'+' '+task.name.encode('utf-8'), body.encode('utf-8'), email_cc=email_cc)
                    else:
                        state = self.pool.get('email.smtpclient').send_email( cr,  uid, smtpserver_id,
                                email, _(subject)+' '+task.name.encode('utf-8'), body.encode('utf-8'), email_cc=email_cc)
                cr.commit()

                if not state:
                    raise Exception, _('Verification failed, Please check the Server Configuration!')
        return {}

    def task_email_scheduled_action(self, cr, uid, ids=False, context={}):
        for tasks in self.pool.get('project.task').search(cr, uid, [('state','=','open')]):
            task=self.pool.get('project.task').browse(cr,uid,tasks)
            cr_date=task.date_end
            current_date=time.strftime('%Y-%m-%d %H:%M:%S')
            if cr_date:
                dif2=comp_dates2(cr_date,current_date)
                if task.work_ids==[]:
                    if dif2 > 3600:
                        print 'Sending Warning E-mail',task.name
                        sub='Warning,  Task "Ending Date" has been reached :'
                        self.send_mail(cr, uid, [tasks], [], sub, [])
        return {}


task()