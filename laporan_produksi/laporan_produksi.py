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

class laporanProduksi(osv.osv):
    _name="laporan.produksi"
    
    def _get_default_item_lines(self, cr, uid, context=None):
        res = []
        #curr = [100000, 50000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100]
        curr = [
                'OB - Daily',
                'OB - Month to Date',
                'Coal Getting - Daily',
                'Coal Getting - Month to Date',
                'ROM Stockpile', 
                'Coal Hauling - Daily',
                'Coal Hauling - Daily',
                'Coal Hauling - Month to Date',
                'Stockpile at Sta 5',
                'Mini Stockpile at Port',
                'Fuel Supply',
                'Fuel Stock',
                'Rain Fall', 'Slippery',
                ]
        
        

        for rs in curr:
            dct = {
                'name'  : rs,
                'value' : 0,
                'uom'   : False,
            }
            res.append(dct)
        return res
    
    _columns = {
                'name':fields.char('Laporan Produksi',size=64),
                'date':fields.date('Tanggal'),
                'period':fields.many2one('account.period','Period'),
                'production_line':fields.one2many('laporan.produksi.line','product_id','Product Lines'),
                #'employee_id':fields.many2one('hr.employee','Send To '),
                }
    
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
    
    
    def send_email(self, cr, uid, ids=False, context=None):
        print "_check_invoice_"
        smtp = self.pool.get('email.smtpclient')
        smtpserver_id = self.pool.get('email.smtpclient').select(cr, uid, 'default')
        
        comp = self.pool.get('res.company')
        company_id = comp.search(cr, uid, [])[0]
        company = comp.browse(cr, uid, company_id)
        no = 0
        emails = []
        subjects    = ""
        bodys       = ""
        line_mails  = ""
        
        host = str(company.web_client or 'http://localhost:9090')

                    
        for production in self.browse(cr, uid, ids, context=None):
            url         = str('%sopenerp/form/view?model=laporan.produksi&id=%d&ids=[%d]&db=%s\n'% (host,production.id,production.id,cr.dbname))
                    #print "url------------------->>", url
            href        = str('<a href=%s>Check To OpenERP System</a>')%  url
            for line in production.production_line:
                no += 1
                description = line.name
                prod_value  = line.value
                uom         = line.uom.name
                line_mail   =   '''<tr>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                                </tr>'''% (no,description,prod_value,uom)
                
                line_mails = line_mails +" "+line_mail
                #subjects    = subjects + ", " + mr_number
        
        
        subjects    = production.name
            #bodys       = bodys +'\n' + body
        
        bodys = '''
                <table border="1">

                    <tr>
                        <td bgcolor="#CCCCCC">No.</td>
                        <td bgcolor="#CCCCCC">Description</td>
                        <td bgcolor="#CCCCCC">Value</td>
                        <td bgcolor="#CCCCCC">Unit of Measure</td>
                    </tr>
                    %s
                </table>
                <br>%s'''% (line_mails, href)
        
            
        try:
            msg = MIMEText(bodys.encode('utf8') or '',_subtype='plain',_charset='utf-8')
        except:
            msg = MIMEText(bodys or '',_subtype='plain',_charset='utf-8')
        
        smtpserver_id = self.pool.get('email.smtpclient').select(cr, uid, 'default')
        msg['Subject'] = subjects or ''
        message = msg.as_string()
        email   = ['soebianto.erp@ptgbu.com','erwin.manurung@ptgbu.com']
        cc      = 'aryalemon.mail@gmail.com'
#        email = production.employee_id.work_email
#        if not email:
#            raise osv.except_osv(_('Error'), _('No Email In This Employee!')) 
        mail = {
                'to' : email,
                'cc' : cc,
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
        
    _defaults = {
            'production_line' : _get_default_item_lines,
                 }
    
laporanProduksi()

class laporanProduksiLine(osv.osv):
    _name="laporan.produksi.line"
    _columns = {
                'name':fields.char('Produk',size=64),
                'value': fields.float('Value'),
                #'uom': fields.char('Unit of Measure',size=64),
                'uom': fields.many2one('product.uom','Unit of Measure'),
                'product_id': fields.many2one('laporan.produksi','Laporan'),
                }
laporanProduksiLine()