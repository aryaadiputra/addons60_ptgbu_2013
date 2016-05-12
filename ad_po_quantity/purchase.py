import time
from osv import fields, osv
from tools.translate import _

class purchase_quantity(osv.osv):
    
    _inherit = "purchase.order.line"
    
    
    def onchange_quantity(self, cr, uid, ids, product_qty):
        print "mmmmmmmmm", product_qty
        print "xxxxxxxxxxxxxxxxxxx", ids
        
        
        if ids:
            
        
            id_qty = self.pool.get('purchase.order.line').search(cr,uid,[('id','=',ids)])
            qty = self.pool.get('purchase.order.line').browse(cr,uid,id_qty)
            
            print "cccccccccccccccccccc", qty
            
            for q in qty:
                hasil_qty = q['product_qty']
                print "HHHHHHHHHHHHHHHHHHHHHHH",hasil_qty
                
            #product_qty = p_v
            
            if hasil_qty < product_qty:
                
                save = hasil_qty
            else: 
                save = product_qty
            
            return {'value': {'product_qty': save}}
    
        #{'value':{'p_v_dump':p_v_dump}}
    
    #hasil = self.pool.get('purchase.order.line').browse(cr,uid,tes)
    
    _columns = {
             'product_qty': fields.float('Quantity', required=False, digits=(16,2)),
             'virtual': fields.boolean('Budget Virtual', readonly=True),
             #'delegate': fields.many2one('hr.employee', 'Delegate to', required=False),
                }
    
purchase_quantity()






class purchase_order_res(osv.osv):
    
    _inherit = "purchase.order"
    
    
    
    _columns = {
             
             'delegate': fields.many2one('hr.employee', 'Delegate to', required=False, readonly=True),
             #'contact_supplier': fields.char('Contact Supplier', size=64,),
             #'requisition_id' : fields.many2one('purchase.requisition','Purchase Requisition')
                }
    
purchase_order_res()