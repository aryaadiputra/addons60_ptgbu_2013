# -*- coding: utf-8 -*-
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

{
    "name" : "Accounting Cash Settlement",
    "version" : "1.0",
    "author" : 'ADSOFT',
    "description": """Cash Settlement modules same like Account Voucher
    
    Added : 
        - Settlemnet Receive Date
        - Select Method Settlement
        - Rounding
        - Cash Advance Pay Administration
        - Wkf From Employee
        - Ticket Relation to Supplier Invoice
        - Approval CEO
        - Group Deleted
        - Pooling Budget
    
    """,
    "category" : "Cash Advance & Settlement Menu Multi Currencies Support",
    "website" : "http://www.adsoft.co.id",
    "depends" : ["account","ad_acc_inv_double_validation"],
    "init_xml" : [],

    "demo_xml" : [],

    "update_xml" : [
        "wizard/cash_advance_report_view.xml",
        "partner_view.xml",
        "cash_advance.xml",
        "workflow_advance.xml",
        "cash_settlement.xml",
        "workflow_settlement.xml",
        "base_update.xml",
        "advance_type_view.xml",
        "invoice_view.xml",
        "pool_budget_view.xml",
        
    ],
    "test" : [],
    'certificate': '',
    "active": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: