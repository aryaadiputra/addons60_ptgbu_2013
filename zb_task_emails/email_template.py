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

from osv import fields,osv
import pooler
from tools.translate import _


class SmtpClientEmailTemplate(osv.osv):
    _name = 'email.smtpclient.email.template'
    _description = 'Email Template'
    _columns = {
        'name': fields.selection([
            ('task','Task'),
            ('task_complete','Task (Completed)'),('task_pending','Task (Pending)'),('task_reassigned','Task (Re Assigned)'),('task_des_changed','Task (Des Changed)'),
            ('task_reopen','Task (Re Activated)'),('task_work_summary','Task (Work Summary)'),('task_cancelled','Task(Cancelled)'),('task_warning','Task Warning'),],'Type', size=32, required=True),
        'body' : fields.text('Message'),
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Type of the Email Template must be unique !')
    ]

    def select(self, cr, uid, type):
        pool = self.pool.get('email.smtpclient.email.template')
        ids = pool.search(cr, uid, [('name','=',type)], context=False)
        if not ids:
            return False
        return pool.browse(cr, uid, ids[0]).body
SmtpClientEmailTemplate()