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
{
    "name" : "Check writing",
    "version" : "1.83",
    "author" : "OpenERP SA",
    "category": "Generic Modules/Accounting",
    "description": """
    Module for the Check writing and check printing
    """,
    'website': 'http://www.openerp.com',
    'init_xml': [],
    "depends" : [
        "account_voucher",
        'account_voucher_credits_us',    #To make working onchange_partner_id function
        'purchase',
        'account_cash_discount_us'                      #To find the invoice related to purchase for adding invoice reference in reception in check
        ],
    'update_xml': [
        'wizard/check_print_view.xml',
        'check_sequence.xml',
        'account_check_writing_report.xml',
        'account_view.xml',
        'account_voucher_view.xml',
    ],
    'demo_xml': [
        'account_demo.xml',
    ],
    'test': [
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
