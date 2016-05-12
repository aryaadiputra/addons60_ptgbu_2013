# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 CamptoCamp
# Copyright (c) 2006-2010 OpenERP S.A
# Copyright (c) 2011 Thamini S.à.R.L
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from report import report_sxw
from common_report_header import common_report_header

class general_ledger(report_sxw.rml_parse, common_report_header):
    _name = 'report.account.general.ledger'

    def strip_name(self, char, size=50, truncation_str='...'):
        if not char:
            return ""
        if len(char) <= size:
            return char
        return char[:size-len(truncation_str)] + truncation_str

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        obj_move = self.pool.get('account.move.line')
        self.sortby = data['form'].get('sortby', 'sort_date')
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=data['form'].get('used_context',{}))
        ctx2 = data['form'].get('used_context',{}).copy()
        ctx2.update({'initial_bal': True})
        self.init_query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx2)
        self.init_balance = data['form']['initial_balance']
        self.display_account = data['form']['display_account']
        self.target_move = data['form'].get('target_move', 'all')
        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form']['fiscalyear_id']
        if data['form']['filter'] == 'filter_period':
            ### XXX: FIX FIX FIX
            if data['form']['periods']:
                ctx['periods'] = data['form']['periods']
            else:
                ctx['period_from'] = data['form']['period_from']
                ctx['period_to'] = data['form']['period_to']
            ### XXX: FIX FIX FIX
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form']['date_from']
            ctx['date_to'] =  data['form']['date_to']
        ctx['state'] = data['form']['target_move']
        ### XXX: FIX FIX FIX
        ctx['initial_bal'] = data['form'].get('initial_balance',False)
        ### XXX: FIX FIX FIX
        self.context.update(ctx)
        if (data['model'] == 'ir.ui.menu'):
            new_ids = [data['form']['chart_account_id']]
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(general_ledger, self).set_context(objects, data, new_ids, report_type=report_type)

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(general_ledger, self).__init__(cr, uid, name, context=context)
        self.query = ""
        self.tot_currency = 0.0
        self.period_sql = ""
        self.sold_accounts = {}
        self.sortby = 'sort_date'
        self.localcontext.update( {
            'time': time,
            'lines': self.lines,
            'count_lines': self.count_lines,
            'strip_name': self.strip_name,
            'sum_debit_account': self._sum_debit_account,
            'sum_credit_account': self._sum_credit_account,
            'sum_balance_account': self._sum_balance_account,
            'sum_currency_amount_account': self._sum_currency_amount_account,
            'sum_currency_account': self._sum_currency_account,
            'get_children_accounts': self.get_children_accounts,
            'get_fiscalyear': self._get_fiscalyear,
            'get_journal': self._get_journal,
            'get_account': self._get_account,
            'get_filter_string': self.get_filter_string,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_filter': self._get_filter,
            'get_sortby': self._get_sortby,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
            'currency_rate': self._currency_rate,
            'currency_id': self._currency_id,
            #'sum_currency_amount_account_idr':self._sum_currency_amount_account_idr
        })
        self.context = context
        self.qcache = {}
        self.ilcache = {} # init line cache

    def get_filter_string(self, data):
        filter_mode = self._get_filter(data)
        if filter_mode == 'Date':
            return 'Date: %s -> %s' % (self._formatLang(get_start_date(data), date=True),
                                       self._formatLang(get_end_date(data), date=True))
        elif filter_mode == 'Periods':
            return 'Periods: %s -> %s' % (self.get_start_period(data),
                                          self.get_end_period(data))
        else:
            return filter_mode

    def _sum_currency_account(self, account):
        self.cr.execute('SELECT sum(l.amount_currency) AS tot_currency \
                FROM account_move_line l \
                WHERE l.account_id = %s AND %s' %(account.id, self.query))
        sum_currency = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT sum(l.amount_currency) AS tot_currency \
                            FROM account_move_line l \
                            WHERE l.account_id = %s AND %s '%(account.id, self.init_query))
            sum_currency += self.cr.fetchone()[0] or 0.0
        return sum_currency


    def get_children_accounts(self, account):
        res = []
        currency_obj = self.pool.get('res.currency')
        ids_acc = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, account.id)
        currency = account.currency_id and account.currency_id or account.company_id.currency_id
        for child_account in self.pool.get('account.account').browse(self.cr, self.uid, ids_acc, context=self.context):
            sql = """
                SELECT count(id)
                FROM account_move_line AS l
                WHERE %s AND l.account_id = %%s
            """ % (self.query)
            self.cr.execute(sql, (child_account.id,))
            num_entry = self.cr.fetchone()[0] or 0
            sold_account = self._sum_balance_account(child_account)
            self.sold_accounts[child_account.id] = sold_account
            if self.display_account == 'movement':
                if child_account.type != 'view' and num_entry <> 0:
                    res.append(child_account)
            elif self.display_account == 'not_zero':
                if child_account.type != 'view' and num_entry <> 0:
                    if not currency_obj.is_zero(self.cr, self.uid, currency, sold_account):
                        res.append(child_account)
            else:
                res.append(child_account)
        if not res:
            return [account]
        return res

############################Perbaikan Net Initial Balance##########################################
#    def get_children_accounts(self, account):
#        res = []
#        ids_acc = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, [account.id])
#        tuple_ids_acc = tuple(ids_acc)
#        for child_account in ids_acc:
#            self.qcache.setdefault(child_account, {'num_entry': 0,
#                            'debit': 0.0, 'credit': 0.0, 'balance': 0.0, 'currency': 0.0, 'num_entry': 0,
#                            'init_debit': 0.0, 'init_credit': 0.0, 'init_balance': 0.0, 'init_currency': 0.0 })
#        q = """
#            SELECT l.account_id,
#                   count(l.id) AS num_entry,
#                   COALESCE(SUM(l.debit),0.0) AS debit,
#                   COALESCE(SUM(l.credit),0.0) AS credit,
#                   COALESCE(SUM(l.debit),0.0) - COALESCE(SUM(l.credit),0.0) AS balance,
#                   COALESCE(SUM(l.amount_currency),0.0) AS currency
#            FROM account_move_line AS l
#            WHERE %s
#              AND l.account_id IN %%s
#            GROUP BY l.account_id
#            """ % (self.query)
#        self.cr.execute(q, (tuple_ids_acc,))
#        for a in self.cr.dictfetchall():
#            aid = a.pop('account_id')
#            self.qcache[aid].update(a)
#
#        if self.init_balance:
#            move_state = ['draft','posted']
#            if self.target_move == 'posted':
#                move_state = ['posted','']
#
#            # Compute account initial debit / credit / balance
#            q = """
#                SELECT l.account_id,
#                       COALESCE(SUM(l.debit),0) AS init_debit,
#                       COALESCE(SUM(l.credit),0) AS init_credit,
#                       COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit),0) AS init_balance,
#                       COALESCE(SUM(l.amount_currency),0) AS init_currency
#                FROM account_move_line l
#                JOIN account_move am ON (am.id = l.move_id)
#                WHERE (am.state IN %s)
#                AND %s
#                AND l.account_id IN %%s
#                GROUP BY l.account_id
#                """ % (move_state, self.init_query)
#            self.cr.execute(q, (tuple_ids_acc,))
#            for a in self.cr.dictfetchall():
#                aid = a.pop('account_id')
#                self.qcache[aid].update(a)
#
#            # Compute account initial line
#            #FIXME: replace the label of lname with a string translatable
#            sql = """
#                SELECT l.account_id, 0 AS lid, '' AS ldate, '' AS lcode, COALESCE(SUM(l.amount_currency),0.0) AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, '' AS lperiod_id, '' AS lpartner_id,
#                '' AS move_name, '' AS mmove_id, '' AS period_code,
#                '' AS currency_code,
#                NULL AS currency_id,
#                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,
#                '' AS partner_name
#                FROM account_move_line l
#                LEFT JOIN account_move m on (l.move_id=m.id)
#                LEFT JOIN res_currency c on (l.currency_id=c.id)
#                LEFT JOIN res_partner p on (l.partner_id=p.id)
#                LEFT JOIN account_invoice i on (m.id =i.move_id)
#                JOIN account_journal j on (l.journal_id=j.id)
#                WHERE %s AND m.state IN %s AND l.account_id IN %%s
#                GROUP BY l.account_id
#                """ % (self.init_query, tuple(move_state))
#            self.cr.execute(sql, (tuple_ids_acc,))
#            for ailine in self.cr.dictfetchall():
#                self.ilcache[ailine['account_id']] = ailine
#
#        for child_account in self.pool.get('account.account').browse(self.cr, self.uid, ids_acc, context=self.context):
#            #sql = """
#            #    SELECT count(id)
#            #    FROM account_move_line AS l
#            #    WHERE %s AND l.account_id = %%s
#            #""" % (self.query)
#            #print("SQL: %s" % (sql))
#            #self.cr.execute(sql, (child_account.id,))
#            #num_entry = self.cr.fetchone()[0] or 0
#            num_entry = self.qcache[child_account.id]['num_entry']
#            if self.display_account == 'bal_movement':
#                if child_account.type != 'view' and num_entry <> 0:
#                    res.append(child_account)
#            elif self.display_account == 'bal_solde':
#                sold_account = self._sum_balance_account(child_account)
#                self.sold_accounts[child_account.id] = sold_account
#                if child_account.type != 'view' and num_entry <> 0:
#                    if ( sold_account <> 0.0):
#                        res.append(child_account)
#            else:
#                res.append(child_account)
#        if not res:
#            return [account]
#        return res

    def count_lines(self, account):
        return self.qcache[account.id]['num_entry']

    def lines(self, account):
        """ Return all the account_move_line of account with their account code counterparts """
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted', '']
        # First compute all counterpart strings for every move_id where this account appear.
        # Currently, the counterpart info is used only in landscape mode
        sql = """
            SELECT m1.move_id,
                array_to_string(ARRAY(SELECT DISTINCT a.code
                                          FROM account_move_line m2
                                          LEFT JOIN account_account a ON (m2.account_id=a.id)
                                          WHERE m2.move_id = m1.move_id
                                          AND m2.account_id<>%%s), ', ') AS counterpart
                FROM (SELECT move_id
                        FROM account_move_line l
                        LEFT JOIN account_move am ON (am.id = l.move_id)
                        WHERE am.state IN %s and %s AND l.account_id = %%s GROUP BY move_id) m1
        """% (tuple(move_state), self.query)
        self.cr.execute(sql, (account.id, account.id))
        counterpart_res = self.cr.dictfetchall()
        counterpart_accounts = {}
        for i in counterpart_res:
            counterpart_accounts[i['move_id']] = i['counterpart']
        del counterpart_res

        # Then select all account_move_line of this account
        if self.sortby == 'sort_journal_partner':
            sql_sort='j.code, p.name, l.move_id'
        else:
            sql_sort='l.date, l.move_id'
        sql = """
        
            SELECT (SELECT concat (code, ' ', name) FROM account_account WHERE id = l.account_id) AS laccount_name, m.move_name_manual AS mmove_name_manual, l.id AS lid, l.date AS ldate, j.code AS lcode, l.currency_id,l.amount_currency,l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, l.period_id AS lperiod_id, l.partner_id AS lpartner_id,
            m.name AS move_name, m.id AS mmove_id,per.code as period_code,
            c.symbol AS currency_code,
            i.id AS invoice_id, i.type AS invoice_type, i.number AS invoice_number,
            p.name AS partner_name
            FROM account_move_line l
            JOIN account_move m on (l.move_id=m.id)
            LEFT JOIN res_currency c on (l.currency_id=c.id)
            LEFT JOIN res_partner p on (l.partner_id=p.id)
            LEFT JOIN account_invoice i on (m.id =i.move_id)
            LEFT JOIN account_period per on (per.id=l.period_id)
            JOIN account_journal j on (l.journal_id=j.id)
            WHERE %s AND m.state IN %s AND l.account_id = %%s ORDER by %s
        """ %(self.query, tuple(move_state), sql_sort)
        self.cr.execute(sql, (account.id,))
        res_lines = self.cr.dictfetchall()
        res_init = []
        if res_lines and self.init_balance:
            #FIXME: replace the label of lname with a string translatable
            sql = """
                SELECT '' AS laccount_name, '' AS mmove_name_manual, 0 AS lid, '' AS ldate, '' AS lcode, COALESCE(SUM(l.amount_currency),0.0) AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, '' AS lperiod_id, '' AS lpartner_id,
                '' AS move_name, '' AS mmove_id, '' AS period_code,
                '' AS currency_code,
                NULL AS currency_id,
                '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,
                '' AS partner_name
                FROM account_move_line l
                LEFT JOIN account_move m on (l.move_id=m.id)
                LEFT JOIN res_currency c on (l.currency_id=c.id)
                LEFT JOIN res_partner p on (l.partner_id=p.id)
                LEFT JOIN account_invoice i on (m.id =i.move_id)
                JOIN account_journal j on (l.journal_id=j.id)
                WHERE %s AND m.state IN %s AND l.account_id = %%s
            """ %(self.init_query, tuple(move_state))
            self.cr.execute(sql, (account.id,))
            res_init = self.cr.dictfetchall()
        res = res_init + res_lines
        account_sum = 0.0
        for l in res:
            l['move'] = l['move_name'] != '/' and l['move_name'] or ('*'+str(l['mmove_id']))
            l['partner'] = l['partner_name'] or ''
            account_sum += l['debit'] - l['credit']
            l['progress'] = account_sum
            l['line_corresp'] = l['mmove_id'] == '' and ' ' or counterpart_accounts[l['mmove_id']].replace(', ',',')
            # Modification of amount Currency
            if l['credit'] > 0:
                if l['amount_currency'] != None:
                    l['amount_currency'] = abs(l['amount_currency']) * -1
            if l['amount_currency'] != None:
                self.tot_currency = self.tot_currency + l['amount_currency']
        return res

######################Perbaikan Initial Balance###############################################
#    def lines(self, account):
#        """ Return all the account_move_line of account with their account code counterparts """
#        if self.qcache[account.id]['num_entry'] == 0:
#            # XXX: No lines, we already known that
#            # XXX: Do we need to diplay the 'Intial Balance' line?
#            return []
#        move_state = ['draft','posted']
#        if self.target_move == 'posted':
#            move_state = ['posted', '']
#        # First compute all counterpart strings for every move_id where this account appear.
#        # Currently, the counterpart info is used only in landscape mode
#        sql = """
#            SELECT m1.move_id,
#                array_to_string(ARRAY(SELECT DISTINCT a.code
#                                          FROM account_move_line m2
#                                          LEFT JOIN account_account a ON (m2.account_id=a.id)
#                                          WHERE m2.move_id = m1.move_id
#                                          AND m2.account_id<>%%s), ', ') AS counterpart
#                FROM (SELECT move_id
#                        FROM account_move_line l
#                        LEFT JOIN account_move am ON (am.id = l.move_id)
#                        WHERE am.state IN %s and %s AND l.account_id = %%s GROUP BY move_id) m1
#        """% (tuple(move_state), self.query)
#        self.cr.execute(sql, (account.id, account.id))
#        counterpart_res = self.cr.dictfetchall()
#        counterpart_accounts = {}
#        for i in counterpart_res:
#            counterpart_accounts[i['move_id']] = i['counterpart']
#        del counterpart_res
#
#        # Then select all account_move_line of this account
#        if self.sortby == 'sort_journal_partner':
#            sql_sort='j.code, p.name, l.move_id'
#        else:
#            sql_sort='l.date, l.move_id'
#        sql = """
#            SELECT l.id AS lid,
#                   l.date AS ldate,
#                   j.code AS lcode,
#                   l.currency_id,
#                   l.amount_currency,
#                   l.ref AS lref,
#                   l.name AS lname,
#                   COALESCE(l.debit,0) AS debit,
#                   COALESCE(l.credit,0) AS credit,
#                   l.period_id AS lperiod_id,
#                   l.partner_id AS lpartner_id,
#                   m.name AS move_name,
#                   m.id AS mmove_id,
#                   per.code as period_code,
#                   c.symbol AS currency_code,
#                   i.id AS invoice_id,
#                   i.type AS invoice_type,
#                   i.number AS invoice_number,
#                   p.name AS partner_name
#            FROM account_move_line l
#            JOIN account_move m on (l.move_id=m.id)
#            LEFT JOIN res_currency c on (l.currency_id=c.id)
#            LEFT JOIN res_partner p on (l.partner_id=p.id)
#            LEFT JOIN account_invoice i on (m.id =i.move_id)
#            LEFT JOIN account_period per on (per.id=l.period_id)
#            JOIN account_journal j on (l.journal_id=j.id)
#            WHERE %s AND m.state IN %s AND l.account_id = %%s ORDER by %s
#        """ %(self.query, tuple(move_state), sql_sort)
#        self.cr.execute(sql, (account.id,))
#        res_lines = self.cr.dictfetchall()
#        res_init = []
#        if res_lines and self.init_balance:
#            res_init = ilcache.get(account.id, [])
#        if res_init:
#            res = res_init + res_lines
#        else:
#            res = res_lines
#        account_sum = 0.0
#        for l in res:
#            l['move'] = l['move_name'] != '/' and l['move_name'] or ('*'+str(l['mmove_id']))
#            l['partner'] = l['partner_name'] or ''
#            account_sum += l['debit'] - l['credit']
#            l['progress'] = account_sum
#            l['line_corresp'] = l['mmove_id'] == '' and ' ' or counterpart_accounts[l['mmove_id']].replace(', ',',')
#            # Modification of amount Currency
#            if l['credit'] > 0:
#                if l['amount_currency'] != None:
#                    l['amount_currency'] = abs(l['amount_currency']) * -1
#            if l['amount_currency'] != None:
#                self.tot_currency = self.tot_currency + l['amount_currency']
#        return res

#    def _sum_debit_account(self, account):
#        if account.type == 'view':
#            return account.debit
#        sum_debit = self.qcache[account.id]['debit']
#        if self.init_balance:
#            sum_debit += self.qcache[account.id]['init_debit']
#        return sum_debit
################Menggunakan Versi 6.1#######################
    def _sum_debit_account(self, account):
        if account.type == 'view':
            return account.debit
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted','']
        self.cr.execute('SELECT sum(debit) \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND '+ self.query +' '
                ,(account.id, tuple(move_state)))
        sum_debit = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT sum(debit) \
                    FROM account_move_line l \
                    JOIN account_move am ON (am.id = l.move_id) \
                    WHERE (l.account_id = %s) \
                    AND (am.state IN %s) \
                    AND '+ self.init_query +' '
                    ,(account.id, tuple(move_state)))
            # Add initial balance to the result
            sum_debit += self.cr.fetchone()[0] or 0.0
        return sum_debit
##############################################################
#    def _sum_credit_account(self, account):
#        if account.type == 'view':
#            return account.credit
#        sum_credit = self.qcache[account.id]['credit']
#        if self.init_balance:
#            sum_credit += self.qcache[account.id]['init_credit']
#        return sum_credit
################Menggunakan Versi 6.1#######################
    def _sum_credit_account(self, account):
        if account.type == 'view':
            return account.credit
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted','']
        self.cr.execute('SELECT sum(credit) \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND '+ self.query +' '
                ,(account.id, tuple(move_state)))
        sum_credit = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT sum(credit) \
                    FROM account_move_line l \
                    JOIN account_move am ON (am.id = l.move_id) \
                    WHERE (l.account_id = %s) \
                    AND (am.state IN %s) \
                    AND '+ self.init_query +' '
                    ,(account.id, tuple(move_state)))
            # Add initial balance to the result
            sum_credit += self.cr.fetchone()[0] or 0.0
        return sum_credit
###############################################################
#    def _sum_balance_account(self, account):
#        if account.type == 'view':
#            return account.balance
#        sum_balance = self.qcache[account.id]['balance']
#        if self.init_balance:
#            sum_balance += self.qcache[account.id]['init_balance']
#        return sum_balance
################Menggunakan Versi 6.1#######################
    def _sum_balance_account(self, account):
        if account.type == 'view':
            return account.balance
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted','']
        self.cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                FROM account_move_line l \
                JOIN account_move am ON (am.id = l.move_id) \
                WHERE (l.account_id = %s) \
                AND (am.state IN %s) \
                AND '+ self.query +' '
                ,(account.id, tuple(move_state)))
        sum_balance = self.cr.fetchone()[0] or 0.0
        if self.init_balance:
            self.cr.execute('SELECT (sum(debit) - sum(credit)) as tot_balance \
                    FROM account_move_line l \
                    JOIN account_move am ON (am.id = l.move_id) \
                    WHERE (l.account_id = %s) \
                    AND (am.state IN %s) \
                    AND '+ self.init_query +' '
                    ,(account.id, tuple(move_state)))
            # Add initial balance to the result
            sum_balance += self.cr.fetchone()[0] or 0.0
        return sum_balance
#############################################################
    def _get_account(self, data):
        if data['model'] == 'account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(general_ledger ,self)._get_account(data)

    def _get_sortby(self, data):
        if self.sortby == 'sort_date':
            return 'Date'
        elif self.sortby == 'sort_journal_partner':
            return 'Journal & Partner'
        return 'Date'
    
    def _currency_rate(self, ids, cur_id):
        obj_currency = self.pool.get('account.move.line').browse(self.cr, self.uid, ids)
        if cur_id <> obj_currency.currency_id.id:
            amount = abs(obj_currency.amount_currency)
        else:
            amount = ''
        return amount
    
    def _currency_id(self, ids, cur_id):
        obj_currency = self.pool.get('account.move.line').browse(self.cr, self.uid, ids)
        if cur_id <> obj_currency.currency_id.id:
            aid = obj_currency.currency_id.symbol
        else:
            aid = ''
        return aid
    
    def _sum_currency_amount_account(self, currency):
        # 1 = latest rate, 0 = average
        pilihan = 1 
        if pilihan == 1:
            qry= '''select b.rate as rate from res_currency a
                    left join res_currency_rate b on a.id = b.currency_id and b.id = (select max(id) from res_currency_rate c where c.currency_id=b.currency_id) 
                    where a.name = 'IDR' '''
        else:
            qry= '''select avg(b.rate) as rate from res_currency a
                    left join res_currency_rate b on a.id = b.currency_id
                    where a.name = 'IDR' group by a.name'''
            
        self.cr.execute(qry)
        sum_currency = self.cr.fetchone()[0] or 0.0
        #print "yyyy",sum_currency
        total = sum_currency*currency
        return total

report_sxw.report_sxw('report.account.general.ledger.ls', 'account.account', 'addons/ad_account_optimization/report/account_general_ledger_landscape.rml', parser=general_ledger, header="internal landscape")
#report_sxw.report_sxw('report.account.general.ledger_landscape.opti', 'account.account', 'addons/account_optimization/report/account_general_ledger_landscape.rml', parser=general_ledger, header=False)
#report_sxw.report_sxw('report.account.general.ledger_landscape.opti.currency', 'account.account', 'addons/account_optimization/report/account_general_ledger_landscape_currency.rml', parser=general_ledger, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
