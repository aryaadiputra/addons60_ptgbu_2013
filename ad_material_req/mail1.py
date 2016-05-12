from osv import fields, osv
import random
import smtplib
import mimetypes

from email import Encoders
from optparse import OptionParser
from email.Message import Message
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.Utils import COMMASPACE, formatdate

import decimal_precision as dp
from tools.translate import _

import netsvc
import pooler
import tools

from datetime import date, timedelta, datetime
import time

error_msg = {
    'not_active' : "Please activate Email Server, without activating you can not send Email(s).",
    'server_stop' : 'Please start Email Server, without starting  you can not send Email(s).',
    'server_not_confirm' : 'Please Verify Email Server, without verifying you can not send Email(s).'
}

logger = netsvc.Logger()


class res_users(osv.osv):
    _inherit = 'res.users'
    _description = 'Res Users'
    _columns = {
        'mr_draft'  : fields.boolean('Draft'),
        'mr_lv1'    : fields.boolean('Waiting Manager Approve'),
        'mr_lv2'    : fields.boolean('Waiting Kadiv Approve'),
        'mr_lv3'    : fields.boolean('Waitting CEO'),
        'mr_lv4'    : fields.boolean('Waitting Warehouse User'),
        'super_user': fields.boolean('Super User'),
    }
res_users()


class material_requisition(osv.osv):
    _inherit = "material.requisition"
    _description="Material Requisition inherit mail sched"
    
    def _check_mr(self, cr, uid, ids=False):
        #print "_check_invoice_"
        smtp = self.pool.get('email.smtpclient')
        smtpserver_id = self.pool.get('email.smtpclient').select(cr, uid, 'default')
        
        mr = self.pool.get('material.requisition')
        mr_ids = mr.search(cr, uid, [])
        
        user = self.pool.get('res.users')
        user_ids = user.search(cr, uid, [])
        #company_id = company.web_client
        comp = self.pool.get('res.company')
        company_id = comp.search(cr, uid, [])[0]
        company = comp.browse(cr, uid, company_id)
        
        mrs = []
        emails = []
#        drafts = []
#        approve_lv1 = []
#        approve_lv2 = []
#        approve_lv3 = []
#        approve_lv4 = []
#        for usr in user.browse(cr, uid, user_ids):
#            if usr.mr_draft:
#                drafts.append(usr.user_email)
#            if usr.mr_lv1:
#                approve_lv1.append(usr.user_email)
#            if usr.mr_lv2:
#                approve_lv2.append(usr.user_email)
#            if usr.mr_lv3:
#                approve_lv3.append(usr.user_email)
#            if usr.mr_lv4:
#                approve_lv4.append(usr.user_email)
        for mrx in mr.browse(cr, uid, mr_ids):
            print "****mrx",mrx.name,"\n\r"
            if mrx.state == 'draft':
                user_acc_id = self.pool.get('res.users').search(cr,uid,[('mr_draft','=',True),('context_department_id','=',mrx.department.id)])
                user_acc_dt = self.pool.get('res.users').browse(cr,uid,user_acc_id)
                print "draft",user_acc_dt
                for d in user_acc_dt:
                    #print "qqq",d,inv.number
                    body = 'MR Number __mr_number__\n'\
                           'Created by __creator__\n'\
                           'Requested by __req_employee__\n'\
                           'Department __department__\n'\
                           'Description __description__\n'\
                           'State __state__\n'\
                           'URL __web_url1__'
                    #for x in inv.invoice_line:
                        #items.append(x.name)
                    #print items
                        #body = body and body.replace('__line_name__', x.name or '')
                        #body = body and body.replace('__line_quantity__', x.quantity or '')
                        #body = body and body.replace('__line_price__', x.price_unit or '')
                    body = body and body.replace('__mr_number__', mrx.name or '')
                    body = body and body.replace('__creator__', mrx.user_id.name or '')
                    body = body and body.replace('__req_employee__', mrx.req_employee.resource_id.name or '')
                    body = body and body.replace('__department__', mrx.department.name or '')
                    body = body and body.replace('__description__', mrx.origin or '')
                    body = body and body.replace('__state__', 'Draft')
                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
                     "openerp/form/view?model=material.requisition&id=%d&ids=[%d]&db=%s"% (mrx.id,mrx.id,cr.dbname))
                    try:
                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
                    except:
                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
                    msg['Subject'] = 'MR no %s' % mrx.name or ''
                    message = msg.as_string()
                    mail = {'to': d.user_email,
                            'server_id': smtpserver_id,
                            'name': msg['Subject'],
                            'body': body,
                            'serialized_message':message,
                            'priority':1,
                            'type':'system'
                            }
                    emails.append(mail)
            elif mrx.state == 'lv_1':
                user_acc_id = self.pool.get('res.users').search(cr,uid,[('mr_lv1','=',True),('context_department_id','=',mrx.department.id)])
                user_acc_dt = self.pool.get('res.users').browse(cr,uid,user_acc_id)
                print "mr_lv1",user_acc_dt
                for d in user_acc_dt:
                    #print "qqq",d,inv.number
                    body = 'MR Number __mr_number__\n'\
                           'Created by __creator__\n'\
                           'Requested by __req_employee__\n'\
                           'Department __department__\n'\
                           'Description __description__\n'\
                           'State __state__\n'\
                           'URL __web_url1__'
                    #for x in inv.invoice_line:
                        #items.append(x.name)
                    #print items
                        #body = body and body.replace('__line_name__', x.name or '')
                        #body = body and body.replace('__line_quantity__', x.quantity or '')
                        #body = body and body.replace('__line_price__', x.price_unit or '')
                    body = body and body.replace('__mr_number__', mrx.name or '')
                    body = body and body.replace('__creator__', mrx.user_id.name or '')
                    body = body and body.replace('__req_employee__', mrx.req_employee.resource_id.name or '')
                    body = body and body.replace('__department__', mrx.department.name or '')
                    body = body and body.replace('__description__', mrx.origin or '')
                    body = body and body.replace('__state__', 'Waiting Manager Approve')
                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
                     "openerp/form/view?model=material.requisition&id=%d&ids=[%d]&db=%s"% (mrx.id,mrx.id,cr.dbname))
                    try:
                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
                    except:
                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
                    msg['Subject'] = 'MR no %s' % mrx.name or ''
                    message = msg.as_string()
                    mail = {'to': d.user_email,
                            'server_id': smtpserver_id,
                            'name': msg['Subject'],
                            'body': body,
                            'serialized_message':message,
                            'priority':1,
                            'type':'system'
                            }
                    emails.append(mail)
            elif mrx.state == 'lv_2':
                user_acc_id = self.pool.get('res.users').search(cr,uid,[('mr_lv2','=',True),('context_division_id','=',mrx.department.division_id.id)])
                user_acc_dt = self.pool.get('res.users').browse(cr,uid,user_acc_id)
                print "mr_lv2",user_acc_dt
                for d in user_acc_dt:
                    #print "qqq",d,inv.number
                    body = 'MR Number __mr_number__\n'\
                           'Created by __creator__\n'\
                           'Requested by __req_employee__\n'\
                           'Department __department__\n'\
                           'Description __description__\n'\
                           'State __state__\n'\
                           'URL __web_url1__'
                    #for x in inv.invoice_line:
                        #items.append(x.name)
                    #print items
                        #body = body and body.replace('__line_name__', x.name or '')
                        #body = body and body.replace('__line_quantity__', x.quantity or '')
                        #body = body and body.replace('__line_price__', x.price_unit or '')
                    body = body and body.replace('__mr_number__', mrx.name or '')
                    body = body and body.replace('__creator__', mrx.user_id.name or '')
                    body = body and body.replace('__req_employee__', mrx.req_employee.resource_id.name or '')
                    body = body and body.replace('__department__', mrx.department.name or '')
                    body = body and body.replace('__description__', mrx.origin or '')
                    body = body and body.replace('__state__', 'Waiting Kadiv Approve')
                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
                     "openerp/form/view?model=material.requisition&id=%d&ids=[%d]&db=%s"% (mrx.id,mrx.id,cr.dbname))
                    try:
                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
                    except:
                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
                    msg['Subject'] = 'MR no %s' % mrx.name or ''
                    message = msg.as_string()
                    mail = {'to': d.user_email,
                            'server_id': smtpserver_id,
                            'name': msg['Subject'],
                            'body': body,
                            'serialized_message':message,
                            'priority':1,
                            'type':'system'
                            }
                    emails.append(mail)
            elif mrx.state == 'lv_3':
                user_acc_id = self.pool.get('res.users').search(cr,uid,[('mr_lv3','=',True)])
                user_acc_dt = self.pool.get('res.users').browse(cr,uid,user_acc_id)
                print "mr_lv3",user_acc_dt
                for d in user_acc_dt:
                    #print "qqq",d,inv.number
                    body = 'MR Number __mr_number__\n'\
                           'Created by __creator__\n'\
                           'Requested by __req_employee__\n'\
                           'Department __department__\n'\
                           'Description __description__\n'\
                           'State __state__\n'\
                           'URL __web_url1__'
                    #for x in inv.invoice_line:
                        #items.append(x.name)
                    #print items
                        #body = body and body.replace('__line_name__', x.name or '')
                        #body = body and body.replace('__line_quantity__', x.quantity or '')
                        #body = body and body.replace('__line_price__', x.price_unit or '')
                    body = body and body.replace('__mr_number__', mrx.name or '')
                    body = body and body.replace('__creator__', mrx.user_id.name or '')
                    body = body and body.replace('__req_employee__', mrx.req_employee.resource_id.name or '')
                    body = body and body.replace('__department__', mrx.department.name or '')
                    body = body and body.replace('__description__', mrx.origin or '')
                    body = body and body.replace('__state__', 'Waiting CEO')
                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
                     "openerp/form/view?model=material.requisition&id=%d&ids=[%d]&db=%s"% (mrx.id,mrx.id,cr.dbname))
                    try:
                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
                    except:
                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
                    msg['Subject'] = 'MR no %s' % mrx.name or ''
                    message = msg.as_string()
                    mail = {'to': d.user_email,
                            'server_id': smtpserver_id,
                            'name': msg['Subject'],
                            'body': body,
                            'serialized_message':message,
                            'priority':1,
                            'type':'system'
                            }
                    emails.append(mail)
            elif mrx.state == 'lv_4':
                user_acc_id = self.pool.get('res.users').search(cr,uid,[('mr_lv4','=',True),('context_department_id','=',mrx.department.id)])
                user_acc_dt = self.pool.get('res.users').browse(cr,uid,user_acc_id)
                print "mr_lv4",user_acc_dt
                for d in user_acc_dt:
                    #print "qqq",d,inv.number
                    body = 'MR Number __mr_number__\n'\
                           'Created by __creator__\n'\
                           'Requested by __req_employee__\n'\
                           'Department __department__\n'\
                           'Description __description__\n'\
                           'State __state__\n'\
                           'URL __web_url1__'
                    #for x in inv.invoice_line:
                        #items.append(x.name)
                    #print items
                        #body = body and body.replace('__line_name__', x.name or '')
                        #body = body and body.replace('__line_quantity__', x.quantity or '')
                        #body = body and body.replace('__line_price__', x.price_unit or '')
                    body = body and body.replace('__mr_number__', mrx.name or '')
                    body = body and body.replace('__creator__', mrx.user_id.name or '')
                    body = body and body.replace('__req_employee__', mrx.req_employee.resource_id.name or '')
                    body = body and body.replace('__department__', mrx.department.name or '')
                    body = body and body.replace('__description__', mrx.origin or '')
                    body = body and body.replace('__state__', 'Waiting Warehouse User')
                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
                     "openerp/form/view?model=material.requisition&id=%d&ids=[%d]&db=%s"% (mrx.id,mrx.id,cr.dbname))
                    try:
                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
                    except:
                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
                    msg['Subject'] = 'MR no %s' % mrx.name or ''
                    message = msg.as_string()
                    mail = {'to': d.user_email,
                            'server_id': smtpserver_id,
                            'name': msg['Subject'],
                            'body': body,
                            'serialized_message':message,
                            'priority':1,
                            'type':'system'
                            }
                    emails.append(mail)
        queue = self.pool.get('email.smtpclient.queue')
        for e in emails:
            queue.create(cr, uid, e)
        return True
    
material_requisition()