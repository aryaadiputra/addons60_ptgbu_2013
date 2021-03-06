# -*- coding: utf-8 -*-
#
#  File: config.py
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

class eagle_config_params( osv.osv ):
	_inherit = 'eagle.config.params'
	
	_columns = {
		'opport_2_contract_mode': fields.selection( [
			('none', 'None'),
			('win', 'New contract if won'),
			('creation','New contract at creation')], 'Relation between an opportunity and a contract' ),
	}
	
	_defaults = {
		'opport_2_contract_mode': lambda *a: 'win', 
	}

eagle_config_params()
