# -*- coding: utf-8 -*-
##############################################################################
#
#   OpenERP, Open Source Management Solution    
#   Copyright (C) 2013 ADSOft (<http://www.adsoft.co.id>). All Rights Reserved
#
##############################################################################

{
    'name': 'Report Cash Flow',
    'description': """Cash Flow Report""",
    'version': '1.0',
    'author' : 'ADSOFT',
    'category': 'Custom Report/List Customer',
    'depends' : [
                    'base',
                    'account',
                    #'ad_cash_settlement'
                ],
    'init_xml' : [],
    'update_xml': [
        #'cash_flow_category_view.xml',
        #'account_view.xml',
        'wizard/raw_data_view.xml',
                ],
    'demo_xml': [
                ],
    'active': False,
    'installable': True,
    'certificate': '',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: