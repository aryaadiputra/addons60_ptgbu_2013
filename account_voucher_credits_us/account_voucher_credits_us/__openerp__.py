# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com) All Rights Reserved.
# sinoj@zbeanztech.com
#
##############################################################################
{
    "name" : "Voucher modifications for US",
    "version" : "0.07",
    "author" : 'Voucher and NovaPoint Group LLC',
    "description": """
This module will add new functionality to better manage credits and how and when they apply to Sales Payments. 
The result of this development will enable users to designate which credit(s) will apply to each individual invoice, and how much of an individual credit amount to apply.
    """,
    "category" : "Generic Modules/Accounting",
    "website" : "http://www.novapointgroup.com/",
    "depends" : ["account", "account_voucher",],
    "init_xml" : [],

    "demo_xml" : [],

    "update_xml" : [
        "voucher_payment_receipt_view.xml",
        "wizard/account_post_voucher.xml",],
    "test" : [],
    "active": False,
    "installable": True,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
