# -*- coding: utf-8 -*-
# Copyright 2010 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from osv import osv
from osv import fields

class account_pl_report_opti(osv.osv_memory):
    _inherit = 'account.pl.report'
    _columns = {
        'type': fields.selection([('pdf','PDF'),('xls','Excel')], 'Type', required=True),
        'currency_rate': fields.boolean('With Currency Rate ?', help="Converted All balance with Current rate Currency"),
        'rate_opt': fields.float('Rate', digits=(16,4), help="Fill this blank with Rate Currency(default= IDR")
    }
    _defaults = {
        'type': lambda *a: 'pdf',
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids[0], context=context)
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['initial_balance', 'currency_rate', 'rate_opt', 'reconcil', 'page_split', 'amount_currency','get_lines'])[0])

        final_report = ''
        if wizard.type == 'pdf':
            if wizard.currency_rate:
            #if data['form']['currency_rate']:
                final_report = 'ad.pl.account.currency'
            else:
                final_report = 'ad.pl.account'
        elif wizard.type == 'xls':
            final_report = 'account.profit.loss.xls'
        else:
            return {}


        return {
            'type': 'ir.actions.report.xml',
            'report_name': final_report,
            'datas': data,
        }

account_pl_report_opti()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
