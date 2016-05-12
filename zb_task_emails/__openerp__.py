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

{
    'name': 'Task E-mails ',
    'version': '1.0',
    'category': 'Generic Modules/Others',
    'description': """
    * This module allows user to send notification e-mails, related to tasks in OpenERP Project Management.
    * Notifications are sent to 'Assigned User' or 'Project Manager' upon various actions, changes and updates in a particular task 
    """,
    'author': 'Zesty Beanz Technologies Pvt Ltd',
    'depends': ['project','hr','smtpclient',],
    'init_xml': [],
    'update_xml': ['company_view.xml','smtpclient_view.xml','email_template_view.xml','project_view.xml',
                   'email_template_data.xml','security/ir.model.access.csv'],#
    'demo_xml': [],
    'installable': True,
    'active': False,
}