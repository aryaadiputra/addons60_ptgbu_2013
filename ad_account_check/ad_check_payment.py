from osv import osv,fields
import time


class payment_order(osv.osv):
    
    
    _inherit='payment.order'
    _description = 'inherit field to invoice'
    
    _columns={
 
      "check_num": fields.many2one("account.cheque", "Cheque Number"),
 
            }
 
payment_order()