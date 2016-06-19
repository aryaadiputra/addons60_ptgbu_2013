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

class cash_advance(osv.osv):
    _inherit = "cash.advance"
    _description = "Cash Advance mail sched"
    
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
       
    def check_adv(self, cr, uid, ids=False, context=None):
        print "_check_adv"
        smtp = self.pool.get('email.smtpclient')
        smtpserver_id = self.pool.get('email.smtpclient').select(cr, uid, 'default')
        
        adv_obj = self.pool.get('cash.advance')
        adv_ids = adv_obj.search(cr, uid, [])
        
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
        host = str(company.web_client or 'http://localhost:9090')

        cr.execute("""select state from cash_advance where state not in ('cancel','posted') group by state""")
        all_state = cr.fetchall()
        for states in all_state:
            print "states------------------->>", states[0]
            state = states[0]
            #print "state-----------------MM", state
            if state == 'draft':
                cr.execute("""select user_id from cash_advance where state = '%s' group by user_id"""% state)
                print "11111111111"
                print "11111111111", state
            elif state in ('approve'):
                print "2222222222222"
                print "222222222222", state
                cr.execute("""select department_id from cash_advance where state = '%s' group by department_id"""% state)
#            elif state in ('lv_2'):
#                cr.execute("""select division_rel_employee from material_requisition where state = '%s' group by division_rel_employee"""% state)
#            else:
#                return True
            #grouping_state = cr.fetchall()
            
            try:
                grouping_state = cr.fetchall()
            except Exception,e:
                continue

            
            for adv_res in grouping_state:
                res = adv_res[0]
                #print "USER ", mr_user_id
                if state == 'draft':
                    adv_search = adv_obj.search(cr, uid, [('state','=',state),('user_id','=',res)])
                elif state in ('approve'):
                    adv_search = adv_obj.search(cr, uid, [('state','=',state),('department_id','=',res)])
#                elif state in ('lv_2'):
#                    mr_search = mr_obj.search(cr, uid, [('state','=',state),('division_rel_employee','=',res)])
#                else:
#                    return True
                #print "XXXXXXXXXXXXXXXXXX", mr_search
                if not adv_search:
                    return True
                adv_browse  = adv_obj.browse(cr, uid, adv_search)
                subjects    = ""
                bodys       = ""
                line_mails  = ""
                no   = 0
                last_app    = "/"
                
                
                for adv in adv_browse:
                    tot = 0
                    no += 1
                    #print "ID---------->>", mr.id
                    email   = "/"
                    adv_to   = "/"
                    if state == 'draft':
                        email       = adv.user_id.user_email or "/"
                    elif state == 'approve':
                        email       = adv.employee_id.department_id.division_id.manager_id.user_id.user_email or "/"
                        
                    url         = str('%sopenerp/form/view?model=cash.advance&id=%d&ids=[%d]&db=%s\n'% (host,adv.id,adv.id,cr.dbname))
                    #print "url------------------->>", url
                    href        = str('<a href=%s>Approve</a>')%  url
                    
                    advance_number  = adv.number
                    req_date        = adv.req_date
                    employee_req    = adv.employee_id.name
                    approval_to     = adv.employee_id.department_id.division_id.manager_id.name
                    advance_desc    = adv.name
                    advance_total   = adv.amount
                    
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
                                    </tr>'''% (no,advance_number,req_date,employee_req,approval_to,advance_desc,advance_total,href)
                                                
                    
                    line_mails = line_mails +" "+line_mail
                    #subjects    = subjects + ", " + mr_number
                    subjects    = "Cash Advance Request"
                    #bodys       = bodys +'\n' + body
                
                bodys = '''
                        <table border="1">
     
                            <tr>
                                <td bgcolor="#CCCCCC">No.</td>
                                <td bgcolor="#CCCCCC">Referensi</td>
                                <td bgcolor="#CCCCCC">Request Date</td>
                                <td bgcolor="#CCCCCC">Employee</td>
                                <td bgcolor="#CCCCCC">Approval Untuk</td>
                                <td bgcolor="#CCCCCC">Description</td>
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
cash_advance()
