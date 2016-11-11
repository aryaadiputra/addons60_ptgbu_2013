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
    _description = "Material Requisition inherit mail sched"
    
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
       
    def check_mr(self, cr, uid, ids=False, context=None):
        print "_check_invoice_"
        smtp = self.pool.get('email.smtpclient')
        smtpserver_id = self.pool.get('email.smtpclient').select(cr, uid, 'default')
        
        mr_obj = self.pool.get('material.requisition')
        mr_ids = mr_obj.search(cr, uid, [])
        
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

        cr.execute("""select state from material_requisition where state not in ('cancel','done')group by state""")
        for states in cr.fetchall():
            #print "states------------------->>", states[0]
            state = states[0]
            #print "state-----------------MM", state
            if state == 'draft':
                cr.execute("""select user_id from material_requisition where state = '%s' group by user_id"""% state)
            elif state in ('lv_1'):
                cr.execute("""select department from material_requisition where state = '%s' group by department"""% state)
            elif state in ('lv_2'):
                cr.execute("""select division_rel_employee from material_requisition where state = '%s' group by division_rel_employee"""% state)
#            else:
#                return True
            for mr_res in cr.fetchall():
                res = mr_res[0]
                #print "USER ", mr_user_id
                if state == 'draft':
                    mr_search = mr_obj.search(cr, uid, [('state','=',state),('user_id','=',res)])
                elif state in ('lv_1'):
                    mr_search = mr_obj.search(cr, uid, [('state','=',state),('department','=',res)])
                elif state in ('lv_2'):
                    mr_search = mr_obj.search(cr, uid, [('state','=',state),('division_rel_employee','=',res)])
#                else:
#                    return True
                #print "XXXXXXXXXXXXXXXXXX", mr_search
                if not mr_search:
                    return True
                mr_browse = mr_obj.browse(cr, uid, mr_search)
                subjects    = ""
                bodys       = ""
                line_mails  = ""
                no   = 0
                last_app    = "/"
                
                
                for mr in mr_browse:
                    tot = 0
                    no += 1
                    #print "ID---------->>", mr.id
                    email   = "/"
                    mr_to   = "/"
                    if state == 'draft':
                        email       = mr.user_id.user_email or "/"
                        last_app    = mr.date_start
                        mr_to       = mr.user_id.name
                    elif state == 'lv_1':
                        if mr.department :
                            if mr.department.manager_id:
                                email       = mr.department.manager_id.user_id.user_email
                                mr_to       = mr.department.manager_id.user_id.name
                        last_app    = mr.user_app
                    elif state == 'lv_2':
                        if mr.department:
                            if mr.department.division_id:
                                if mr.department.division_id.manager_id:
                                    email       = mr.department.division_id.manager_id.user_id.user_email
                                    mr_to       = mr.department.division_id.manager_id.user_id.name
                        last_app    = mr.manager_app
                    
                    for line_mr in mr.line_ids:
                        tot += line_mr.product_qty * line_mr.price
                        
                    #email       = "arya@adsoft.co.id"
                    cur_date    = datetime.now().strftime('%Y-%m-%d')
                    last_app = last_app[:10]
                    #print "last_app------------------>>123", last_app
                    fmt = '%Y-%m-%d'
                    d2 = datetime.strptime(cur_date, fmt)
                    d1 = datetime.strptime(last_app, fmt)
                    
                    daysDiff = (d2-d1).days
                    print "daysDiff------------------------>>", mr.name, daysDiff
                    
                    mr_last_app = last_app or '/'
                    mr_number   = mr.name
                    mr_created  = mr.user_id.name
                    mr_req      = mr.req_employee.name
                    mr_dept     = mr.department.name
                    mr_desc     = mr.origin
                    mr_total    = self.formatLang(cr,uid,tot,digits=2,lang='en_US') or 0
                    #print "mr_total=====================??", mr_total
                    url         = str('%sopenerp/form/view?model=material.requisition&id=%d&ids=[%d]&db=%s\n'% (host,mr.id,mr.id,cr.dbname))
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
                                    </tr>'''% (no,mr_number,daysDiff,mr_req,mr_to,mr_desc,mr_total,href)
                    
                    line_mails = line_mails +" "+line_mail
                    #subjects    = subjects + ", " + mr_number
                    subjects    = "Material Request"
                    #bodys       = bodys +'\n' + body
                
                bodys = '''
                        <table border="1">
     
                            <tr>
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
material_requisition()
