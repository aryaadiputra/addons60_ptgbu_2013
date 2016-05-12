from osv import fields, osv
from datetime import datetime
import netsvc
import pooler
from osv.orm import browse_record, browse_null
from tools.translate import _

class hr_expense_generate_invoice(osv.osv_memory):
    _name = "hr.expense.generate.invoice"
    _description = "Hr Expense Generate Invoice"

    def merge_department(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context)
        date_inv = datetime.strptime(wizard.date_invoice, '%Y-%m-%d')
        currency_id = self.pool.get('res.currency').search(cr, uid, [])
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id)
        for cur in currency:
            department_id = self.pool.get('hr.department').search(cr, uid, [])
            department = self.pool.get('hr.department').browse(cr, uid, department_id)
            for depart in department:
                cr.execute('SELECT company_id, currency_id, department_id, sum(unit_amount*unit_quantity) as amount FROM hr_expense_expense h join hr_expense_line l on h.id = l.expense_id WHERE type = %s AND state = %s AND department_id = %s AND currency_id = %s GROUP BY department_id,currency_id,company_id',("medical","accepted",depart.id,cur.id))
                expense_data = cr.dictfetchall()
                if expense_data:
                    for i in expense_data:
                        company = self.pool.get('res.company').browse(cr, uid, i['company_id'])
                        val = {
                            'journal_id' : 1,
                            'description' : 'Expense Medical for '+depart.name,
                            'name' : 'Expense Medical',
                            'partner_id' : i['company_id'],
                            'address_invoice_id': 1,
                            'account_id' : company.partner_id.property_account_payable.id,
                            'date_due' : date_inv,
                            'date_invoice': date_inv,
                            'currency_id': i['currency_id'],
                            'type': 'in_invoice',
                             }
                        inv = self.pool.get('account.invoice').create(cr,uid,val,context=context);

                        cr.execute('SELECT currency_id, department_id, product_id, sum(unit_amount*unit_quantity) as amount FROM hr_expense_expense h join hr_expense_line l on h.id = l.expense_id WHERE type = %s AND state = %s AND department_id = %s AND currency_id = %s GROUP BY department_id,product_id,currency_id',("medical","accepted",i['department_id'],cur.id))
                        expense_product = cr.dictfetchall()
                        if expense_product:
                            for j in expense_product:
                                get_product = self.pool.get('product.product').browse(cr, uid, [j['product_id']])
                                account_id = 0
                                analytic_account_id = 0
                                for data_product in get_product:
                                    print "aaaaaaaaaaaaccou",data_product.property_account_expense.id
                                    account_id = data_product.property_account_expense.id
                                    analytic_account_id = self.pool.get('account.analytic.account').search(cr, uid, (['department_id','=',j['department_id']],['budget_expense','=',account_id]))
                                    print "aaaaaaaaaanalytic", analytic_account_id
                                    analytic_account = self.pool.get('account.analytic.account').browse(cr, uid, analytic_account_id)
                                    for a in analytic_account:
                                        analytic_account_id = a.id
                                    val_inv_line = {
                                                    'product_id' : j['product_id'],
                                                    'account_id' : account_id,
                                                    'name' : "Expense for "+depart.name,
                                                    'quantity' : 1,
                                                    'price_unit' : j['amount'],
                                                    'account_analytic_id': analytic_account_id,
                                                    'price_subtotal' : j['amount'],
                                                    'invoice_line_tax_id': False,
                                                    'invoice_id' : inv,
                                                    } 
                                    inv_line = self.pool.get('account.invoice.line').create(cr,uid,val_inv_line,context=context);
                        
                        expense_expense_id = self.pool.get('hr.expense.expense').search(cr, uid, (['type','=','medical'], ['state','=','accepted'], ['department_id','=',depart.id]))
                        expense_expense = self.pool.get('hr.expense.expense').browse(cr, uid, expense_expense_id)
                        wf_service = netsvc.LocalService("workflow")
                        for ex_id in expense_expense:
                            self.pool.get('hr.expense.expense').write(cr, uid, ex_id.id, {'invoice_id': inv})
                            wf_service.trg_validate(uid, 'hr.expense.expense', ex_id.id, 'invoice', cr)

        return {
            'name'      : 'Hr Expense Generate Notification',
            'view_type' : 'form',
            'view_mode' : 'form',
            'res_model' : 'hr.expense.generate.notification',
            'type'      : 'ir.actions.act_window',
            'target'    : 'new',
            'context'   : context
            }

    _columns = {
                'date_invoice' : fields.date('Date Invoice'),
                }

hr_expense_generate_invoice()

class hr_expense_generate_notification(osv.osv_memory):
    _name = "hr.expense.generate.notification"
    _description = "Hr Expense Generate Notification"
    _columns = {
       
                }
hr_expense_generate_notification()

class hr_expense_expense_inherit(osv.osv):

    _inherit = "hr.expense.expense"
    _description = "Expense Inherit"

    def action_invoice_create(self, cr, uid, expense_id):
        self.pool.get('hr.expense.expense').write(cr, uid, expense_id, {'state': 'invoiced'})

    _columns = {

                }
hr_expense_expense_inherit()