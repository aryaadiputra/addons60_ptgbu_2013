from osv import fields,osv

class expenses_structure_line(osv.osv):
    _name = 'expenses.structure.line'
    _columns = {
            'line_id':fields.integer('ID'),
            'name': fields.char('Expense Note', size=128, required=True),
            'expense_id': fields.many2one('hr.expense.expense', 'Expense', ),
            'unit_amount': fields.float('Unit Price'),
            'unit_quantity': fields.float('Quantities' ),
            'product_id': fields.many2one('product.product', 'Product', domain=[('hr_expense_ok','=',True)]),
            'uom_id': fields.many2one('product.uom', 'UoM' ),
            'analytic_account': fields.many2one('account.analytic.account','Analytic account'),
            'ref': fields.char('Reference', size=32),
            'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of expense lines."),
            }
expenses_structure_line()

class expenses_structure(osv.osv):
    _name = 'expenses.structure'
    _description = 'Expenses Structure'
    _columns = {
        'name':fields.char('Name', size=256, required=True, readonly=False),
        'code':fields.char('Code', size=64, required=True, readonly=False),
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
            
            for x in data.line_ids :
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
                "expense_structure" : fields.many2one("expenses.structure","Expense Structure"),
                }
hr_expense_expense()