import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _

class account_invoice(osv.osv):
    
    _inherit = 'account.invoice'
    
    def update_payment_date(self, cr, uid, ids):
        #print "xxxxxxxxxxxx", ids
        obj_move = self.pool.get('account.move')
        obj_move_line = self.pool.get('account.move.line')
        
        browse_inv = self.browse(cr, uid, ids)
        for id_inv in browse_inv:
            
            print "WWWW : ", id_inv.number
            #print "Payment Date :", id_inv.payment_date
            
        search_move = obj_move.search(cr, uid, [('name','=',id_inv.number)])
        browse_move = obj_move.browse(cr, uid, search_move)
        
        for id_move in browse_move:
            print "yyy :", id_move.id
        
        search_move_line = obj_move_line.search(cr, uid, [('move_id','=',id_move.id)])
        browse_move_line = obj_move_line.browse(cr, uid, search_move_line)
        
        for id_move_line in browse_move_line:
            #print "HHH :", id_move_line.id
            #obj_move_line.write(cr, uid, [id_move_line.id], {'payment_date': id_inv.payment_date})
            ##############Payment Date Di Remove#################################
            obj_move_line.write(cr, uid, [id_move_line.id], {'payment_date': False})
        
        #obj_move_line.write(cr, uid, ids, {'payment_date': '2012-04-04'})
        
    _columns = {
                
                }
account_invoice()