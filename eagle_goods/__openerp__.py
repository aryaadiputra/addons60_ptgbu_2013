# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_goods
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
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

{
    'name': 'Eagle View, Goods module',
    'version': '1.1.11',
    'category': 'Eagle view/Goods',
    'description': """This module introduces the notion of Goods to manage, in the context of a contract.
    """,
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['eagle_base'],
    'init_xml': [],
    'update_xml': [
    	"security/ir.model.access.csv",
    	'goods_view.xml',
    	'contracts_view.xml',
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'active': False,
}
