# -*- coding: utf-8 -*-
#
#  File: requests.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2010 Open-Net Ltd. All rights reserved.
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

import netsvc
from osv import fields, osv
import tools
import time
from tools.translate import _

res_request_priorities = [
	('0','When possible (Low)'),
	('1','When possible (keep cool)'),
	('2','When possible (High)'),
	('3','Within a week'),
	('4','Tomorrow'),
	('5','Today')
]

class res_request( osv.osv ):
	_inherit = 'res.request'
	
	def __get_eagle_parameters( self, cr, uid, context={} ):
		params_obj = self.pool.get( 'eagle.config.params' )
		for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
			return params

		return False
	
	def _detect_can_send_mails(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		if context is None:
			context = {}

		ret = True
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		if not eagle_param or not eagle_param.send_mail_with_request:
			ret = False
		if not tools.config.get('smtp_server'):
			ret = False
		for id in ids:
			res[id] = ret

		return res

	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
		'priority': fields.selection( res_request_priorities, 'Priority', states={'closed':[('readonly',True)]}, required=True),
		'send_mail': fields.boolean('Send a mail with the response?'),
		'can_send_mails': fields.function( _detect_can_send_mails, method=True, type='boolean', string='Can send mails?', store=False ),
		'ons_current_user': fields.char( 'Current user', type='char', size=64),
		'ons_date_start': fields.datetime('Start date'),
		'is_in_progress': fields.boolean('Is in progress?'),
		'remarks': fields.text('Remarks'),
	}
	
	def _get_default_can_send_mails(self, cr, uid, context=None):
		if context is None:
			context = {}

		ret = True
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		if not eagle_param or not eagle_param.send_mail_with_request:
			ret = False
		if not tools.config.get('smtp_server'):
			ret = False

		return ret
	
	_defaults = {
		'can_send_mails': _get_default_can_send_mails,
		'is_in_progress': False,
	}

	
	def request_send(self, cr, uid, ids, context={}):
		res = super( res_request, self ).request_send( cr, uid, ids, context )

		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		if not eagle_param or not eagle_param.send_mail_with_request:
			netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "The request won't send any email because it's parameterized as is." )
			return res

		if not tools.config.get('smtp_server'):
			netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "The request can't send any email because there's no stmp server defined..." )
			return res

		for request in self.browse( cr, uid, ids ):
			if not request.send_mail: continue
			if not request.act_from.user_email: 
				netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "The request '%s' can't send any email because there's no email defined for the sender..." % request.name )
				continue
			if not request.act_to.user_email: 
				netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "The request '%s' can't send any email because there's no email defined for the recipient..." % request.name )
				continue
			netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "About to send an email to %s from %s with the following subject: %s" % (request.act_to.user_email,request.act_from.user_email,request.name) )
			levels = {
				'0':'When possible (Low)',
				'1':'When possible (keep cool)',
				'2':'When possible (High)',
				'3':'Within a week',
				'4':'Tomorrow',
				'5':'Today'}
			level = request.priority in levels and levels[request.priority] or ('Code: ' + str(request.priority))
			tools.email_send(
				email_from=request.act_from.user_email,
				email_to=[request.act_to.user_email],
				subject='['+level+'] '+request.name,
				body=request.body
				)
		return res
	
	def in_progress(self, cr, uid, ids, context={}):
		dt_now = time.strftime('%Y-%m-%d %H:%M:%S')
		user_name = self.pool.get('res.users').browse(cr,uid,uid).name
		self.write( cr,uid,ids,{'is_in_progress':True,'ons_current_user':user_name, 'ons_date_start':dt_now} )
		return True

	def stop_progress(self, cr, uid, ids, context={}):
		self.write( cr,uid,ids,{'is_in_progress':False,'ons_current_user':'', 'ons_date_start':False} )
		return True

res_request()

