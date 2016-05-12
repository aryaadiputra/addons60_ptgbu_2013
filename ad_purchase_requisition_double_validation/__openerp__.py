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
    "name" : "Purchase - Purchase Requisition Double Validation",
    "version" : "0.1",
    "author" : "OpenERP SA",
    "category" : "Custom Modules PTGBU/Sales & Purchases",
    "website" : "http://www.openerp.com",
    "description": """
    Module ini untuk menambahkan Approval dari Admin User - Manager Dept - Kadiv
    """,
    "depends" : ["purchase","purchase_requisition"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["purchase_requisition_workflow.xml",
                    "purchase_requisition_view.xml",
                    
    ],
    "active": False,
    "test":[],
    "installable": True,
    "certificate" : "",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

