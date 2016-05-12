# -*- coding: utf-8 -*-
##############################################################################
#
#   OpenERP, Open Source Management Solution    
#   Copyright (C) 2013 ADSOft (<http://www.adsoft.co.id>). All Rights Reserved
#
##############################################################################

from osv import osv, fields

class raw_data(osv.osv_memory):
    _name = 'raw.data'
    _description = 'Raw Data'

    _columns = {
        'without_zero': fields.boolean('Without zero amount', help="Check this if report without zero budget"),
        'period_start' : fields.many2one('account.period', 'Start', required=True),
        'period_end' : fields.many2one('account.period', 'End', required=True),
    }
    
    
    def print_raw_data(self, cr, uid, ids, context):
        print "--------------------------------->>"
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'raw.data'
        datas['form'] = self.read(cr, uid, ids)[0]
        form = datas['form']
    
        return {
            'type': 'ir.actions.report.xml',
            #'report_name': 'cash.flow.report',
            'report_name': 'raw.data.report.xls',
            'report_type': 'webkit',
            'datas': datas,
        }

raw_data()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: