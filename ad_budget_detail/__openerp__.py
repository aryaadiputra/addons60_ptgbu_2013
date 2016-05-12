# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) Camptocamp SA - http://www.camptocamp.com
# Author: Arnaud WÃŒst ported by nbessi
#
#    This file is part of the ad_budget module
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
{
    "name" : "Budget Detail Report",
    "version" : "1.0",
    "author" : "ADSOFT",
    "category" : "Generic Modules/Accounting",
    "website" : "http://adsoft.co.id",
    "description": """
    This module aim to add new object budget division
    """,
    "depends" : [
                    "base",
                    "account",
                    "c2c_reporting_tools",
                    "chricar_account_period_sum",
                    #"hr",
                    "ad_budget",
                    "ad_budget_report",
                ],
    "init_xml" : [],
    "update_xml" : [
                    #"hr_department_view.xml",
                    "budget_detail_report.xml",
                    "budget_detail_view.xml",                   
                    ],
    "active": False,
    "installable": True
}