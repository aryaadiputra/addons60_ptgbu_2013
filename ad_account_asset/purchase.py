import time
from osv import fields, osv
from tools.translate import _


class asset_purchase(osv.osv):
    print"HHHHHHHHHHHHHHHHHHHHHH"
    _inherit = "purchase.order"
    
    def inv_line_create(self, cr, uid, a, ol):
        
        if ol.set_to_asset == True:
            asset_info = "Set to Asset"
            asset_check_value = True
        else:
            asset_info = "Don't Set to Asset"
            asset_check_value = False
        
        print "BBBBBBBBBBBBBBBBBBBBB", ol
        return (0, False, {
            'name': ol.name,
            'account_id': a,
            'price_unit': ol.price_unit or 0.0,
            'quantity': ol.product_qty,
            'product_id': ol.product_id.id or False,
            'uos_id': ol.product_uom.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in ol.taxes_id])],
            'account_analytic_id': ol.account_analytic_id.id or False,
            'set_to_asset': asset_info,
            'asset_check': asset_check_value,
            'discount':ol.discount,
        })
             
asset_purchase()


class asset_purchase_line(osv.osv):
    
    _inherit = "purchase.order.line"
    
    _columns = {
             #'asset_category_id': fields.many2one('account.asset.category', 'Asset Category'),
             'set_to_asset': fields.boolean('Set to Asset?'),
             #'set_to_asset': fields.char('Make to Asset?', size=64,),
                }
     
asset_purchase_line()