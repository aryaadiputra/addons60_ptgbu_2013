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
        'draft': fields.boolean('Draft'),
        #'proforma': fields.boolean('Pro-forma'),
        #'proforma2': fields.boolean('Pro-forma'),
        #'wait_approve': fields.boolean('Waiting Approve'),
        #'approved': fields.boolean('Approved'),
        'open': fields.boolean('Open'),
        #'paid': fields.boolean('Paid'),
        #'cancel': fields.boolean('Cancelled'),
        'approve_lv2_1': fields.boolean('Waiting CEO Cost Control Approve'),
        'approve_lv2': fields.boolean('Waiting CFO Cost Control Approve'),
        'approve_lv3': fields.boolean('Waiting Treasury Approve'),
        'approve_lv4': fields.boolean('Waiting CFO Payment Approve'),
        'approve_lv5': fields.boolean('Waiting CEO Approve'),
        #'approve_lv6': fields.boolean('Approve Lv6'),
        #'approve_lv7': fields.boolean('Approve Lv7'),
    }
    
res_users()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _description = 'Account Invoice'
    
    def formatLang(self,cr,uid, value, digits=None, date=False, date_time=False, grouping=True, monetary=False,lang="en_US"):
        """format using the know cursor, language from localcontext"""
        #print "====================",digits,"--",date,"--",date_time,"--",grouping,"--",monetary
        if digits is None:
            digits = self.parser_instance.get_digits(value)
        if isinstance(value, (str, unicode)) and not value:
            return ''
        pool_lang = self.pool.get('res.lang')
        #lang = self.localcontext['lang']
        
        lang_ids = pool_lang.search(cr, uid, [('code','=',lang)])[0]
        lang_obj = pool_lang.browse(cr, uid, lang_ids)

        if date or date_time:
            if not str(value):
                return ''

            date_format = lang_obj.date_format
            parse_format = '%Y-%m-%d'
            if date_time:
                value=value.split('.')[0]
                date_format = date_format + " " + lang_obj.time_format
                parse_format = '%Y-%m-%d %H:%M:%S'
            if not isinstance(value, time.struct_time):
                return time.strftime(date_format, time.strptime(value, parse_format))

            else:
                date = datetime(*value.timetuple()[:6])
            return date.strftime(date_format)

        return lang_obj.format('%.' + str(digits) + 'f', value, grouping=grouping, monetary=monetary)
        
        
    def _check_invoice(self, cr, uid, ids=False):
        #print "_check_invoice_"
        smtp = self.pool.get('email.smtpclient')
        smtpserver_id = self.pool.get('email.smtpclient').select(cr, uid, 'default')
        
        invoice = self.pool.get('account.invoice')
        invoice_ids = invoice.search(cr, uid, [])
        
        user = self.pool.get('res.users')
        user_ids = user.search(cr, uid, [])
        #company_id = company.web_client
        comp = self.pool.get('res.company')
        company_id = comp.search(cr, uid, [])[0]
        company = comp.browse(cr, uid, company_id)
        
        invoices = []
        emails = []
        drafts = []
        opens = []
        approve_lv2s = []
        approve_lv2_1s = []
        approve_lv3s = []
        approve_lv4s = []
        approve_lv5s = []
        for usr in user.browse(cr, uid, user_ids):
            if usr.draft:
                drafts.append(usr.user_email)
            if usr.open:
                opens.append(usr.user_email)
            if usr.approve_lv2:
                approve_lv2s.append(usr.user_email)
            if usr.approve_lv2_1:
                approve_lv2_1s.append(usr.user_email)
            if usr.approve_lv3:
                approve_lv3s.append(usr.user_email)
            if usr.approve_lv4:
                approve_lv4s.append(usr.user_email)
            if usr.approve_lv5:
                approve_lv5s.append(usr.user_email)
        #print "xxxx",opens[0]
        items = []
        for inv in invoice.browse(cr, uid, invoice_ids):
            
            #########Selain CEo dimatikan###################
#            if inv.state == 'draft':
#                for d in drafts:
#                    #print "qqq",d,inv.number
#                    body = 'Invoice Number __invoice_number__\n'\
#                           'Supplier __supplier__\n'\
#                           'Due Date __date_due__\n'\
#                           'Amount __currency__ __amount__\n'\
#                           'State __state__\n'\
#                           'URL __web_url1__'
#                    #for x in inv.invoice_line:
#                        #items.append(x.name)
#                    #print items
#                        #body = body and body.replace('__line_name__', x.name or '')
#                        #body = body and body.replace('__line_quantity__', x.quantity or '')
#                        #body = body and body.replace('__line_price__', x.price_unit or '')
#                    body = body and body.replace('__invoice_number__', inv.number or '')
#                    body = body and body.replace('__supplier__', inv.partner_id.name or '')
#                    body = body and body.replace('__date_due__', inv.date_due or '')
#                    body = body and body.replace('__currency__', inv.currency_id.name or '')
#                    body = body and body.replace('__amount__', self.formatLang(cr,uid,inv.amount_total,digits=2,lang=inv.partner_id.lang) or 0)
#                    body = body and body.replace('__state__', 'Draft')
#                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
#                     "openerp/form/view?model=account.invoice&id=%d&ids=[%d]&db=%s"% (inv.id,inv.id,cr.dbname))
#                    try:
#                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
#                    except:
#                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
#                    msg['Subject'] = 'Invoice %s' % inv.number or ''
#                    message = msg.as_string()
#                    mail = {'to': d,
#                            'server_id': smtpserver_id,
#                            'name': msg['Subject'],
#                            'body': body,
#                            'serialized_message':message,
#                            'priority':1,
#                            'type':'system'
#                            }
#                    emails.append(mail)
#            if inv.state == 'open':
#                for o in opens:
#                    #print "open",o,inv.number
#                    body = 'Invoice Number __invoice_number__\nSupplier __supplier__\nDue Date __date_due__\nAmount __currency__ __amount__\nState __state__\nURL __web_url1__'
#                    body = body and body.replace('__invoice_number__', inv.number or '')
#                    body = body and body.replace('__supplier__', inv.partner_id.name or '')
#                    body = body and body.replace('__date_due__', inv.date_due or '')
#                    body = body and body.replace('__currency__', inv.currency_id.name or '')
#                    body = body and body.replace('__amount__', self.formatLang(cr,uid,inv.amount_total,digits=2,lang=inv.partner_id.lang) or 0)
#                    body = body and body.replace('__state__', 'Open')
#                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
#                     "openerp/form/view?model=account.invoice&id=%d&ids=[%d]&db=%s"% (inv.id,inv.id,cr.dbname))
#                    try:
#                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
#                    except:
#                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
#                    msg['Subject'] = 'Invoice %s' % inv.number or ''
#                    message = msg.as_string()
#                    mail = {'to': o,
#                            'server_id': smtpserver_id,
#                            'name': msg['Subject'],
#                            'body': body,
#                            'serialized_message':message,
#                            'priority':1,
#                            'type':'system'
#                            }
#                    emails.append(mail)
#            if inv.state == 'approve_lv2-1':
#                for a2_1 in approve_lv2_1s:
#                    #print "lvl2",a2,inv.number
#                    body = 'Invoice Number __invoice_number__\nSupplier __supplier__\nDue Date __date_due__\nAmount __currency__ __amount__\nState __state__\nURL __web_url1__'
#                    body = body and body.replace('__invoice_number__', inv.number or '')
#                    body = body and body.replace('__supplier__', inv.partner_id.name or '')
#                    body = body and body.replace('__date_due__', inv.date_due or '')
#                    body = body and body.replace('__currency__', inv.currency_id.name or '')
#                    body = body and body.replace('__amount__', self.formatLang(cr,uid,inv.amount_total,digits=2,lang=inv.partner_id.lang) or 0)
#                    body = body and body.replace('__state__', 'Waiting CEO Cost Control Approve')
#                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
#                     "openerp/form/view?model=account.invoice&id=%d&ids=[%d]&db=%s"% (inv.id,inv.id,cr.dbname))
#                    try:
#                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
#                    except:
#                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
#                    msg['Subject'] = 'Invoice %s' % inv.number or ''
#                    message = msg.as_string()
#                    mail = {'to': a2_1,
#                            'server_id': smtpserver_id,
#                            'name': msg['Subject'],
#                            'body': body,
#                            'serialized_message':message,
#                            'priority':1,
#                            'type':'system'
#                            }
#                    emails.append(mail)
#            if inv.state == 'approve_lv2':
#                for a2 in approve_lv2s:
#                    #print "lvl2",a2,inv.number
#                    body = 'Invoice Number __invoice_number__\nSupplier __supplier__\nDue Date __date_due__\nAmount __currency__ __amount__\nState __state__\nURL __web_url1__'
#                    body = body and body.replace('__invoice_number__', inv.number or '')
#                    body = body and body.replace('__supplier__', inv.partner_id.name or '')
#                    body = body and body.replace('__date_due__', inv.date_due or '')
#                    body = body and body.replace('__currency__', inv.currency_id.name or '')
#                    body = body and body.replace('__amount__', self.formatLang(cr,uid,inv.amount_total,digits=2,lang=inv.partner_id.lang) or 0)
#                    body = body and body.replace('__state__', 'Waiting CFO Cost Control Approve')
#                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
#                     "openerp/form/view?model=account.invoice&id=%d&ids=[%d]&db=%s"% (inv.id,inv.id,cr.dbname))
#                    try:
#                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
#                    except:
#                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
#                    msg['Subject'] = 'Invoice %s' % inv.number or ''
#                    message = msg.as_string()
#                    mail = {'to': a2,
#                            'server_id': smtpserver_id,
#                            'name': msg['Subject'],
#                            'body': body,
#                            'serialized_message':message,
#                            'priority':1,
#                            'type':'system'
#                            }
#                    emails.append(mail)
#            if inv.state == 'approve_lv3':
#                for a3 in approve_lv3s:
#                    #print "lvl3",a3,inv.number
#                    body = 'Invoice Number __invoice_number__\nSupplier __supplier__\nDue Date __date_due__\nAmount __currency__ __amount__\nState __state__\nURL __web_url1__'
#                    body = body and body.replace('__invoice_number__', inv.number or '')
#                    body = body and body.replace('__supplier__', inv.partner_id.name or '')
#                    body = body and body.replace('__date_due__', inv.date_due or '')
#                    body = body and body.replace('__currency__', inv.currency_id.name or '')
#                    body = body and body.replace('__amount__', self.formatLang(cr,uid,inv.amount_total,digits=2,lang=inv.partner_id.lang) or 0)
#                    body = body and body.replace('__state__', 'Waiting Treasury Approve')
#                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
#                     "openerp/form/view?model=account.invoice&id=%d&ids=[%d]&db=%s"% (inv.id,inv.id,cr.dbname))
#                    try:
#                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
#                    except:
#                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
#                    msg['Subject'] = 'Invoice %s' % inv.number or ''
#                    message = msg.as_string()
#                    mail = {'to': a3,
#                            'server_id': smtpserver_id,
#                            'name': msg['Subject'],
#                            'body': body,
#                            'serialized_message':message,
#                            'priority':1,
#                            'type':'system'
#                            }
#                    emails.append(mail)
#            if inv.state == 'approve_lv4':
#                for a4 in approve_lv4s:
#                    #print "lvl4",a4,inv.number
#                    body = 'Invoice Number __invoice_number__\nSupplier __supplier__\nDue Date __date_due__\nAmount __currency__ __amount__\nState __state__\nURL __web_url1__'
#                    body = body and body.replace('__invoice_number__', inv.number or '')
#                    body = body and body.replace('__supplier__', inv.partner_id.name or '')
#                    body = body and body.replace('__date_due__', inv.date_due or '')
#                    body = body and body.replace('__currency__', inv.currency_id.name or '')
#                    body = body and body.replace('__amount__', self.formatLang(cr,uid,inv.amount_total,digits=2,lang=inv.partner_id.lang) or 0)
#                    body = body and body.replace('__state__', 'Waiting CFO Payment Approve')
#                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
#                     "openerp/form/view?model=account.invoice&id=%d&ids=[%d]&db=%s"% (inv.id,inv.id,cr.dbname))
#                    try:
#                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
#                    except:
#                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
#                    msg['Subject'] = 'Invoice %s' % inv.number or ''
#                    message = msg.as_string()
#                    mail = {'to': a4,
#                            'server_id': smtpserver_id,
#                            'name': msg['Subject'],
#                            'body': body,
#                            'serialized_message':message,
#                            'priority':1,
#                            'type':'system'
#                            }
#                    emails.append(mail)
            if inv.state == 'approve_lv5':
                for a5 in approve_lv5s:
                    #print "lvl5",a5,inv.number
                    body = 'Invoice Number __invoice_number__\nSupplier __supplier__\nDue Date __date_due__\nAmount __currency__ __amount__\nState __state__\nURL __web_url1__'
                    body = body and body.replace('__invoice_number__', inv.number or '')
                    body = body and body.replace('__supplier__', inv.partner_id.name or '')
                    body = body and body.replace('__date_due__', inv.date_due or '')
                    body = body and body.replace('__currency__', inv.currency_id.name or '')
                    body = body and body.replace('__amount__', self.formatLang(cr,uid,inv.amount_total,digits=2,lang=inv.partner_id.lang) or 0)
                    body = body and body.replace('__state__', 'Waiting CEO Approve')
                    body = body and body.replace('__web_url1__', str(company.web_client or 'http://localhost:9090/')+
                     "openerp/form/view?model=account.invoice&id=%d&ids=[%d]&db=%s"% (inv.id,inv.id,cr.dbname))
                    try:
                        msg = MIMEText(body.encode('utf8') or '',_subtype='plain',_charset='utf-8')
                    except:
                        msg = MIMEText(body or '',_subtype='plain',_charset='utf-8')
                    msg['Subject'] = 'Invoice %s' % inv.number or ''
                    message = msg.as_string()
                    mail = {'to': a5,
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
account_invoice()
