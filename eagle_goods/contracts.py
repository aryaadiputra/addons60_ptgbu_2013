# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_goods
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
from tools.translate import _

class eagle_contract( osv.osv ):
	_inherit = 'eagle.contract'

	def get_view_selections(self, cr, uid, context={}):
		# The result looks like this:
		#	[('contract', 'Contract'), ('account', 'Accounting'), ('crm', 'CRM'), ('moves', 'Stock Moves')]
		lst = super( eagle_contract, self ).get_view_selections( cr, uid, context )
		lst += [('goods','Goods Management')]

		return lst

	def get_active_tabs(self, cr, uid, cnt_ids, field_name, args, context={}):
		return super( eagle_contract, self).get_active_tabs(cr, uid, cnt_ids, field_name, args, context=context)

	_columns = {
		'goods_ids': fields.one2many( 'eagle.good.object', 'contract_id', 'Goods', select=True ),
		'activeTab_goods': fields.function( get_active_tabs, method=True, type='boolean', string="Active tab: goods" ),
	}

eagle_contract()

class eagle_contract_pos( osv.osv ):
	_inherit = 'eagle.contract.position'

	def get_active_tabs(self, cr, uid, cnt_ids, field_name, args, context={}):
		val = self.pool.get('eagle.contract').get_active_tabs(cr, uid, False, 'activeTab_goods', [], context=context)
		res = {}
		if cnt_ids:
			for cnt_id in cnt_ids:
				res[cnt_id] = val
		else:
			res = val
		return res

	_columns = {
		'goods_ids': fields.many2many( 'eagle.good.object', 'eagle_positions_goods_rel', 'position_id', 'good_id', 'Concerned Goods', select=True ),
		'activeTab_pos_goods': fields.function( get_active_tabs, method=True, type='boolean', string="Active tab: goods" ),
	}
	
	_defaults = {
		'activeTab_pos_goods': lambda s,cr,uid,c: s.get_active_tabs(cr, uid, False, 'activeTab_goods', [], context=c)
	}

eagle_contract_pos()
