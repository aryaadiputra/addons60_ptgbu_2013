# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import netsvc
from tools.translate import _

from osv import fields,osv

class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"
    _description="Purchase Requisition"
    _columns = {
        
        'req_employee': fields.many2one('hr.employee', 'Request By', required=True),
        'user_id': fields.many2one('res.users', 'Responsible',required=True),
        'date_start': fields.datetime('Requisition Date',required=True),
        'date_end': fields.datetime('Requisition Deadline', required=True),
        'delegate': fields.many2one('res.users', 'Delegate to'),
        'origin': fields.char('Origin', size=32, required=True),
        'manager_approve_date': fields.datetime('Manager Approve', readonly=True),
        'buyer_approve_date': fields.datetime('Buyer Approve', readonly=True),
        
    }
    
    
    def tender_in_progress(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'manager_approve_date':time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        self.write(cr, uid, ids, {'state':'in_progress'} ,context=context)
        return True

    def tender_done(self, cr, uid, ids, context=None):
        if not self.browse(cr, uid, ids)[0].purchase_ids:
            raise osv.except_osv(_('No Quotation Defined !'),_("You must select Supplier for Quotation !") )
        self.write(cr, uid, ids, {'buyer_approve_date':time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        self.write(cr, uid, ids, {'state':'done', 'date_end':time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return True
    
    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_end': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
        'exclusive': 'multiple',
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'purchase.requisition', context=c),
        'user_id': lambda self, cr, uid, context: uid,
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'purchase.order.requisition'),
    }

purchase_requisition()