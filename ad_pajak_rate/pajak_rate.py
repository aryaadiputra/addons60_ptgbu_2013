#import ir
import time
import netsvc
import pooler

from lxml import etree
from tools.translate import _
import decimal_precision as dp
from tools.misc import currency
from osv import fields, osv, orm

class res_currency(osv.osv):
    
    def _pajak_rate(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        if 'date' in context:
            date = context['date']
        else:
            date = time.strftime('%Y-%m-%d')
        date = date or time.strftime('%Y-%m-%d')
        for id in ids:
            cr.execute("SELECT pajak_id, rate FROM res_pajak_rate WHERE pajak_id = %s AND name <= %s ORDER BY name desc LIMIT 1" ,(id, date))
            if cr.rowcount:
                id, rate = cr.fetchall()[0]
                res[id] = rate
            else:
                res[id] = 0
        return res
    
    _inherit = "res.currency"
    _columns = {
        'pajak_rate': fields.function(_pajak_rate, method=True, string='Current Tax Rate', digits=(12,20)),
        'pajak_rate_ids': fields.one2many('res.pajak.rate', 'pajak_id', 'Pajak Rates'),
    }
    
    def compute_pajak_rate(self, cr, uid, from_currency_id, to_currency_id, from_amount, round=True, context=None):
        
        if not from_currency_id:
            from_currency_id = to_currency_id
        if not to_currency_id:
            to_currency_id = from_currency_id
        xc = self.browse(cr, uid, [from_currency_id,to_currency_id], context=context)
        from_currency = (xc[0].id == from_currency_id and xc[0]) or xc[1]
        to_currency = (xc[0].id == to_currency_id and xc[0]) or xc[1]
        if to_currency_id == from_currency_id:
            #print "sama"
            if round:
                return self.round(cr, uid, to_currency, from_amount)
            else:
                return from_amount
        else:
            #print "xc",xc[0]
            #print "beda"
            #===================EDITED 18 sept 2012=============================
            tax_rate_id=self.pool.get('res.pajak.rate').search(cr,uid,[('pajak_id','=',from_currency_id),('name','=',context['date'])])
            rate = 1
            if tax_rate_id:
                tax_data=self.pool.get('res.pajak.rate').browse(cr,uid,tax_rate_id)[0]
                rate = tax_data.rate or xc[0].pajak_rate
            #===================================================================
            #print "rate",rate
            if round:
                #print "round"
                return self.round(cr, uid, to_currency, from_amount/rate)
            else:
                #print "not round",from_amount/rate,"=",from_amount,"/",rate
                return (from_amount/rate)
        
res_currency()

class res_pajak_rate(osv.osv):
    _name = "res.pajak.rate"
    _description = "Pajak Rate"
    _columns = {
        'name': fields.date('Date', required=True, select=True),
        'rate': fields.float('Rate', digits=(12,20), required=True),
        'pajak_id': fields.many2one('res.currency', 'Tax', required=True, ondelete='cascade', select=True, readonly=False),
    }

    _defaults = {
        'name': lambda *a: time.strftime('%Y-%m-%d'),
    }

    _order = "name desc"

res_pajak_rate()

