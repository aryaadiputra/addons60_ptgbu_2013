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

from osv import osv, fields
import netsvc

class payment_order(osv.osv):
    _inherit = 'payment.order'
    _description = 'Payment Order'
    _rec_name = 'reference'
    
    _columns = {
        'date_scheduled': fields.date('Scheduled date if fixed', states={'open':[('readonly', True)]}, help='Select a date if you have chosen Preferred Date to be fixed.'),
        'reference': fields.char('Reference', size=128, required=1, states={'open': [('readonly', True)]}),
        'mode': fields.many2one('payment.mode', 'Payment mode', select=True, required=1, states={'open': [('readonly', True)]}, help='Select the Payment Mode to be applied.'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('open', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('done', 'Done')], 'State', select=True,
            help='When an order is placed the state is \'Draft\'.\n Once the bank is confirmed the state is set to \'Confirmed\'.\n Then the order is paid the state is \'Done\'.'),
        'line_ids': fields.one2many('payment.line', 'order_id', 'Payment lines', states={'open': [('readonly', True)]}),
        #'total': fields.function(_total, string="Total", method=True, type='float'),
        'user_id': fields.many2one('res.users', 'User', required=True, states={'open': [('readonly', True)]}),
        'date_prefered': fields.selection([
            ('now', 'Directly'),
            ('due', 'Payment Date'),
            ('fixed', 'Fixed date')
            ], "Preferred date", change_default=True, required=True, states={'open': [('readonly', True)]}, help="Choose an option for the Payment Order:'Fixed' stands for a date specified by you.'Directly' stands for the direct execution.'Due date' stands for the scheduled date of execution."),
        'date_created': fields.date('Creation date', readonly=True),
        'date_done': fields.date('Execution date', readonly=True),
    }
    
payment_order()