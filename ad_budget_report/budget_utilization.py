from osv import osv,fields
from tools.translate import _
import tools
import pooler
import time

class br_wizard(osv.osv_memory):
    _name       = 'br.wizard'
    _columns    = {
                   'name'               : fields.selection([('pdf','PDF'), ('xls','Excel')], 'Type', required=False),
                   'period_id'          : fields.many2one('account.period', 'Period', required=True),
                   'cut_date'           : fields.date('As of'),
                   'dept_relation'      : fields.many2one('hr.department','Department'),
                   'budget_item2'       : fields.many2many('ad_budget.item','wizard_item_rel','item_id','wizard_id','Budget Item',required=True),
                   'dept_relation2'     : fields.many2many('hr.department','wizard_dept_rel','dept_id','wizard_id','Department'),
                   'display_account_level': fields.integer('Up to level',help= 'Display accounts up to this level (0 to show all)'),
                   'without_zero': fields.boolean('Without zero amount', help="Check this if report without zero budget"),
                   }
    _defaults   = {
                   'name'       : 'xls',
                   'display_account_level': lambda *a: 0,
                   }
    
    def onchange_date(self,cr,uid,ids,date,period):
        val={}
        if date:
            if not period:
                val['warning']  = {'title': 'Warning', 'message': 'Please select period first.'}
                val['value']    = {'cut_date':False}
                return val
            period = self.pool.get('account.period').browse(cr,uid,period)
            if date < period.date_start or date > period.date_stop:
                val['warning']  = {'title': 'Date out of range', 'message': 'Date is out of period range you select.'}
                val['value']    = {'cut_date':False}
        return val
    
    def report_budget(self, cr, uid, ids, context):
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'br.wizard'
        datas['form'] = self.read(cr, uid, ids)[0]
#        return {
#                'type': 'ir.actions.report.xml',
#                'report_name': 'budgets.report',
#                'report_type': 'webkit',
#                'datas': datas,
#                }
        if datas['form']['name'] == 'pdf':
            return { 
                'type': 'ir.actions.report.xml',
                'report_name': 'budgets.report.pdf',
                'report_type': 'webkit',
                'datas': datas,
            }
        else:    
            return { 
                'type': 'ir.actions.report.xml',
                'report_name': 'budgets.report.xls',
                'report_type': 'webkit',
                'datas': datas,
            }
br_wizard()