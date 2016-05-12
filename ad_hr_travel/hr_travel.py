import time
from osv import fields, osv, orm
from tools.translate import _
from osv.orm import browse_record, browse_null
import netsvc

class hr_travel(osv.osv):

    _name = "hr.travel"
    _description = 'hr travel'
    
    def action_merge(self, cr, uid, ids, date_invoice, partner_id, address_invoice_id, context=None):
        print "action_merge>>>>>>>>>>>>>>>>>>>>>>", ids
#         print "context>>>>>>>>>>>>>>>>>>>>>>", context ,"+++++++++++++++++++",context['date_invoice']
#         invoice_date = context['date_invoice']
        
        travel_ids = self.browse(cr, uid, ids)
        a = 0
        for t in travel_ids:
            print "action_merge>>>>>>>>>>>>>>>>>>>>>>travel_ids", t.partner_id.name
            tline_ids = self.pool.get('hr.travel.line').search(cr, uid, [('travel_id','=',t.id)], context=context)
            travel_line_ids = self.pool.get('hr.travel.line').browse(cr, uid, tline_ids, context=context)

            print "journaaaaaaaaaaaaaaaaaaaaaa", t.journal_id.id
            print "idddddddddddddddddddddddddddd", travel_line_ids
            if a == 0: 
                val = {
                        'journal_id' : t.journal_id.id,
                        'description' : 'departure',
                        'name' : 'departure',
                        'partner_id' : partner_id,
                        'address_invoice_id': address_invoice_id,
                        'account_id' : t.account_id.id,
                        'date_due' : t.date_due,
                        'date_invoice': date_invoice,
                        'currency_id': t.currency_id.id,
                        'type': 'in_invoice',
                         }
                
                inv = self.pool.get('account.invoice').create(cr,uid,val,context=context);
                a = 1
                print "inv>>>>>>>>>>>>>>>>>>>>>>>>>>>>..", inv
            
            for tl in travel_line_ids:
                print "idddddddddddddddddddddddddddd", tl
                val_inv_line = {
                                'account_id' : tl.account_id.id,
                                'name' : tl.name,
                                'quantity' : tl.quantity,
                                'price_unit' : tl.price_unit,
                                'account_analytic_id': tl.account_analytic_id.id,
                                'price_subtotal' : tl.price_subtotal,
                                'invoice_line_tax_id': tl.invoice_line_tax_id,
                                'invoice_id' : inv,
                                }

                print 'innnnnnnnnnnnnnnnnnnnnnnnn',val_inv_line   
                inv_line = self.pool.get('account.invoice.line').create(cr,uid,val_inv_line,context=context);
                print "inv line>>>>>>>>>>>>>>>>>>>>>>>>>>>>..", inv_line
            
            val_hr_travel = {
                   'date_invoice': date_invoice,
                   'partner_id' : partner_id,
                   'address_invoice_id': address_invoice_id,
                   'states' : 'invoiced',
                    }
            inv_line = self.write(cr,uid,t.id,val_hr_travel,context=context);
        return True
        
    def onchange_partner(self, cr, uid, ids, partner_id):
        result = {}
        print "paaaaaaaaaaaartner_id", partner_id
        partner = self.pool.get('res.partner.address').search(cr, uid, [('partner_id','=',partner_id)])
        print "paaaaaaaaaaaartner_id1", partner
        data = self.pool.get('res.partner.address').browse(cr, uid, partner)
        print "paaaaaaaaaaaartner_id2", data
        address_invoice_id = ""
        for a in data:
            address_invoice_id = a.id

        result['value'] = {
            'address_invoice_id': address_invoice_id,
        }
        return result


    
    def onchange_employee(self,cr,uid,ids,emp):
        val={}
        if emp:
            employee_pool   = self.pool.get('hr.employee')
            val = {}
            emp             = employee_pool.browse(cr,uid,emp)
            val             = {
                               'department_id'  : emp.department_id.id,
                               'section_id'     : emp.section.id
                               }
        return {'value':val}

    _columns = {
        'name': fields.char('Description', size=64, select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'origin': fields.char('Source Document', size=64, help="Reference of the document that produced this invoice.", readonly=True, states={'draft':[('readonly',False)]}),
        'number': fields.related('move_id','name', type='char', readonly=True, size=64, relation='account.move', store=True, string='Number'),
        'internal_number': fields.char('Invoice Number', size=32, readonly=True, help="Unique number of the invoice, computed automatically when the invoice is created."),
        'reference': fields.char('Invoice Reference', size=64, help="The partner reference of this invoice."),
        'comment': fields.text('Additional Information'),
        'date_invoice': fields.date('Invoice Date', states={'paid':[('readonly',True)], 'open':[('readonly',True)], 'close':[('readonly',True)]}, select=True, help="Keep empty to use the current date"),
        'date_due': fields.date('Due Date', states={'paid':[('readonly',True)], 'open':[('readonly',True)], 'close':[('readonly',True)]}, select=True,
            help="If you use payment terms, the due date will be computed automatically at the generation "\
                "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. The payment term may compute several due dates, for example 50% now, 50% in one month."),
        'partner_id': fields.many2one('res.partner', 'Travel Agent', change_default=True, readonly=True, required=False, states={'draft':[('readonly',False)]}),
        'address_contact_id': fields.many2one('res.partner.address', 'Contact Address', readonly=True, states={'draft':[('readonly',False)]}),
        'address_invoice_id': fields.many2one('res.partner.address', 'Travel Address', readonly=True, required=False, states={'draft':[('readonly',False)]}),
        'period_id': fields.many2one('account.period', 'Force Period', help="Keep empty to use the period of the validation(invoice) date.", readonly=True, states={'draft':[('readonly',False)]}),

        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The partner account used for this invoice."),
        'travel_line': fields.one2many('hr.travel.line', 'travel_id', 'Travel Line', readonly=True, states={'draft':[('readonly',False)]}),
        'tax_line': fields.one2many('account.invoice.tax', 'invoice_id', 'Tax Lines', readonly=True, states={'draft':[('readonly',False)]}),

        'move_id': fields.many2one('account.move', 'Journal Entry', readonly=True, select=1, ondelete='restrict', help="Link to the automatically generated Journal Items."),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        # 'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=True, states={'draft':[('readonly',False)]}),
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account',
            help='Bank Account Number, Company bank account if Invoice is customer or supplier refund, otherwise Partner bank account number.', readonly=True, states={'draft':[('readonly',False)]}),
        'move_name': fields.char('Journal Entry', size=64, readonly=True, states={'draft':[('readonly',False)]}),
        'user_id': fields.many2one('res.users', 'Salesman', readonly=True, states={'draft':[('readonly',False)]}),
        'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position', readonly=True, states={'draft':[('readonly',False)]}),
        'reserve_date': fields.date('Reserve Date'),
        'request_date': fields.date('Request Date'),
        'description': fields.text('Description'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'states' : fields.selection([("draft","draft"),("invoiced","invoiced")], 'States', readonly=True, required=False, select=True),
    }
    
    _defaults = {
        'states': 'draft',
    }
    
hr_travel()