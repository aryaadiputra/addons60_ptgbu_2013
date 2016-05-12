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

from osv import osv,fields
import tools

class account_journal(osv.osv):
    _inherit = "account.journal"
    '''
        Add fields Allow Check writing, Use Preprinted Check and Check Sequence on journal
    '''
    _columns = {
        'allow_check_writing': fields.boolean('Allow Check writing', help='Fill this if the journal is to be used for writing checks.'),
        'use_preprint_check': fields.boolean('Use Preprinted Check'),
        'check_sequence': fields.many2one('ir.sequence', 'Check Sequence', help="This field contains the information related to the numbering of the check number."),
        }

account_journal()

class res_company(osv.osv):
    _inherit = "res.company"

    '''
        Add check printing options check_layout, currency_format and check language on company
    '''
    def _get_language(self, cr, uid, context):
        lang_obj = self.pool.get('res.lang')
        lang_ids = lang_obj.search(cr, uid, [('translatable', '=', True)],context=context)
        langs = lang_obj.browse(cr, uid, lang_ids, context=context)
        res = [(lang.code, lang.name) for lang in langs]
        for lang_dict in tools.scan_languages():
            if lang_dict not in res:
                res.append(lang_dict)
        return res

    _columns = {
        'check_layout': fields.selection([
            ('top', 'Check on Top'),
            ('middle', 'Check in middle'),
            ('bottom', 'Check on bottom'),
            ],"Choose Check layout",
            help="Check on top is compatible with Quicken, QuickBooks and Microsoft Money. Check in middle is compatible with Peachtree, ACCPAC and DacEasy. Check on bottom is compatible with Peachtree, ACCPAC and DacEasy only"  ),
        'currency_format': fields.selection([('us','US Format'), ('euro','Europian Format')],'Check Printing Format'),
        'lang': fields.selection(_get_language, string='Check Print Language', size=16),
        }
    _defaults = {
        'check_layout' : lambda *a: 'top',
        'currency_format':'us',
    }
res_company()
class check_log(osv.osv):
    _name = 'check.log'
    _description = 'Check Log'
    '''
        Check Log model
    '''
    _columns = {
        'name':fields.many2one('account.voucher','Reference payment'),
        'status': fields.selection([('active','Active'),
                                    ('voided', 'Voided'),
                                    ('stop_pay', 'Stop Pay Placed'),
                                    ('lost', 'Lost'),
                                    ('unk', 'Unknown'),
                                    ],"Check Status",),
        'check_no':fields.char('Check Number',size=64),
        }
    _defaults = {
        'status' :'blank',
    }
check_log()

class account_invoice(osv.osv):
    """Update inv_reference field.
    This field will update only if the stock_assigned_picker module is installed."""

    _inherit = "account.invoice"

    def _calc_inv_ref(self, cr, uid, ids, name, args, context=None):
        res={}
        for inv in self.browse(cr, uid, ids):
            cr.execute("SELECT purchase_id FROM purchase_invoice_rel WHERE invoice_id = %s", (inv.id,))
            pur_ids = cr.fetchall() or None
            if pur_ids and pur_ids[0] and pur_ids[0][0]:
                pick_ids = self.pool.get('stock.picking').search(cr, uid, [('purchase_id','=',pur_ids[0][0])], context=context)
                if pick_ids:
                    pici_id = self.pool.get('stock.picking').browse(cr, uid, pick_ids[0], context=context)
                    if 'ref_inv_no' in pici_id._columns.keys():
                        res[inv.id] = pici_id.ref_inv_no
        return res
    def _get_invoice_pur(self, cr, uid, ids, context=None):
        result = {}
        for purchase_id in self.pool.get('purchase.order').browse(cr, uid, ids, context=context):
            for invoice_id in purchase_id.invoice_ids:
                result[invoice_id.id] = True
        return result.keys()
    def _get_invoice_pick(self, cr, uid, ids, context=None):
        result = {}
        for pick in self.pool.get('stock.picking').browse(cr, uid, ids, context=context):
            if pick.purchase_id:
                for invoice_id in pick.purchase_id.invoice_ids:
                    result[invoice_id.id] = True
        return result.keys()

    _columns = {

        'inv_ref': fields.function(_calc_inv_ref, method=True, string='Reference Invoice',type='char', size=32,
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['state'], 10),
                'purchase.order': (_get_invoice_pur, ['order_line'], 10),
                'stock.picking': (_get_invoice_pick, ['ref_inv_no','purchase_id'], 10),
            }, multi=False),


    }
account_invoice()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
