# -*- coding: utf-8 -*-
#
#  File: opportunities.py
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

from osv import osv,fields
import netsvc
import datetime
from tools.translate import _

class crm_opportunity(osv.osv):
	_inherit = 'crm.lead'
	
	def conditional_close_contract( self, cr, uid, contract_ids ):
		return self.pool.get( 'eagle.contract' ).conditional_close_contract( cr, uid, contract_ids )

	def eagle_crm_case_close(self, cr, uid, ids, *args):
		"""Overrides close for crm_case for setting probability and close date
		@param self: The object pointer
		@param cr: the current row, from the database cursor,
		@param uid: the current user’s ID for security checks,
		@param ids: List of case Ids
		@param *args: Tuple Value for additional Params
		"""
		res = self._case_close_generic(cr, uid, ids, self._find_won_stage, *args)
		context = { 'lang': self.pool.get('res.users').browse(cr,uid,uid).context_lang }

		create_contract = False
		eagle_param = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
		if eagle_param and hasattr(eagle_param,'opport_2_contract_mode'):
			if eagle_param.opport_2_contract_mode == 'win':
				create_contract = True

		contracts_to_check = []
		for (id, name) in self.name_get(cr, uid, ids):
			opp = self.browse(cr, uid, id)
			if opp.type == 'opportunity':
				message = _("The opportunity '%s' has been won.") % name
				if opp.contract_id:
					ret = contracts_to_check.append(opp.contract_id.id)
					if ret: 
						message += _("The contract '%s' has been set to Production") % opp.contract_id.name
				elif create_contract:
					partner = opp.partner_id or (opp.partner_address_id and opp.partner_address_id.partner_id) or False
					if partner:
						vals = {
							'name': opp.name,
							'customer_id': partner.id,
						}
						if partner.property_product_pricelist:
							vals['pricelist_id'] = partner.property_product_pricelist.id
						contract_id = self.pool.get('eagle.contract').create(cr, uid, vals, context=context)
						if contract_id:
							self.write( cr, uid, [id], {'contract_id': contract_id}, context=context )
							message += _("The contract '%s' has been created, it will be set to Production") % opp.name

				self.log(cr, uid, id, message)
		
		if len(contracts_to_check):
			self.conditional_close_contract( cr, uid, contracts_to_check )
		return res

	def eagle_crm_case_mark_lost(self, cr, uid, ids, *args):
		"""Mark the case as lost: state = done and probability = 0%
		@param self: The object pointer
		@param cr: the current row, from the database cursor,
		@param uid: the current user’s ID for security checks,
		@param ids: List of case Ids
		@param *args: Tuple Value for additional Params
		"""
		res = self._case_close_generic(cr, uid, ids, self._find_lost_stage, *args)
		context = { 'lang': self.pool.get('res.users').browse(cr,uid,uid).context_lang }
		
		contracts_to_check = []		
		for (id, name) in self.name_get(cr, uid, ids):
			opp = self.browse(cr, uid, id)
			if opp.type == 'opportunity':
				message = _("The opportunity '%s' has been marked as lost.") % name
				if opp.contract_id:
					ret = contracts_to_check.append(opp.contract_id.id)
					if ret: 
						message += _("The contract '%s'has been set to Production") % opp.contract_id.name
				self.log(cr, uid, id, message)
		
		if len(contracts_to_check):
			self.conditional_close_contract( cr, uid, contracts_to_check )
		return res

	def case_open(self, cr, uid, ids, *args):
		"""Overrides open for crm_case for setting Open Date
		@param self: The object pointer
		@param cr: the current row, from the database cursor,
		@param uid: the current user’s ID for security checks,
		@param ids: List of case's Ids
		@param *args: Give Tuple Value
		"""

		create_contract = False
		eagle_param = self.pool.get('eagle.config.params').get_instance(cr, uid)
		if eagle_param and hasattr(eagle_param,'opport_2_contract_mode'):
			if eagle_param.opport_2_contract_mode == 'creation':
				create_contract = True

		todo = []
		if create_contract:
			leads = self.browse(cr, uid, ids)
			for i in xrange(0, len(ids)): 
				if leads[i].type == 'opportunity' and not leads[i].contract_id:
					todo.append(leads[i].id)
		
		res = super(crm_opportunity, self).case_open(cr, uid, ids, *args)
		
		if res:
			for id in todo:
				opp = self.browse( cr, uid, id )
				if not opp: continue
				partner = opp.partner_id or (opp.partner_address_id and opp.partner_address_id.partner_id) or False
				if not partner: continue
				vals = {
					'name': opp.name,
					'customer_id': partner.id,
				}
				if partner.property_product_pricelist:
					vals['pricelist_id'] = partner.property_product_pricelist.id
				contract_id = self.pool.get('eagle.contract').create(cr, uid, vals)
				if contract_id:
					self.write( cr, uid, [id], {'contract_id':contract_id} )
		
		return res

crm_opportunity()
