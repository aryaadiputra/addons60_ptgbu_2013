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
from datetime import datetime

error_msg = {
    'not_active' : "Please activate Email Server, without activating you can not send Email(s).",
    'server_stop' : 'Please start Email Server, without starting  you can not send Email(s).',
    'server_not_confirm' : 'Please Verify Email Server, without verifying you can not send Email(s).'
}

logger = netsvc.Logger()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _description = "Purchase Order inherit mail sched"
    
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
    
    def check_po_mail(self, cr, uid, ids=False, context=None):
        print "_check_invoice_"
        smtp = self.pool.get('email.smtpclient')
        smtpserver_id = self.pool.get('email.smtpclient').select(cr, uid, 'default')
        
        po_obj = self.pool.get('purchase.order')
        po_ids = po_obj.search(cr, uid, [])
        
        user = self.pool.get('res.users')
        user_ids = user.search(cr, uid, [('id', '=', 1)])
        #user_ids = user.search(cr, uid, [('mr_draft','<>',False)])
        
        #company_id = company.web_client
        comp = self.pool.get('res.company')
        company_id = comp.search(cr, uid, [])[0]
        company = comp.browse(cr, uid, company_id)
        
        mrs = []
        emails = []
        mr_id_all = []
        host = str(company.web_client or 'http://localhost:9090/')
        host = 'http://localhost:8080/'
        cr.execute("""select state from purchase_order where state not in ('cancel','done')group by state""")
        for states in cr.fetchall():
            #print "states------------------->>", states[0]
            state = states[0]
            print "state-----------------MM", state
            if state == 'confirmed4':
                print "AAAAAAAAAAAAA"
                cr.execute("""select delegate from purchase_order where state = '%s' group by delegate"""% state)
                #print "cr.fetchall()---------------------->>", cr.fetchall()
            else:
                continue
            for po_res in cr.fetchall():
                res = po_res[0]
                print "RS------------------------------->>", res
                #print "USER ", mr_user_id
                if state == 'confirmed4':
                    po_search = po_obj.search(cr, uid, [('state','=',state),('delegate','=',res)])
                    print "po_search------------------->>", po_search
                if not po_search:
                    return True
                po_browse = po_obj.browse(cr, uid, po_search)
                subjects    = ""
                bodys       = ""
                line_mails  = ""
                no   = 0
                last_app    = "/"
                
                
                for po in po_browse:
                    tot = 0
                    no += 1
                    #print "ID---------->>", mr.id
                    email   = "/"
                    po_to   = "/"
                    if state == 'confirmed4':
                        #email       = po.user_id.user_email or "/"
                        last_app    = po.date_order
                        #po_to       = po.user_id.name
                        po_to       = ""
                    
                        
                    email       = "soebianto.erp@ptgbu.com"
                    cur_date    = datetime.now().strftime('%Y-%m-%d')
                    last_app = last_app[:10]
                    #print "last_app------------------>>123", last_app
                    fmt = '%Y-%m-%d'
                    d2 = datetime.strptime(cur_date, fmt)
                    d1 = datetime.strptime(last_app, fmt)
                    
                    #daysDiff = (d2-d1).days
                    #print "daysDiff------------------------>>", mr.name, daysDiff
                    tot         = po.amount_total
                    po_last_app = last_app or '/'
                    po_number   = po.name
                    po_created  = po.delegate.name
                    po_to       = 'chief executive officer'
#                    if po.mr_number:
#                        po_req      = po.mr_number.req_employee.name
#                        po_dept     = po.mr_number.department.name
                    #else:
                    po_req = po.partner_id.name
                    po_dept = "/"
                    
                    po_desc     = po.mr_description
                    po_total    = self.formatLang(cr,uid,tot,digits=2,lang='en_US') or 0
                    #print "mr_total=====================??", mr_total
                    url         = str('%sopenerp/form/view?model=purchase.order&id=%d&ids=[%d]&db=%s\n'% (host,po.id,po.id,cr.dbname))
                    #print "url------------------->>", url
                    href        = str('<a href=%s>Approve</a>')%  url
                    
                    
                    line_mail   =   '''<tr>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>IDR</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                    </tr>'''% (no,po_number,"daysDiff",po_req,po_to,po_desc,po_total,href)
                    
                    line_mails = line_mails +" "+line_mail
                    #subjects    = subjects + ", " + mr_number
                    subjects    = "Purchase Order"
                    #bodys       = bodys +'\n' + body
                
                bodys = '''
                        <table border="1" style="border-collapse:collapse; font-size:10px" cellpadding="3">
     
                            <tr style='font-weight:bold'>
                                <td bgcolor="#CCCCCC">No.</td>
                                <td bgcolor="#CCCCCC">Referensi</td>
                                <td bgcolor="#CCCCCC">Days Since Last Approval</td>
                                <td bgcolor="#CCCCCC">Supplier/Partner/Employee</td>
                                <td bgcolor="#CCCCCC">Approval Untuk</td>
                                <td bgcolor="#CCCCCC">Description</td>
                                <td bgcolor="#CCCCCC">Currency</td>
                                <td bgcolor="#CCCCCC">Jumlah</td>
                                <td bgcolor="#CCCCCC">URL Link</td>
                            </tr>
                            %s
                        
                        </table>'''% line_mails
                
                    
                try:
                    msg = MIMEText(bodys.encode('utf8') or '',_subtype='plain',_charset='utf-8')
                except:
                    msg = MIMEText(bodys or '',_subtype='plain',_charset='utf-8')
                
                smtpserver_id = self.pool.get('email.smtpclient').select(cr, uid, 'default')
                msg['Subject'] = subjects or ''
                message = msg.as_string()
                        
                mail = {'to': email,
                        'server_id': smtpserver_id,
                        #'name': msg['Subject'],
                        'name': msg['Subject'],
                        'body': bodys,
                        'serialized_message':message,
                        'priority':1,
                        'type':'system'
                        }
            
                emails.append(mail)
                
                #queue = self.pool.get('email.smtpclient.queue')
                
                #queue.create(cr, uid, mail)
                
                p = pooler.get_pool(cr.dbname)
                
                smtpserver_id = p.get('email.smtpclient').search(cr, uid, [('type','=','default'),('state','=','confirm'),('active','=',True)], context=False)
                
                if smtpserver_id:
                    smtpserver_id = smtpserver_id[0]
                else:
                    raise osv.except_osv(_('Error'), _('No SMTP Server has been defined!'))
                attachments = []
                p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, email, msg['Subject'], bodys, attachments)
                
        return True
    
purchase_order()