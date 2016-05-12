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
    "name" : "Controller Purchase Requisition",
    "version" : "0.1",
    "author" : "ADSOFT",
    "category" : "Generic Modules/Sales & Purchases",
    "website" : "http://www.openerp.co.id",
    "description": """ Controller PR to PO 
        Added :
        - Required Field Origin
        - Keterangan dilempar ke Notes PO
        - RFQ Number
        - def Create Po Number
    
    """,
    "depends" : ["purchase", "purchase_requisition"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["purchase_requisition_report.xml",
                    "purchase_requisition_view.xml",
                    "purchase_order_view.xml",],
    "active": False,
    "installable": True,
}
