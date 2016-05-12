# -*- coding: utf-8 -*-
#
#  File: goods.py
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
import decimal_precision as dp

class eagle_good_object_base( osv.osv ):
	_name = 'eagle.good.object'
	_description = 'Eagle Goods Management'
	
	_columns = {
		'name': fields.char( 'Good', size=100, required=True, select=True ),
		'seq': fields.integer( 'Sequence', required=True ),
		'contract_id': fields.many2one( 'eagle.contract', 'Contract', select=True ),
		'parent_id': fields.many2one( 'eagle.good.object', 'Parent' ),
		'description': fields.text( 'Description' ),
		'street': fields.char( 'Street', size=128 ),
		'street2': fields.char( 'Street2', size=128 ),
		'zip': fields.char('Zip', change_default=True, size=24),
		'city': fields.char('City', size=128),
		'state_id': fields.many2one("res.country.state", 'Fed. State', domain="[('country_id','=',country_id)]"),
		'country_id': fields.many2one('res.country', 'Country'),
		'contact': fields.char( 'Contact', size=128 ),
		'phone': fields.char('Phone', size=64),
	}
	
	_order = 'contract_id,seq,id'

	_defaults = {
		'seq': lambda *a: 0,
	}

eagle_good_object_base()

class eagle_good_attribut( osv.osv ):
	_name = 'eagle.good.attribut'
	_description = 'Eagle Good Attributs Management'
	
	_columns = {
		'name': fields.char( 'Label', size=30, required=True ),
		'value': fields.char( 'Value', size=100, required=True ),
		'seq': fields.integer( 'Sequence', required=True ),
		'good_id': fields.many2one( 'eagle.good.object', 'Good' ),
	}
	
	_order = 'seq,id'

	_defaults = {
		'seq': lambda *a: 0,
	}

eagle_good_attribut()


class eagle_good_object( osv.osv ):
	_inherit = 'eagle.good.object'

	_columns = {
		'attributs': fields.one2many( 'eagle.good.attribut', 'good_id', 'Characteristics' ),
	}

	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
		res = super(eagle_good_object, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
		lst = res['arch'].split('\n')
		i = 0
		l = len(lst)
		while(i < l):
			if 'contract_id' in lst[i]:
				lst[i] = '<field name="contract_id" colspan="2" invisible="1"/>'
			i += 1
		res['arch'] = '\n'.join(lst)

		return res

eagle_good_object()
