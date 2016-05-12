# -*- coding: utf-8 -*-
##############################################################################
#
#   OpenERP, Open Source Management Solution    
#   Copyright (C) 2013 ADSOft (<http://www.adsoft.co.id>). All Rights Reserved
#
##############################################################################

from osv import osv, fields

class cash_flow(osv.osv_memory):
    _name = 'cash.flow'
    _description = 'Cash Flow'

    _columns = {
        'without_zero': fields.boolean('Without zero amount', help="Check this if report without zero budget"),
        'date_start': fields.date('Date Start', required=True),
        'date_stop': fields.date('Date Stop', required=True),
    }
    
    
    def print_cash_flow(self, cr, uid, ids, context):
        print "--------------------------------->>"
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'cash.flow'
        datas['form'] = self.read(cr, uid, ids)[0]
        form = datas['form']
    
        return {
            'type': 'ir.actions.report.xml',
            #'report_name': 'cash.flow.report',
            'report_name': 'cash.flow.report.xls',
            'report_type': 'webkit',
            'datas': datas,
        }

cash_flow()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: