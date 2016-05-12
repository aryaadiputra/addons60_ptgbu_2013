import time
from osv import osv, fields

class budget_detail(osv.osv_memory):
    _name = "budget.detail.report"
    _columns = {
        #'status_id': fields.many2many('sale.order', 'sale_line_rel', 'sale_line_id', 'sale_id', 'Sales Order', required=True),
#        'date_from': fields.date('Start Date', required=True),
#        'date_to': fields.date('End Date', required=True),
#        'state': fields.selection([
#            ('draft', 'Quotation'),
#            ('waiting_date', 'Waiting Schedule'),
#            ('manual', 'Manual In Progress'),
#            ('progress', 'In Progress'),
#            ('shipping_except', 'Shipping Exception'),
#            ('invoice_except', 'Invoice Exception'),
#            ('done', 'Done'),
#            ('cancel', 'Cancelled')
#            ], 'Order State', select=True, required=True),
        'without_zero': fields.boolean('Without zero amount', help="Check this if report without zero budget"),
#        'user_ids': fields.many2many('res.users', 'sale_user_rel', 'sale_line_id', 'user_id'),
#        'customer_ids': fields.many2many('res.partner', 'sale_partner_rel', 'sale_line_id', 'partner_id'),
#        'groupby': fields.selection([
#            ('salesman', 'Salesman'),
#            ('customer', 'Customer'),
#            ('none', 'None'),
#            ],'Group By', required=True)
        #'date_from': {'string':"Sale Start date", 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-01-01')},
        #'date_to': {'string':"Sale End date", 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal year', help='Keep empty for all open fiscal year'),
        'budget_item_id': fields.many2one('ad_budget.item', 'Budget', help='Select Budget', required=True,),
        'type': fields.selection([('pdf','PDF'),('xls','Excel')], 'Type', required=True),
        'with_detail' : fields.boolean('With Detail Account', help="Check this if report without Detail Account"),
        'budget_item_select'    : fields.many2many('ad_budget.item', 'budget_item_line_select', 'ad_budget_item_id', 'item_id', 'Budget Items'),
        'period_id'             : fields.many2one('account.period', 'Period', required=False),
        #'dept_relation'         : fields.many2one('hr.department','Department'),
        #'div_relation'          : fields.related('dept_relation','division_id',type='many2one',relation='hr.division',string='Division'),
        'with_transaction'      : fields.boolean('With Transaction', help="Check this if report without Detail Transaction"),
        'department_select'     : fields.many2many('hr.department', 'wizard_dept_rel', 'department_id', 'wizard_id', 'Department', ),
        'as_of_date'            : fields.date('As of'),
        'display_account_level': fields.integer('Up to level',help= 'Display accounts up to this level (0 to show all)'),
    }
    
    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False
    
    def _get_budget(self, cr, uid, context=None):
        budgets = self.pool.get('ad_budget.item').search(cr, uid, [('parent_id', '=', False)], limit=1)
        return budgets and budgets[0] or False
    
    def _get_all_sale(self, cr, uid, context=None):
        return self.pool.get('sale.order').search(cr, uid ,[])
    #_order = 'date desc'
    _defaults = {
#        'date_from': lambda *a: time.strftime('%Y-%m-%d'),
#        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
#        'state': lambda *a: 'done',
        'without_zero': lambda *a: True,
#        'groupby': lambda *a: 'none',
        'type': lambda *a: 'xls',
        'fiscalyear_id': _get_fiscalyear,
        'budget_item_id': _get_budget,
        'display_account_level': lambda *a: 0,
    }
    
    def create_budget_detail(self, cr, uid, ids, context=None):
        res = {}
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'budget.detail.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        period_ids = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id','=',datas['form']['fiscalyear_id'])])
        period = self.pool.get('account.period').browse(cr, uid, period_ids)
        i=1
        for p in period:
            res[str(i)] = {
                'id': p.id,
                'name': p.name,
                'date': time.strftime('%b-%y', time.strptime(p.date_start,'%Y-%m-%d')),
                'start': p.date_start,
                'end': p.date_stop,
            }
            i+=1
#        for i in range(13)[::-1]:
#            res[str(i)] = {
#                'name': i
#            }
        datas['form'].update(res)
        if datas['form']['type'] == 'pdf':
            return { 
                'type': 'ir.actions.report.xml',
                'report_name': 'budget.detail.pdf',
                'report_type': 'webkit',
                'datas': datas,
            }
        else:    
            return { 
                'type': 'ir.actions.report.xml',
                'report_name': 'budget.detail.xls',
                'report_type': 'webkit',
                'datas': datas,
            }

budget_detail()
