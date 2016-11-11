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

import os
import sys
import bz2

import time
from datetime import datetime
from datetime import timedelta

import release
import socket

import base64
import binascii

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

import netsvc
import pooler
import tools

from osv import fields
from osv import osv
from tools.translate import _

class smtpclient(osv.osv):

    _inherit = 'email.smtpclient'
    
    _columns = {
       'type' : fields.selection([("default", "Default"),("account", "Account"),("sale","Sale"),("stock","Stock"),("task","Task"),], "Server Type",required=True),
    }
    
    def send_email(self, cr, uid, server_id, emailto, subject, body='', attachments=[], reports=[], ir_attach=[], charset='utf-8', headers={}, context={},email_cc=[], email_bcc=[]):
        ################## Added CC and BCC as arguments of the function - By Vishnu on 2011-06-17 ########################
        if not emailto:
            raise osv.except_osv(_('SMTP Data Error !'), _('Email TO Address not Defined !'))
        
        def createReport(cr, uid, report, ids, name=False):
            files = []
            for id in ids:
                try:
                    service = netsvc.LocalService(report)
                    (result, format) = service.create(cr, uid, [id], {}, {})
                    if not name:
                        report_file = '/tmp/reports'+ str(id) + '.pdf'
                    else:
                        report_file = name
                    
                    fp = open(report_file,'wb+')
                    fp.write(result);
                    fp.close();
                    files += [report_file]    
                except Exception,e:
                    continue        
            return files
        
        smtp_server = self.browse(cr, uid, server_id)
        if smtp_server.state != 'confirm':
            raise osv.except_osv(_('SMTP Server Error !'), _('Server is not Verified, Please Verify the Server !'))
        
        if not subject:
            subject = "OpenERP Email: [Unknown Subject]"
            
        try:
            subject = subject.encode(charset)
        except:
            subject = subject.decode()   

        #attachment from Reports
        for rpt in reports:
            if len(rpt) == 3:
                rpt_file = createReport(cr, uid, rpt[0], rpt[1], rpt[2])
            elif len(rpt) == 2:
                rpt_file = createReport(cr, uid, rpt[0], rpt[1])
            attachments += rpt_file
        
        if isinstance(emailto, str) or isinstance(emailto, unicode):
            emailto = [emailto]

        ir_pool = self.pool.get('ir.attachment')

        for to in emailto:
            msg = MIMEMultipart()
            msg['Subject'] = tools.ustr(subject) 
            msg['To'] =  to
            #### Added CC and BCC - By Vishnu on 2011-06-17
            if email_cc:
                msg['Cc'] = email_cc
            if email_bcc:
                msg['Bcc'] = email_bcc
            
            #msg['From'] = context.get('email_from', smtp_server.from_email)
            msg['From'] = smtp_server.from_email
            
            if body == False:
                body = ''
                            
            if smtp_server.disclaimers:
                body = body + "\n" + smtp_server.disclaimers
                
            try:
                msg.attach(MIMEText(body.encode(charset) or '', _charset=charset, _subtype="html"))
            except:
                msg.attach(MIMEText(body or '', _charset=charset, _subtype="html"))    
            
            #add custom headers to email
            for hk in headers.keys():
                msg[hk] = headers[hk]

            for hk in smtp_server.header_ids:
                msg[hk.key] = hk.value
              
            context_headers = context.get('headers', [])
            for hk in context_headers:
                msg[hk] = context_headers[hk]
            
            # Add OpenERP Server information
            msg['X-Generated-By'] = 'OpenERP (http://www.openerp.com)'
            msg['X-OpenERP-Server-Host'] = socket.gethostname()
            msg['X-OpenERP-Server-Version'] = release.version
            msg['Message-Id'] = "<%s-openerp-@%s>" % (time.time(), socket.gethostname())
            
            if smtp_server.cc_to:
                msg['Cc'] = smtp_server.cc_to
                
            if smtp_server.bcc_to:
                msg['Bcc'] = smtp_server.bcc_to
            
            #attach files from disc
            for file in attachments:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(file,"rb").read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
                msg.attach(part)
            
            #attach files from ir_attachments
            for ath in ir_pool.browse(cr, uid, ir_attach):
                part = MIMEBase('application', "octet-stream")
                datas = base64.decodestring(ath.datas)
                part.set_payload(datas)
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' %(ath.name))
                msg.attach(part)
            
            message = msg.as_string()
            data = {
                'to':to,
                'server_id':server_id,
                'cc':smtp_server.cc_to or False,
                'bcc':smtp_server.bcc_to or False,
                'name':subject,
                'body':body,
                'serialized_message':message,
                'priority':smtp_server.priority,
                'cc':'Cc' in msg and msg['Cc'] or '',
                'bcc':'Bcc' in msg and msg['Bcc'] or '',
                'type' : 'system',
            }
            
            self.create_queue_enrty(cr, uid, data, context)
            
        return True
smtpclient()

