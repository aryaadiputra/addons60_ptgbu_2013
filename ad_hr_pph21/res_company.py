from osv import osv,fields

class res_company(osv.osv):
    _inherit    = "res.company"
    _columns    = {
                    'com_jamsostek_acc' : fields.many2one('account.account', 'Account', required=True, help="Select account used for Jamsostek."),
                    'com_jamsostek_aacc': fields.many2one('account.analytic.account', 'Analytic Account', required=False, help="Select analytic account used for Jamsostek."),
                    'com_jamsostek_cat' : fields.many2one('hr.allounce.deduction.categoty', 'A/D Category', required=True, help="Select Allowance/Deduction category used for Jamsotek."),
                    'emp_jamsostek_acc' : fields.many2one('account.account', 'Account', required=True, help="Select account used for Jamsostek."),
                    'emp_jamsostek_aacc': fields.many2one('account.analytic.account', 'Analytic Account', required=False, help="Select analytic account used for Jamsostek."),
                    'emp_jamsostek_cat' : fields.many2one('hr.allounce.deduction.categoty', 'A/D Category', required=True, help="Select Allowance/Deduction category used for Jamsotek."),

                    'emp_retiring_acc'  : fields.many2one('account.account', 'Account', required=True, help="Select account used for Pension Contribution."),
                    'emp_retiring_aacc' : fields.many2one('account.analytic.account', 'Analytic Account', required=False, help="Select analytic account used for Pension Contribution."),
                    'emp_retiring_cat'  : fields.many2one('hr.allounce.deduction.categoty', 'A/D Category', required=True, help="Select Allowance/Deduction category used for Pension Contribution."),
                    'com_retiring_acc'  : fields.many2one('account.account', 'Account', required=True, help="Select account used for Pension Contribution paid by company."),
                    'com_retiring_aacc' : fields.many2one('account.analytic.account', 'Analytic Account', required=False, help="Select analytic account used for Pension Contribution paid by company."),
                    'com_retiring_cat'  : fields.many2one('hr.allounce.deduction.categoty', 'A/D Category', required=True, help="Select Allowance/Deduction category used for Pension Contribution paid by company."),
#                    'overtime_acc'  : fields.many2one('account.account', 'Overtime Account', help="Select account used for Overtime."),
#                    'overtime_aacc' : fields.many2one('account.analytic.account', 'Overtime', help="Select analytic account used for Overtime."),
#                    'overtime_cat'  : fields.many2one('hr.allounce.deduction.categoty', 'Overtime A/D Category', help="Select Allowance/Deduction category used for Overtime."),
                    'pph21_acc'     : fields.many2one('account.account', 'Account', required=True, help="Select account used for PPh 21."),
                    'pph21_aacc'    : fields.many2one('account.analytic.account', 'Analytic Account', required=False, help="Select analytic account used for PPh 21."),
                    'pph21_cat'     : fields.many2one('hr.allounce.deduction.categoty', 'A/D Category', required=True, help="Select Allowance/Deduction category used for PPh 21."),
#                    'overtime_acc'  : fields.many2one('account.account', 'Overtime Account', help="Select account used for Overtime."),
#                    'overtime_aacc' : fields.many2one('account.analytic.account', 'Overtime', help="Select analytic account used for Overtime."),
#                    'overtime_cat'  : fields.many2one('hr.allounce.deduction.categoty', 'Overtime A/D Category', help="Select Allowance/Deduction category used for Overtime."),
                    'officecost_acc': fields.many2one('account.account', 'Account', required=True, help="Select account used for Functional Expense."),
                    'officecost_aacc':fields.many2one('account.analytic.account', 'Analytic Account', required=False, help="Select analytic account used for Functional Expense."),
                    'officecost_cat': fields.many2one('hr.allounce.deduction.categoty', 'A/D Category', required=True, help="Select Allowance/Deduction category used for Functional Expense."),
                    
                    'emp_thr_acc': fields.many2one('account.account', 'Account', required=True, help="Select account used for THR."),
                    'emp_thr_aacc':fields.many2one('account.analytic.account', 'Analytic Account', required=False, help="Select analytic account used for THR."),
                    'emp_thr_cat': fields.many2one('hr.allounce.deduction.categoty', 'A/D Category', required=True, help="Select Allowance/Deduction category used for THR."),
                    
                    'emp_bonus_acc': fields.many2one('account.account', 'Account', required=True, help="Select account used for THR."),
                    'emp_bonus_aacc':fields.many2one('account.analytic.account', 'Analytic Account', required=False, help="Select analytic account used for THR."),
                    'emp_bonus_cat': fields.many2one('hr.allounce.deduction.categoty', 'A/D Category', required=True, help="Select Allowance/Deduction category used for THR."),
                   }
res_company()