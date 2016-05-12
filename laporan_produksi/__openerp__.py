##############################################################################
#
#    Vikasa Infinity Anugrah, PT
#    Copyright (c) 2011 - 2012 Vikasa Infinity Anugrah <http://www.infi-nity.com>
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
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "aaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "version": "1.1",
    "author": "ADSOFT",
    "category": "Generic Modules/Accounting",
    "description": """
    This module enhances Avanzosc's account_invoice_analytics, particularly for 
    the installment invoicing method:
    * Defaulting of Analytic Account during SO creation, using the Default 
      Analytic Account mechanism 
    * Make the Analytic Account field required if the Shipping Policy is Invoice
      From Analytics
    * Relate the sale order line with the corresponding account analytic line and
      display it as "Installments" under a new tab
    * Extend wizard to link SO and SO line items to created invoices
    * Provide (default) option to use analytical line date as due date with option to calculate 
      it based on customer's payment term  
    * Provide functionality to make multiple partial payment against an installment
    """,
    "website" : "http://www.adsoft.co.id",
    "license" : "GPL-3",
    "depends": [
                "account",
                ],
    "init_xml": [],
    'update_xml': [
                   "view_laporan_produksi.xml",
                  
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
