# -*- coding: utf-8 -*-
#
#  File: claims.py
#  Module: eagle_crm
#
#  Created by sbe@open-net.ch
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

class crm_claim(osv.osv):
	_inherit = 'crm.claim'
	
	_columns = {
		'contract_id': fields.many2one( 'eagle.contract', 'Contract', domain=[('state','in',['installation','production'])] ),
		#'partner_id': fields.many2one('res.partner', 'Partner',  domain="[('contract_ids', '=', contract_id)]"),
	}
	
	
		
	def onchange_contract_id(self, cr, uid, ids, cont_id, part=False):
		ret = { 'value': {} }
		partner_id  = False
		contract = self.pool.get('eagle.contract').browse( cr, uid, cont_id, context={} )
		if contract:
			partner_id = contract.customer_id and contract.customer_id.id or False
		
		ret['partner_id'] = partner_id

		return { 'value': ret }
	
	def create(self, cr, uid, vals, context=None):
		ret = super( crm_claim, self ).create( cr, uid, vals, context=context )

		contract_id = vals.get('contract_id', False)
		if contract_id:
			self.pool.get('eagle.contract').manage_sav_mode( cr, uid, [contract_id], context=context )

		return ret

	def write(self, cr, uid, ids, vals, context=None):
		ret = super( crm_claim, self ).write( cr, uid, ids, vals, context=context )
		
		if isinstance(ids,(int,long)): ids = [ids]

		contract_id = vals.get('contract_id', False)
		if contract_id:
			self.pool.get('eagle.contract').manage_sav_mode( cr, uid, [contract_id], context=context )
		else:
			issue_state = vals.get( 'state', False )
			if issue_state:
				todo = []
				for issue in self.browse( cr, uid, ids, context=context ):
					if issue.contract_id:
						todo.append(issue.contract_id.id)
				if len(todo) > 0:
					self.pool.get('eagle.contract').manage_sav_mode( cr, uid, todo, context=context )

		return ret

crm_claim()
