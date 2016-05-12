import time
from osv import fields, osv, orm
from tools.translate import _
import decimal_precision as dp

class hr_travel_line(osv.osv):
    
    _name = "hr.travel.line"
    _description = 'hr travel line'

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, address_id=line.invoice_id.address_invoice_id, partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    _columns = {
        'name': fields.char('Description', size=256, required=True),
        'origin': fields.char('Origin', size=256, help="Reference of the document that produced this invoice."),
        'invoice_id': fields.many2one('account.invoice', 'Invoice Reference', ondelete='cascade', select=True),
        'uos_id': fields.many2one('product.uom', 'Unit of Measure', ondelete='set null'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null'),
        'account_id': fields.many2one('account.account', 'Account', required=True, domain=[('type','<>','view'), ('type', '<>', 'closed')], help="The income or expense account related to the selected product."),
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Account')),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal', type="float",
            digits_compute= dp.get_precision('Account'), store=True),
        'quantity': fields.float('Quantity', required=True),
        'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Account')),
        'invoice_line_tax_id': fields.many2many('account.tax', 'invoice_line_tax_id', 'invoice_line_id', 'tax_id', 'Taxes'),
        'note': fields.text('Notes'),
        'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),
        # 'company_id': fields.related('invoice_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
        'partner_id': fields.related('invoice_id','partner_id',type='many2one',relation='res.partner',string='Partner',store=True),
        'travel_id': fields.many2one('hr.travel', 'Travel Line'),
    }
    
hr_travel_line()