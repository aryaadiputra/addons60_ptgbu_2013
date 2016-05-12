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

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from osv import fields, osv
from tools.translate import _
import netsvc
import tools
import decimal_precision as dp
import logging



class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _description = "Picking List"
    
    _columns ={
            
               }
    
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        if context is None:
            context = {}

        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        address_obj = self.pool.get('res.partner.address')
        invoices_group = {}
        
        res = {}
        inv_type = type
        for picking in self.browse(cr, uid, ids, context=context):
            po_seacrh = self.pool.get('purchase.order').search(cr, uid, [('id', '=', picking.purchase_id.id)])
            po_browse = self.pool.get('purchase.order').browse(cr, uid, po_seacrh)
            for po_id in po_browse:
                payment_id = po_id.payment_term.id
                #################Downpayment#####################
                for dp_amount in po_id.downpayment_line:
                    amount_dp = 0.0
                    amount_dp = amount_dp + dp_amount.amount
                    #print "ddwssde", dp_amount.amount
                downpayment_id = po_id.downpayment_id.id
                ######################################
            
            print "xxxxxxx :", payment_id
            if picking.invoice_state != '2binvoiced':
                continue
            payment_term_id = False
            partner =  picking.address_id and picking.address_id.partner_id
            print "Partner ::", partner
            if not partner:
                raise osv.except_osv(_('Error, no partner !'),
                    _('Please put a partner on the picking list if you want to generate invoice.'))

            if not inv_type:
                inv_type = self._get_invoice_type(picking)

            if inv_type in ('out_invoice', 'out_refund'):
                account_id = partner.property_account_receivable.id
                payment_term_id = self._get_payment_term(cr, uid, picking)
            else:
                account_id = partner.property_account_payable.id

            address_contact_id, address_invoice_id = \
                    self._get_address_invoice(cr, uid, picking).values()
            address = address_obj.browse(cr, uid, address_contact_id, context=context)

            comment = self._get_comment_invoice(cr, uid, picking)
            print "account_id++++++++++++++++++++", account_id
            if account_id == 191:
                raise osv.except_osv(_('Error, Account !'),
                    _('Please Call Your Administrator Error Number AC-191.'))
            
            if group and partner.id in invoices_group:
                invoice_id = invoices_group[partner.id]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals = {
                    'name': (invoice.name or '') + ', ' + (picking.name or ''),
                    'origin': (invoice.origin or '') + ', ' + (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
                    'comment': (comment and (invoice.comment and invoice.comment+"\n"+comment or comment)) or (invoice.comment and invoice.comment or ''),
                    'date_invoice':context.get('date_inv',False),
                    'user_id':uid
                }
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals, context=context)
            else:
                invoice_vals = {
                    'name': picking.name,
                    'origin': (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
                    'type': inv_type,
                    'account_id': account_id,
                    'partner_id': address.partner_id.id,
                    'address_invoice_id': address_invoice_id,
                    'address_contact_id': address_contact_id,
                    'comment': comment,
                    'payment_term': payment_id or payment_term_id,
                    'fiscal_position': partner.property_account_position.id,
                    'date_invoice': context.get('date_inv',False),
                    'company_id': picking.company_id.id,
                    'user_id':uid,
                    ###########################Downpayment###################
                    'amount_dp' : 0.0,
                    'downpayment_id' : downpayment_id,
                    #########################################################
                }
                cur_id = self.get_currency_id(cr, uid, picking)
                if cur_id:
                    invoice_vals['currency_id'] = cur_id
                if journal_id:
                    invoice_vals['journal_id'] = journal_id
                invoice_id = invoice_obj.create(cr, uid, invoice_vals,
                        context=context)
                #################################Update Invoice Date###################################
                self.pool.get('purchase.order').write(cr, uid, picking.purchase_id.id, {'inv_receive_date' : context.get('date_inv',False)})
                ####################################################################
                invoices_group[partner.id] = invoice_id
            res[picking.id] = invoice_id
            for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                origin = move_line.picking_id.name or ''
                if move_line.picking_id.origin:
                    origin += ':' + move_line.picking_id.origin
                if group:
                    name = (picking.name or '') + '-' + move_line.name
                else:
                    name = move_line.name

                if inv_type in ('out_invoice', 'out_refund'):
                    account_id = move_line.product_id.product_tmpl_id.\
                            property_account_income.id
                    if not account_id:
                        account_id = move_line.product_id.categ_id.\
                                property_account_income_categ.id
                else:
                    account_id = move_line.product_id.product_tmpl_id.\
                            property_account_expense.id
                    if not account_id:
                        account_id = move_line.product_id.categ_id.\
                                property_account_expense_categ.id

                price_unit = self._get_price_unit_invoice(cr, uid,
                        move_line, inv_type)
                
                discount = self._get_discount_invoice(cr, uid, move_line)
                #if inv_type == 'in_invoice':
                    #discount
                
                tax_ids = self._get_taxes_invoice(cr, uid, move_line, inv_type)
                account_analytic_id = self._get_account_analytic_invoice(cr, uid, picking, move_line)
                print "account_analytic_id^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", account_analytic_id
                #set UoS if it's a sale and the picking doesn't have one
                uos_id = move_line.product_uos and move_line.product_uos.id or False
                if not uos_id and inv_type in ('out_invoice', 'out_refund'):
                    uos_id = move_line.product_uom.id
                account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, partner.property_account_position, account_id)
                invoice_line_id = invoice_line_obj.create(cr, uid, {
                    'name': name,
                    'origin': origin,
                    'invoice_id': invoice_id,
                    'uos_id': uos_id,
                    'product_id': move_line.product_id.id,
                    'account_id': account_id,
                    'price_unit': price_unit,
                    'discount': discount,
                    'quantity': move_line.product_uos_qty or move_line.product_qty,
                    'invoice_line_tax_id': [(6, 0, tax_ids)],
                    'account_analytic_id': account_analytic_id,
                }, context=context)
                
                
                
                self._invoice_line_hook(cr, uid, move_line, invoice_line_id)
            #########################Landed Cost######################
            if po_id:
                print "Landed Cost"
                
                for landed_cost_line in po_id.landed_cost_line:
                
                    landed_cost_line_id = invoice_line_obj.create(cr, uid, {
                        'name': landed_cost_line.name,
                        #'origin': origin,
                        'invoice_id': invoice_id,
                        #'uos_id': uos_id,
                        #'product_id': move_line.product_id.id,
                        'account_id': landed_cost_line.account_id.id,
                        'price_unit': landed_cost_line.amount,
                        #'discount': discount,
                        'quantity': 1,
                        #'invoice_line_tax_id': [(6, 0, tax_ids)],
                        #'account_analytic_id': account_analytic_id,
                    }, context=context)
                
                ########################################################
                print "invoice_line_id -========================:", invoice_line_id
            invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
                    set_total=(inv_type in ('in_invoice', 'in_refund')))
            self.write(cr, uid, [picking.id], {
                'invoice_state': 'invoiced',
                }, context=context)
            self._invoice_hook(cr, uid, picking, invoice_id)
        self.write(cr, uid, res.keys(), {
            'invoice_state': 'invoiced',
            }, context=context)
        return res

stock_picking()