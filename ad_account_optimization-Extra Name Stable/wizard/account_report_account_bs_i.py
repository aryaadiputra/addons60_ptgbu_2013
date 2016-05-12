# -*- coding: utf-8 -*-
# Copyright 2010 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from osv import osv
from osv import fields

class account_bs_report(osv.osv_memory):
    _inherit = 'account.bs.report'
    _columns = {
        'type': fields.selection([('pdf','PDF222222'),('xls','Excel')], 'Type', required=True),
        'currency_rate': fields.boolean('With Currency Rate ?', help="Converted All balance with Current rate Currency(default= IDR"),
        'rate_opt': fields.float('Rate', digits=(16,4), help="Fill this blank with Rate Currency(default= IDR"),
        'new_report': fields.boolean('New Report'),
    }

    _defaults = {
        'type': lambda *a: 'pdf',
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids[0], context=context)
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['landscape', 'currency_rate', 'rate_opt', 'reserve_account_id', 'amount_currency', 'sortby'])[0])
        if not data['form']['reserve_account_id']:# GTK client problem onchange does not consider in save record
            data['form'].update({'currency_rate': False})
        if wizard.type == 'xls':
            if wizard.new_report == True:
                final_report = 'account.balancesheet.new.xls'
            else:
                final_report = 'account.balancesheet.xls'
        elif wizard.type == 'pdf':
            if wizard.currency_rate:
                final_report = 'ad.account.balancesheet.currency'
            elif wizard.new_report == True:
                final_report = 'ad.account.balancesheet.new'
            else:
                final_report = 'ad.account.balancesheet'
        return { 'type': 'ir.actions.report.xml', 'report_name': final_report, 'datas': data}
    
account_bs_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
