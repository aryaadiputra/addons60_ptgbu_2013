##############################################################################
#
#    Copyright (C) 2009 Almacom (Thailand) Ltd.
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "Account Cheque",
    "version" : "0.1",
    "depends" : ["account", "account_payment", "account_voucher"],
    "author" : "ADSOFT",
    "website" : "http://adsoft.co.id/",
    "description": """
     This module cheque for accounting.
    """,
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "security/ir.model.access.csv",
        "account_check_view.xml",
        #"ad_check_payment_view.xml",
        #"voucher_payment_receipt_view.xml",
        ],
    "installable": True,
}
