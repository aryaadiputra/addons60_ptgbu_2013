from osv import fields,osv

class expenses_structure_line(osv.osv):
    _name = 'expenses.structure.line'
    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        cr.execute("SELECT l.id,COALESCE(SUM(l.unit_amount*l.unit_quantity),0) AS amount FROM expenses_structure_line l WHERE id IN %s GROUP BY l.id ",(tuple(ids),))
        res = dict(cr.fetchall())
        return res
    
    _columns = {
            'date_value':fields.date('Date'),
            'line_id':fields.integer('ID'),
            'name': fields.char('Expense Note', size=128, required=True),
            'expense_id': fields.many2one('hr.expense.expense', 'Expense', ),
            'unit_amount': fields.float('Unit Price'),
            'unit_quantity': fields.float('Quantities' ),
            'product_id': fields.many2one('product.product', 'Product', domain=[('hr_expense_ok','=',True)]),
            'uom_id': fields.many2one('product.uom', 'UoM' ),
            'analytic_account': fields.many2one('account.analytic.account','Analytic account'),
            'ref': fields.char('Reference', size=32),
            'total_amount': fields.function(_amount, method=True, string='Total Amount'),
            'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of expense lines."),
            }
    def onchange_product_id(self, cr, uid, ids, product_id, uom_id, employee_id, context=None):
        res = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            res['name'] = product.name
            amount_unit = product.price_get('standard_price', context=context)[product.id]
            res['unit_amount'] = amount_unit
            if not uom_id:
                res['uom_id'] = product.uom_id.id
        return {'value': res}
expenses_structure_line()

class expenses_structure(osv.osv):
    _name = 'expenses.structure'
    _description = 'Expenses Structure'
    _columns = {
        'name':fields.char('Name', size=256, required=True, readonly=False),
        'code':fields.char('Code', size=64, required=True, readonly=False),
#        'line_ids': fields.one2many('expenses.structure.line', 'line_id', 'Expense Lines',),
        'line_ids': fields.one2many('expenses.structure.line', 'line_id', 'Expense Lines',),
        'company_id':fields.many2one('res.company', 'Company', required=False),
        'note': fields.text('Description'),
    }
expenses_structure()

class hr_expense_expense(osv.osv):
    _inherit = "hr.expense.expense"
    _description = '##'
    def onchange_expense_structure(self, cr, uid, ids, id):
        if id:
            value = []
            data = self.pool.get('expenses.structure').browse(cr, uid, [id])[0]
            print 'data=========',data
            for x in data.line_ids :
                print x
                value.append({
                        'name': x.name,
                        'expense_id': x.expense_id.id, 
                        'unit_amount': x.unit_amount, 
                        'unit_quantity': x.unit_quantity, 
                        'product_id': x.product_id.id,
                        'uom_id': x.uom_id.id, 
                        #'description': x.description, 
                        'analytic_account': x.analytic_account.id,
                        'ref': x.ref,
                        'sequence': x.sequence,
                        })   
            #print "===========",value
            return {'value':{'line_ids':value}}
        return True
    _columns = {
                'expense_structure' : fields.many2one("expenses.structure","Expense Structure"),
                'type': fields.selection([("insurance","Insurance Medical"),("medical","Medical Expenses")], 'Type ', select=True),
                }
hr_expense_expense()

class hr_expense_line_inherit(osv.osv):
    _inherit = "hr.expense.line"
    _description = 'Hr Expense Line Inherit'

    def onchange_product(self, cr, uid, ids, product_id):
        product_id = self.pool.get('product.product').search(cr, uid, (['id','=',product_id]))
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        for pro in product:
            print "aaaaaaaaaaaaccou",pro.property_account_expense.name
            return {'value':{'product_account_id':pro.property_account_expense.id}}
    
    def onchange_product_id(self, cr, uid, ids, product_id, uom_id, employee_id, context=None):
        res = {}
        if product_id:
            department = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            print "department", department.department_id.id
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            res['name'] = product.name
            res['product_account_id'] = product.property_account_expense.id
            analytic_account_id = self.pool.get('account.analytic.account').search(cr, uid, (['department_id','=',department.department_id.id],['budget_expense','=',product.property_account_expense.id]))
            print "aaaaaaaaaanalytic", analytic_account_id
            analytic_account = self.pool.get('account.analytic.account').browse(cr, uid, analytic_account_id)
            for a in analytic_account:
                res['analytic_account'] = a.id
            amount_unit = product.price_get('standard_price', context=context)[product.id]
            res['unit_amount'] = amount_unit
            if not uom_id:
                res['uom_id'] = product.uom_id.id
        return {'value': res}

    _columns = {
                'product_account_id': fields.many2one('account.account','Account'),
                }
hr_expense_line_inherit()
