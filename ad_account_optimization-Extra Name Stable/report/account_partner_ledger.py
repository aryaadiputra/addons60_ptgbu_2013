# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 Thamini S.à.R.L (<http://www.thamini.com>)
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

import time
import re
from report import report_sxw
from common_report_header import common_report_header

class third_party_ledger(report_sxw.rml_parse, common_report_header):

    def strip_name(self, char, size=50, truncation_str='...'):
        if not char:
            return ""
        if len(char) <= size:
            return char
        return char[:size-len(truncation_str)] + truncation_str

    def __init__(self, cr, uid, name, context=None):
        super(third_party_ledger, self).__init__(cr, uid, name, context=context)
        self.init_bal_sum = 0.0
        self.move_state = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit_partner': self._sum_debit_partner,
            'sum_credit_partner': self._sum_credit_partner,
#            'sum_debit': self._sum_debit,
#            'sum_credit': self._sum_credit,
            'get_currency': self._get_currency,
            'comma_me': self.comma_me,
            'strip_name': self.strip_name,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_account': self._get_account,
            'get_filter': self._get_filter,
            'get_start_date': self._get_start_date,
            'get_end_date': self._get_end_date,
            'get_fiscalyear': self._get_fiscalyear,
            'get_journal': self._get_journal,
            'get_partners':self._get_partners,
            'get_intial_balance':self._get_intial_balance,
            'display_initial_balance':self._display_initial_balance,
            'display_currency':self._display_currency,
            'display_filter': self._display_filter,
            'display_journals': self._display_journals,
            'get_target_move': self._get_target_move,
        })
        self.qcache = {}    # partner debit / credit / balance cache
        self.ilcache = {}   # initial line cache

    def set_context(self, objects, data, ids, report_type=None):
##        print("SET CONTEXT: %s" % (data))
        obj_move = self.pool.get('account.move.line')
        obj_partner = self.pool.get('res.partner')
        obj_fiscalperiod = self.pool.get('account.period')
        obj_fiscalyear = self.pool.get('account.fiscalyear')
##        print("USED CONTEXT: %s" % (data['form'].get('used_context', {})))
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context', {}))
        ctx2 = data['form'].get('used_context',{}).copy()
        ctx2.update({'initial_bal': True})
        self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
##        print("INIT QUERY: %s" % (self.init_query))
        self.reconcil = data['form'].get('reconcil', True)
        self.initial_balance = data['form'].get('initial_balance', True)
        self.result_selection = data['form'].get('result_selection', 'customer')
        self.amount_currency = data['form'].get('amount_currency', False)
        self.target_move = data['form'].get('target_move', 'all')
        PARTNER_REQUEST = ''
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']
        self.move_state = tuple(move_state)

        if self.reconcil:
            self.RECONCILE_TAG = " "
        else:
            self.RECONCILE_TAG = "AND l.reconcile_id IS NULL"


        self.end_date = None
        if ctx2.get('date_from',False) and ctx2.get('date_to',False):
            self.end_date = ctx2['date_to']
        elif ctx2.get('period_from',False) and ctx2.get('period_to',False):
            period_to = obj_fiscalperiod.browse(self.cr, self.uid, ctx2['period_to'], context=data['form'].get('used_context', {}))
            self.end_date = period_to.date_stop
        elif ctx2.get('fiscalyear'):
            fy = obj_fiscalyear.browse(self.cr, self.uid, ctx2['fiscalyear'], context=data['form'].get('used_context', {}))
            self.end_date = fy.date_stop
        else:
            self.end_date = time.strftime('%Y-%m-%d')

        if (data['model'] == 'res.partner'):
            ## Si on imprime depuis les partenaires
            if ids:
                PARTNER_REQUEST =  "AND line.partner_id IN %s",(tuple(ids),)
        if self.result_selection == 'supplier':
            self.ACCOUNT_TYPE = ['payable']
        elif self.result_selection == 'customer':
            self.ACCOUNT_TYPE = ['receivable']
        else:
            self.ACCOUNT_TYPE = ['payable','receivable']

        self.cr.execute(
            "SELECT a.id " \
            "FROM account_account a " \
            "LEFT JOIN account_account_type t " \
                "ON (a.type=t.code) " \
                'WHERE a.type IN %s' \
                "AND a.active", (tuple(self.ACCOUNT_TYPE), ))
        self.account_ids = [a for (a,) in self.cr.fetchall()]
        self.tuple_account_ids = tuple(self.account_ids)
        partner_to_use = []
        self.cr.execute(
                "SELECT DISTINCT l.partner_id " \
                "FROM account_move_line AS l, account_account AS account, " \
                " account_move AS am " \
                "WHERE l.partner_id IS NOT NULL " \
                    "AND l.account_id = account.id " \
                    "AND am.id = l.move_id " \
                    "AND am.state IN %s"
                    "AND " + self.query +" " \
                    "AND l.account_id IN %s " \
                    " " + PARTNER_REQUEST + " " \
                    "AND account.active ",
                (self.move_state, tuple(self.account_ids),))

        res = self.cr.dictfetchall()
        for res_line in res:
            partner_to_use.append(res_line['partner_id'])
        new_ids = partner_to_use
        self.partner_ids = new_ids
#        print("Partner To Use: %d %s" % (len(new_ids), new_ids))
##        print("Query: %s" % (self.query))

        for partner_id in self.partner_ids:
            self.qcache.setdefault(partner_id, {'debit': 0.0, 'credit': 0.0, 'balance': 0.0})
            self.ilcache.setdefault(partner_id, {'init_debit': 0.0, 'init_credit': 0.0, 'init_balance': 0.0})

        # Update cache
        self.cr.execute(
            """ SELECT l.partner_id,
                       COALESCE(SUM(l.debit),0.0) AS debit,
                       COALESCE(SUM(l.credit),0.0) AS credit,
                       COALESCE(SUM(l.debit),0.0) - COALESCE(SUM(l.credit),0) AS balance
                FROM account_move_line AS l,
                     account_move AS m
                WHERE m.id = l.move_id
                  AND m.state IN %%s
                  AND account_id IN %%s
                  %(reconcile_tag)s
                  AND %(query)s
                GROUP BY l.partner_id
            """ % {'reconcile_tag': self.RECONCILE_TAG, 'query': self.query},
            (self.move_state, self.tuple_account_ids,))

        for psummary in self.cr.dictfetchall():
            partner_id = psummary.pop('partner_id')
            self.qcache[partner_id] = psummary


        self.cr.execute(
            """ SELECT l.partner_id,
                       COALESCE(SUM(l.debit),0.0) AS init_debit,
                       COALESCE(SUM(l.credit),0.0) AS init_credit,
                       COALESCE(sum(debit-credit), 0.0) AS init_balance
                FROM account_move_line AS l,
                     account_move AS m
                WHERE m.id = l.move_id
                  AND m.state IN %%s
                  AND account_id IN %%s
                  %(reconcile_tag)s
                  AND %(query)s
                GROUP BY l.partner_id
            """ % {'reconcile_tag': self.RECONCILE_TAG, 'query': self.init_query},
            (self.move_state, self.tuple_account_ids))

        for isummary in self.cr.dictfetchall():
            partner_id = isummary.pop('partner_id')
            self.ilcache[partner_id] = isummary

        res = self.cr.fetchall()


        #self.partner_ids = new_ids = [ 1915 ]
        objects = obj_partner.browse(self.cr, self.uid, new_ids)
        return super(third_party_ledger, self).set_context(objects, data, new_ids, report_type)

    def _display_filter(self, data):
        filter_mode = self._get_filter(data)
        filter_string = filter_mode
        if filter_mode == 'Date':
            filter_string = '%s -> %s' % (self.formatLang(self._get_start_date(data), date=True),
                                          self.formatLang(self._get_end_date(data), date=True))
        elif filter_mode == 'Periods':
            filter_string = '%s -> %s' % (self.get_start_period(data) or '',
                                 self.get_end_period(data) or '')

        moves_string = self._get_target_move(data)
        display_partner_string = self._get_partners()

        return 'Display Partner: %s, Filter By: %s, Target Moves: %s' % (display_partner_string, filter_string, moves_string)

    def _display_journals(self, data):
        return u'Journals: %s' % (', '.join([ lt or '' for lt in self._get_journal(data) ]))

    def comma_me(self, amount):
        if type(amount) is float:
            amount = str('%.2f'%amount)
        else:
            amount = str(amount)
        if (amount == '0'):
             return ' '
        orig = amount
        new = re.sub("^(-?\d+)(\d{3})", "\g<1>'\g<2>", amount)
        if orig == new:
            return new
        else:
            return self.comma_me(new)

    def lines(self, partner):

        full_account = []
        self.cr.execute(
            "SELECT l.id, l.date, j.code, acc.code as a_code, acc.name as a_name, l.ref, m.name as move_name, l.name, l.debit, l.credit, l.amount_currency,l.currency_id, c.symbol AS currency_code " \
            "FROM account_move_line l " \
            "LEFT JOIN account_journal j " \
                "ON (l.journal_id = j.id) " \
            "LEFT JOIN account_account acc " \
                "ON (l.account_id = acc.id) " \
            "LEFT JOIN res_currency c ON (l.currency_id=c.id)" \
            "LEFT JOIN account_move m ON (m.id=l.move_id)" \
            "WHERE l.partner_id = %s " \
                "AND l.account_id IN %s AND " + self.query +" " \
                "AND m.state IN %s " \
                " " + self.RECONCILE_TAG + " "\
                "ORDER BY l.date",
                (partner.id, self.tuple_account_ids, self.move_state))
        res = self.cr.dictfetchall()
        sum = 0.0
        if self.initial_balance:
            sum = self.init_bal_sum
        for r in res:
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            full_account.append(r)
        return full_account

    def _get_intial_balance(self, partner):
        res =  self.ilcache[partner.id]
        self.init_bal_sum = res['init_balance']
        return res

    def _sum_debit_partner(self, partner):
        result_tmp = 0.0
        result_init = 0.0
        if self.initial_balance:
            result_init = self.ilcache[partner.id]['init_debit']

        result_tmp = self.qcache[partner.id]['debit']
        return result_tmp  + result_init

    def _sum_credit_partner(self, partner):
        result_tmp = 0.0
        result_init = 0.0
        if self.initial_balance:
            result_init = self.ilcache[partner.id]['init_credit']

        result_tmp = self.qcache[partner.id]['credit']
        return result_tmp  + result_init

    def _get_partners(self):
        if self.result_selection == 'customer':
            return 'Receivable Accounts'
        elif self.result_selection == 'supplier':
            return 'Payable Accounts'
        elif self.result_selection == 'customer_supplier':
            return 'Receivable and Payable Accounts'
        return ''

    def _sum_currency_amount_account(self, account, form):
        self._set_get_account_currency_code(account.id)
        self.cr.execute("SELECT sum(aml.amount_currency) FROM account_move_line as aml,res_currency as rc WHERE aml.currency_id = rc.id AND aml.account_id= %s ", (account.id,))
        total = self.cr.fetchone()
        if self.account_currency:
            return_field = str(total[0]) + self.account_currency
            return return_field
        else:
            currency_total = self.tot_currency = 0.0
            return currency_total

    def _display_initial_balance(self, data):
         if self.initial_balance:
             return True
         return False

    def _display_currency(self, data):
         if self.amount_currency:
             return True
         return False

report_sxw.report_sxw('report.account.third_party_ledger.opti', 'res.partner',
        'addons/account/report/account_partner_ledger.rml', parser=third_party_ledger,
        header=False)
report_sxw.report_sxw('report.account.third_party_ledger_other.opti', 'res.partner',
        'addons/account/report/account_partner_ledger_other.rml', parser=third_party_ledger,
        header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
