# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

{
    "name" : "Payment Term with Cash Discount",
    "version" : "1.07",
    "depends" : ["account","account_voucher_credits_us","account_cash_discount"],
    "author" : "Tiny and NovaPoint Group LLC",
    "description" : "Cash discounts, based on payment terms",
    "website" : "http://www.novapointgroup.com/",
    "category" : "Generic Modules/Accounting",
    "description": """
    This module adds cash discounts on payment terms. Cash discounts
    for a payment term can be configured with:
        * A number of days,
        * A discount (%),
        * A debit and a credit account 
        * Sales and Purchase discounts are added to product and invoice line
    """,
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "account_cash_discount_view.xml",
        "product_view.xml",
        "security/ir.model.access.csv",
    ],
    "active": False,
    "installable": True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

