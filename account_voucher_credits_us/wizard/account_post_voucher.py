# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from osv import fields, osv

class account_post_voucher(osv.osv_memory):
    _name = 'account.post.voucher'
    _description = 'Account Pay Voucher'

    _columns = {
        'total_paid': fields.float('Total Received'),
        'total_allocated': fields.float('Total Allocated'),
        'ok_to_go': fields.float('OK to Go'),
    }

    def _get_total_paid(self, cr, uid, context={}):
        obj_voucher = self.pool.get('account.voucher')
        return obj_voucher.browse(cr, uid, context['active_id'], context).amount

    def _get_total_allocated(self, cr, uid, context={}):
        obj_voucher = self.pool.get('account.voucher')
        voucher = obj_voucher.browse(cr, uid, context['active_id'], context)
        total_allocated = 0.0
        for line in voucher.line_cr_ids:
            total_allocated += line.amount
        return total_allocated

    def _get_ok_to_go(self,cr, uid, context={}):
        obj_voucher = self.pool.get('account.voucher')
        voucher = obj_voucher.browse(cr, uid, context['active_id'], context)
        total_allocated = 0.0
        for line in voucher.line_cr_ids:
            total_allocated += line.amount
        return total_allocated - voucher.amount

    _defaults = {
        'total_paid': _get_total_paid,
        'total_allocated': _get_total_allocated,
        'ok_to_go': _get_ok_to_go,
    }
    def onchange_ok_to_go(self,cr, uid, ids, ok_to_go, context={}):
        if ok_to_go > 0.0:
            return {'warning': {'title': 'Overallocated invoices', 'message': 'Reduce allocations to match Total Receipt'}}
        else:
            return {'value':{}}
    def launch_wizard(self, cr, uid, ids, context=None):
        """
        Don't allow post if total_allocated > total_paid.
        """
        obj_voucher = self.pool.get('account.voucher')
        obj_voucher.action_move_line_create(cr, uid, context['active_ids'], context)
        return {}

account_post_voucher()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
