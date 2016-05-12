# -*- coding: utf-8 -*-
##############################################################################
#
#    account_optimization module for OpenERP, Account Optimizations
#    Copyright (C) 2011 Thamini S.à.R.L (<http://www.thamini.com) Xavier ALT
#
#    This file is a part of account_optimization
#
#    account_optimization is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    account_optimization is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'account_optimization',
    'version': '0.1',
    'author': 'Thamini S.à.R.L',
    'website': 'http://www.thamini.com',
    'description': """
        Account Optimizations
        
        Added :
        - Perbaikan Initial Balance
        - Perbaikan P & L mengambil data hanya Yang Posted
    """,
    'depends': [
        'base',
        'account',
        'smtpclient',
    ],
    'init_xml': [
    ],
    'demo_xml': [
    ],
    'update_xml': [
        'account_bank_statement_view.xml',
        'account_fiscal_position_view.xml',
        'security/ir.model.access.csv',
        'wizard/account_report_account_balance_view_i.xml',
        'wizard/account_report_partner_balance_view_i.xml',
        'wizard/account_report_aged_partner_balance_view_i.xml',
        'wizard/account_report_general_ledger_view_i.xml',
        'wizard/account_report_partner_ledger_view_i.xml',
        'wizard/account_report_account_bs_view_i.xml',
        'wizard/account_report_profit_loss_view_i.xml',
        'account_report_report.xml',
        'account_report_wizard.xml',
        
        'report/account_balance_sheet_new.xml',
        'report/account_profit_loss_new.xml'
    ],
    'active': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
