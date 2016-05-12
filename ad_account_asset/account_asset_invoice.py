# -*- encoding: utf-8 -*-
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

from osv import osv, fields

class account_invoice(osv.osv):

    _inherit = 'account.invoice'
    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(account_invoice, self).line_get_convert(cr, uid, x, part, date, context=context)
        res['asset_id'] = x.get('asset_id', False)
        return res

account_invoice()

class account_invoice_line(osv.osv):

    _inherit = 'account.invoice.line'
    _columns = {
        'asset_category_id': fields.many2one('account.asset.category', 'Asset Category'),
    }

    def move_line_get_item(self, cr, uid, line, context=None):
        amount_tax = 0.0
        print "mmmmmmmmmmmmmmmmmmmm", line.id
        
        account_invoice_line_id = line.id
        print "account_invoice_line_id", account_invoice_line_id
        
#        line_tax_search = self.pool.get('account_invoice_line_tax').search(cr,uid,[('invoice_line_id','=',account_invoice_line_id)])
#        line_tax_browse = self.pool.get('account_invoice_line_tax').browse(cr,uid,line_tax_search)

        cr.execute('select tax_id from account_invoice_line_tax where invoice_line_id=%s', (account_invoice_line_id,))
        line_tax_ids = cr.fetchall()
        print "line_tax_ids", line_tax_ids
        
        for line_tax in line_tax_ids:
            line_tax_id = line_tax
            print "tax_id", line_tax_id
            
            tax_search = self.pool.get('account.tax').search(cr,uid,[('id','=',line_tax_id)])
            tax_browse = self.pool.get('account.tax').browse(cr,uid,tax_search)
            
            for tax in tax_browse:
                tax = tax.amount
            
            amount_tax += tax
        
        
#        print "amount_tax", amount_tax
#        
        gross_add_tax = (line.price_subtotal * amount_tax) + line.price_subtotal
        #print "gross_add_tax : ", gross_add_tax
        
        #print "oooppopopopopop",line.invoice_id.state, line.invoice_id.number
        
        asset_obj = self.pool.get('account.asset.asset')
        res = super(account_invoice_line, self).move_line_get_item(cr, uid, line, context=context)
        print "+++++++++++++++++++++++++++"
        if line.invoice_id and line.invoice_id.type not in ('out_invoice', 'out_refund') and line.asset_category_id and line.invoice_id.state=="approve_lv2-1":
                #print "QUantity ::::", int(line.quantity)
                qty_asset = int(line.quantity)
                price_asset_per_unit = gross_add_tax/qty_asset
                for a in range(qty_asset)   :
                    seq_fa = self.pool.get('ir.sequence').get(cr, uid, 'fa')
                    #print "seq_fa :", seq_fa
                    code_categ_seq = line.asset_category_id.code_extra
                    #print "code_categ_seq :", code_categ_seq
                    code_categ_seq_merge = seq_fa +"/"+ code_categ_seq
                    #print "code_categ_seq_merge :", code_categ_seq_merge
                    #print "hahahahahahaha"
                    vals = {
                        'code':code_categ_seq_merge,
                        'name': line.product_id and (line.name + ": " + line.product_id.name) or line.name,
                        'category_id': line.asset_category_id.id,
                        'purchase_value': price_asset_per_unit,
                        #'purchase_value': gross_add_tax,line.price_subtotal
                        'period_id': line.invoice_id.period_id.id,
                        'partner_id': line.invoice_id.partner_id.id,
                        'company_id': line.invoice_id.company_id.id,
                        'currency_id': line.invoice_id.currency_id.id,
                    }
                    #print vals
                    #print "*******************************************************"
                    asset_id = asset_obj.create(cr, uid, vals, context=context)
                    if line.asset_category_id.open_asset:
                        asset_obj.validate(cr, uid, [asset_id], context=context)
        return res

account_invoice_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
