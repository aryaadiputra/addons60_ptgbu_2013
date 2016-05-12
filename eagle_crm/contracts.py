# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_crm
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
##############################################################################
#	
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.	 
#
##############################################################################

import netsvc
from osv import fields, osv
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import tools
from tools.translate import _
import decimal_precision as dp
from crm import crm

class eagle_contract( osv.osv ):
	_inherit = 'eagle.contract'

	def __init__(self, pool, cr):
		super( eagle_contract, self ).__init__(pool, cr)
		funcs = [ 
			('inst','do_contract_crm_installation'),
			]
		for func_item in funcs:
			self.register_event_function( cr, 'Eagle CRM', func_item[0], func_item[1] )
			
	def get_view_selections(self, cr, uid, context={}):
		lst = super( eagle_contract, self ).get_view_selections(cr, uid, context=context)
		return lst+[('crm','CRM')]

	def get_active_tabs(self, cr, uid, cnt_ids, field_name, args, context={}):
		res = {}
		eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
		tabs = False
		if eagle_param:
			if not eagle_param.show_all_meta_tabs:
				if eagle_param.tabs:
					tabs = eagle_param.tabs.split(';')
				user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
				if user and user.eagle_tabs:
					tabs = user.eagle_tabs.split(';')
		if not tabs:
			tabs = []
			for item in self.get_view_selections(cr, uid, context=context):
				tabs.append(item[0])
		tab_name = field_name.split('_')[1]
		val = tab_name in tabs

		if cnt_ids:
			for cnt_id in cnt_ids:
				res[cnt_id] = val
		else:
			res = val
			
		netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "get_active_tabs() called with field_name="+str(field_name)+", returning: "+str(res))
		
		return res

	_columns = {
		'opportunity_ids': fields.one2many('crm.lead', 'contract_id', 'Opportunities', domain=[('type','=','opportunity')]),
		'meetings': fields.one2many('crm.meeting', 'contract_id', 'Phone Calle'),
		'phonecalls': fields.one2many('crm.phonecall', 'contract_id', 'Phone Calle'),
		'issues': fields.one2many( 'project.issue', 'contract_id','Contracts issue' ),
		'view_selection': fields.selection( get_view_selections, 'View selection' ),
		'claims': fields.one2many('crm.claim', 'contract_id', 'Claim'),
		'sav_mode': fields.boolean( 'SAV Mode' ),
		'activeTab_crm': fields.function( get_active_tabs, method=True, type='boolean', string="Active tab: account" ),
	}

	# Start the installation
	def do_contract_crm_installation( self, cr, uid, cnt_ids, context={} ):
		netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "do_contract_crm_installation() called" )

	# Activate the "CRM" tabs
	def button_view_crm(self, cr, uid, ids, context={}):
		self.write( cr,uid,ids,{'view_selection':'crm'} )
		return True
		
	def run_crm_leads_scheduler( self, cr, uid, days_for_late=7, context={} ):
		''' Runs CRM scheduler.
		'''
		if not context:
			context={}
		opportunities = self.pool.get('crm.lead')
		
		self_name = 'Eagle CRM Scheduler'
		for contract in self.browse( cr, uid, self.search( cr, uid, [], context=context ), context=context ):
			if contract.state not in ['draft']: 
 				netsvc.Logger().notifyChannel( self_name, netsvc.LOG_DEBUG, "Contract state is '%s', skipping it" % contract.state )
				continue

			netsvc.Logger().notifyChannel( self_name, netsvc.LOG_DEBUG, "Checking the opportunites of the contract '%s' ,days=%d" % (contract.name,days_for_late) )
			q_base_phone = "select count(*) from crm_phonecall where contract_id="+str(contract.id)+" and %s"
			q_base_meeting = "select count(*) from crm_meeting where  contract_id="+str(contract.id)+" and %s"
			date_now = datetime.now().strftime( '%Y-%m-%d' )
			date_target = (datetime.now() - relativedelta(days=days_for_late)).strftime( '%Y-%m-%d' )

			for opportunity in contract.opportunity_ids:

				# Default state is very old			
				opport_state = 'old'
	
				# Count for late items
				q_end = "opportunity_id=%d and date < '%s' and date >= '%s'" % (opportunity.id, date_now, date_target)
				q = 0
				cr.execute( q_base_phone % (q_end,) )
				row = cr.fetchone()
				if row: 
					q = row[0]
					netsvc.Logger().notifyChannel( self_name, netsvc.LOG_DEBUG, "    ** Late phone calls detected: "+str(row[0]) )
				cr.execute( q_base_meeting % (q_end,) )
				row = cr.fetchone()
				if row: 
					q += row[0]
					netsvc.Logger().notifyChannel( self_name, netsvc.LOG_DEBUG, "    ** Late meetings detected: "+str(row[0]) )
				if q > 0:
					opport_state = 'late'
	
				# Count for running items
				q_end = "opportunity_id=%d and date >= '%s'" % (opportunity.id, date_now)
				q = 0
				cr.execute( q_base_phone % (q_end,) )
				row = cr.fetchone()
				if row: 
					q = row[0]
					netsvc.Logger().notifyChannel( self_name, netsvc.LOG_DEBUG, "    ** Running phone calls detected: "+str(row[0]) )
				cr.execute( q_base_meeting % (q_end,) )
				row = cr.fetchone()
				if row: 
					q += row[0]
					netsvc.Logger().notifyChannel( self_name, netsvc.LOG_DEBUG, "    ** Running meetings detected: "+str(row[0]) )
				if q > 0:
					opport_state = 'running'
				
				netsvc.Logger().notifyChannel( self_name, netsvc.LOG_DEBUG, "    ** New opportunity state: "+str(opport_state) )
				opportunities.write(cr, uid, opportunity.id, {'lead_statut':opport_state}, context=context)
				
		return True

	def manage_sav_mode( self, cr, uid, contract_ids, context=None ):

		if context is None:
			context = { 'lang': self.pool.get('res.users').browse(cr,uid,uid).context_lang }
		for contract in self.browse( cr, uid, contract_ids, context=context ):
			if contract.state not in ['installation','production']: continue

			sav_mode = False
			for claim in contract.claims:
				if claim.state in [crm.AVAILABLE_STATES[1][0],crm.AVAILABLE_STATES[4][0]]: # Open,Pending
					sav_mode = True
					break
			
			if not sav_mode:
				# issues that have generated a task are in 'pending' state
				for issue in contract.issues:
					if issue.state not in ['cancel','done']:
						sav_mode = True
						break
			
			self.write( cr, uid, [contract.id], { 'sav_mode': sav_mode }, context=context )
			netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, " Contract '"+contract.name+"' is "+(sav_mode and '' or 'not ')+"in SAV mode" )

		return True

	def conditional_close_contract():
		netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "conditional_close_contract(...) called" )
		if not contract_ids:
			netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "conditional_close_contract(...) cancelled by 1" )
			return False
		if not len(contract_ids):
			netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, "conditional_close_contract(...) cancelled by 2" )
			return False

		ret = False
		if context is None:
			context = { 'lang': self.pool.get('res.users').browse(cr,uid,uid).context_lang }
		for contract in self.browse( cr, uid, contract_ids, context=context ):
			close_it = True
			open_it = True
			for opp in contract.opportunity_ids:
				if opp.probability > 0.0:
					close_it = False
				if opp.probability == 0.0:
					open_it = False

			if close_it:
				if not open_it:
					self.contract_close( cr, uid, contract.id, context=context )
					ret = True 
			elif open_it:
				self.contract_installation( cr, uid, contract.id, context=context )
				ret = True 

				sav_mode = False
				for claim in contract.claims:
					if claim.state == crm.AVAILABLE_STATES[4][0]: # Pending
						sav_mode = True
						break
				
				if not sav_mode:
					# issues that have generated a task are in 'pending' state
					for issue in contract.issues:
						if issue.state not in ['cancel','done']:
							sav_mode = True
							break
				
				self.write( cr, uid, [contract.id], { 'sav_mode': sav_mode }, context=context )
				netsvc.Logger().notifyChannel( 'addons.'+self._name, netsvc.LOG_DEBUG, " Contract '"+contract.name+"' is "+(sav_mode and '' or 'not ')+"in SAV mode" )

		return ret

eagle_contract()
