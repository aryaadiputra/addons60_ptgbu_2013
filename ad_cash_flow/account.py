# -*- coding: utf-8 -*-
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

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter

import netsvc
import pooler
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _

class cash_flow_category(osv.osv):
    _name = "cash.flow.category"
    
    _columns = {
            'name'          : fields.char('Name', size=256, required=True, ),
            'sequence'      : fields.integer('Sequence',required=True, ),
            'sub_category_line'  : fields.one2many('sub.category.line','category_id','Lines', required=True),
                }
    
cash_flow_category()

class sub_category_line(osv.osv):
    _name = "sub.category.line"
    
    _columns = {
            'category_id'   : fields.many2one('cash.flow.category','Category'),
            'name'          : fields.char('Name', size=256, required=True, ),
            'sequence'      : fields.integer('Sequence',required=True, ),
                }
    
sub_category_line()



class account_account(osv.osv):
    _inherit = "account.account"
    
    _columns = {
        'ar_ap' : fields.boolean('AR/ AP'),
        'sub_cashflow_category_id'   : fields.many2one('sub.category.line','Cash Flow Sub Category'),
                }
    
account_account()