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

class account_inv(osv.osv):
    
    _inherit='account.invoice'
    
    def action_query(self, cr, uid, ids, context=None):
        print "vvvbbb"
        obj_move_line = self.pool.get('account.move.line')
        obj_move = self.pool.get('account.move')
        obj_account_inv = self.pool.get('account.invoice')
        
        
        employee = cr.execute('SELECT number, id FROM account_invoice')
        res = cr.fetchall()
        
        for a in res:
            print "iD :", a
            
        inv_search = obj_account_inv.search(cr, uid, [('company_id','=', 1)])
        inv_browse = obj_account_inv.browse(cr, uid, inv_search)
        
        for x in inv_browse:
            print "==============>>^^^^^^", x.number
            
            move_search = obj_move.search(cr, uid, [('name','=',x.number)])
            move_browse = obj_move.browse(cr, uid, move_search)
            
            for y in move_browse:
                print "=============>>", y.name, y.id
                
                move_line_search = obj_move_line.search(cr, uid, [('move_id','=',y.id)])
                move_line_browse = obj_move_line.browse(cr, uid, move_line_search)
                
                for r in move_line_browse:
                    print "x.payment_date", x.payment_date
                    obj_move_line.write(cr, uid, [r.id], {'payment_date':x.payment_date,})

        
#        account_inv_browse = obj_account_inv.browse(cr, uid, ids)
#        
#        for inv in account_inv_browse:
#            print "inv.number", inv.name
#            
#            obj_move_browse = obj_move.browse(cr, uid, [inv.number])
#            
#            for move in obj_move_browse:
#                print "move :", move.name
        
        ##########################################
        
    
    _columns = {
                
                }
account_inv()