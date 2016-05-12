from osv import fields,osv

class account_move(osv.osv):
    _inherit = "account.move"
    _columns = {
        'labeled_tax_amount':fields.float("Labeled Tax Amount",digits=(16,4)),
        'with_tax_rate':fields.boolean("With Tax Rate",)
               }
account_move()