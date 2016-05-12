from osv import osv, fields
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
import tools
from tools.translate import _
import decimal_precision as dp
import netsvc

def prev_bounds(cdate=False):
    when = date.fromtimestamp(time.mktime(time.strptime(cdate,"%Y-%m-%d")))
    this_first = date(when.year, when.month, 1)
    month = when.month + 1
    year = when.year
    if month > 12:
        month = 1
        year += 1
    next_month = date(year, month, 1)
    prev_end = next_month - timedelta(days=1)
    return this_first, prev_end

class account_period(osv.osv):
    _inherit = "account.period"
    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        res = []
        period   = self.browse(cr,uid,ids[0])
        nmy = datetime.fromtimestamp(time.mktime(time.strptime(period.date_start,"%Y-%m-%d")))
        str = tools.ustr(nmy.strftime('%B %Y'))
        res.append((period.id, str or "Bad period"))
        return res
account_period()

class hr_contract(osv.osv):
    _inherit = "hr.contract"
    _columns = {
                'marital'       : fields.many2one('hr.employee.marital.status', 'Marital Status'),
                'amenability'   : fields.float('Amenability'),
                'familiy_doc'   : fields.binary('Family Document'),
                'has_npwp'      : fields.boolean('Has NPWP?'),
                'npwp_no'       : fields.char('NPWP', size=32),
                'ptkp'          : fields.selection([('tk0','TK/-'),
                                                    ('tk1','TK/1'),
                                                    ('tk2','TK/2'),
                                                    ('tk3','TK/3'),
                                                    ('k0' ,'K/-'),
                                                    ('k1' ,'K/1'),
                                                    ('k2' ,'K/2'),
                                                    ('k3' ,'K/3'),
                                                    ('ki0','K/I/-'),
                                                    ('ki1','K/I/1'),
                                                    ('ki2','K/I/2'),
                                                    ('ki3','K/I/3'),
                                                    ], 'PTKP', required=True),
                'ptkp_amount'   : fields.float('NW Amount (monthly)', help="Nontaxable Wages Amount (monthly)"),
                }
    
    def onchange_employeeid(self,cr,uid,ids,data,context=None):
        dict={}
        if data:
            employee = self.pool.get('hr.employee').browse(cr,uid,data)
            if employee.current_job_level:
                if employee.current_job_level.sal_struc:
                    dict['struct_id']= employee.current_job_level.sal_struc.id
            if employee.npwp:
                dict['has_npwp']    = True
                dict['npwp_no']     = employee.npwp
            else:
                dict['has_npwp']    = False
                dict['npwp_no']     = ""
            print dict
        return {'value':dict} 
    def onchange_ptkp(self,cr,uid,ids,data):
        dict={}
        if data:
            ptkp_conf=self.pool.get('ptkp.conf').search(cr,uid,[('name','=',data)])
            if len(ptkp_conf)==0:
                raise osv.except_osv(_('PTKP Not Defined!'), _('This PTKP not defined yet. Please go to menu:\nHuman Resources - Configuration - PTKP - PTKP'))
            else:
                ptkp_data=self.pool.get('ptkp.conf').browse(cr,uid,ptkp_conf)[0]
            self.amenability=int(data[-1:])
            dict['amenability'] = self.amenability
            dict['ptkp_amount'] = ptkp_data.ptkp_amount
            self.ptkp_amount=dict['ptkp_amount']
        else:
            self.amenability=0
            self.ptkp_amount=0
        return {'value':dict}
hr_contract()

class payment_category(osv.osv):
    _inherit = "hr.allounce.deduction.categoty"
    _columns = {
               'type':fields.selection([('allowance','Allowance'),
                                        ('deduction','Deduction'),
                                        ('leaves','Leaves'),
                                        ('advance','Advance'),
                                        ('loan','Loan'),
                                        ('installment','Loan Installment'),
                                        ('otherpay','Other Payment'),
                                        ('otherdeduct','Other Deduction'),
                                        ('pension','Pension')],'Type', select=True, required=True),
               }
payment_category()

class hr_payslip_line(osv.osv):
    _inherit = "hr.payslip.line"
    _columns = {
               'type':fields.selection([('allowance','Allowance'),
                                        ('deduction','Deduction'),
                                        ('leaves','Leaves'),
                                        ('advance','Advance'),
                                        ('loan','Loan'),
                                        ('installment','Loan Installment'),
                                        ('otherpay','Other Payment'),
                                        ('otherdeduct','Other Deduction'),
                                        ('pension','Pension')],'Type', select=True, required=True),
               }
hr_payslip_line()

class hr_payslip(osv.osv):
    _inherit = "hr.payslip"

    def verify_sheet(self, cr, uid, ids, context=None):
        move_pool       = self.pool.get('account.move')
        movel_pool      = self.pool.get('account.move.line')
        exp_pool        = self.pool.get('hr.expense.expense')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        period_pool     = self.pool.get('account.period')
        property_pool   = self.pool.get('ir.property')
        payslip_pool    = self.pool.get('hr.payslip.line')
        jamsostek_pool  = self.pool.get('hr.jamsostek')
        company_obj     = self.pool.get('res.users').browse(cr,uid,uid).company_id

        for slip in self.browse(cr, uid, ids, context=context):
            if not slip.journal_id:
                # Call super method to verify sheet if journal_id is not specified.
                super(hr_payslip, self).verify_sheet(cr, uid, [slip.id], context=context)
                continue
            total_deduct = 0.0

            line_ids = []
            partner = False
            partner_id = False

            if not slip.employee_id.bank_account_id:
                raise osv.except_osv(_('Configuration Error !'), _('Please define bank account for %s !') % (slip.employee_id.name))

            if not slip.employee_id.bank_account_id.partner_id:
                raise osv.except_osv(_('Configuration Error !'), _('Please define partner in bank account for %s !') % (slip.employee_id.name))

            partner = slip.employee_id.bank_account_id.partner_id
            partner_id = slip.employee_id.bank_account_id.partner_id.id

            period_id = False

            if slip.period_id:
                period_id = slip.period_id.id
            else:
                fiscal_year_ids = fiscalyear_pool.search(cr, uid, [], context=context)
                if not fiscal_year_ids:
                    raise osv.except_osv(_('Warning !'), _('Please define fiscal year for perticular contract'))
                fiscal_year_objs = fiscalyear_pool.read(cr, uid, fiscal_year_ids, ['date_start','date_stop'], context=context)
                year_exist = False
                for fiscal_year in fiscal_year_objs:
                    if ((fiscal_year['date_start'] <= slip.date) and (fiscal_year['date_stop'] >= slip.date)):
                        year_exist = True
                if not year_exist:
                    raise osv.except_osv(_('Warning !'), _('Fiscal Year is not defined for slip date %s') % slip.date)
                search_periods = period_pool.search(cr,uid,[('date_start','<=',slip.date),('date_stop','>=',slip.date)])
                print search_periods, slip.date, type(slip.date)
                if not search_periods:
                    raise osv.except_osv(_('Warning !'), _('Period is not defined for slip date %s') % slip.date)
                period_id = search_periods[0]

            move = {
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
                'date': slip.date,
                'ref':slip.number,
                'narration': slip.name
            }
            move_id = move_pool.create(cr, uid, move, context=context)
            self.create_voucher(cr, uid, [slip.id], slip.name, move_id)
            
            if not slip.employee_id.salary_account.id:
                raise osv.except_osv(_('Warning !'), _('Please define Salary Account for %s.') % slip.employee_id.name)
            
            #===================================================================
            # Line untuk Gaji Pokok
            #===================================================================
            
            line = {
                'move_id':move_id,
                'name': "Basic Salary Expenses " + slip.employee_id.name,
                'date': slip.date,
                'account_id': slip.employee_id.salary_account.id,
                'debit': slip.basic,
                'credit': 0.0,
                'quantity':slip.working_days,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
                'analytic_account_id': False,
                'ref':slip.number
            }
            #Setting Analysis Account for Basic Salary
            if slip.employee_id.analytic_account:
                line['analytic_account_id'] = slip.employee_id.analytic_account.id

            move_line_id = movel_pool.create(cr, uid, line, context=context)
            line_ids += [move_line_id]

            if not slip.employee_id.employee_account.id:
                raise osv.except_osv(_('Warning !'), _('Please define Employee Payable Account for %s.') % slip.employee_id.name)
            
            line = {
                'move_id':move_id,
                'name': "Basic Payable Salary  " + slip.employee_id.name,
                'partner_id': partner_id,
                'date': slip.date,
                'account_id': slip.employee_id.employee_account.id,
                'debit': 0.0,
                'quantity':slip.working_days,
                'credit': slip.basic,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
                'ref':slip.number
            }
            
            line_ids += [movel_pool.create(cr, uid, line, context=context)]
            #===================================================================
            # Line untuk Gaji Pokok
            #===================================================================

            #===================================================================
            # Line untuk Jamsostek oleh Perusahaan
            #===================================================================
            if slip.jsostek_comp>0:
                line = {
                    'move_id':move_id,
                    'name': "Jamsostek Expenses oleh Perusahaan untuk " + slip.employee_id.name,
                    'date': slip.date,
                    'account_id': company_obj.com_jamsostek_acc.id,
                    'debit': slip.jsostek_comp,
                    'credit': 0.0,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'analytic_account_id': False,
                    'ref':slip.number
                }
                #Setting Analysis Account for Basic Salary
            #   if slip.employee_id.analytic_account:
            #       line['analytic_account_id'] = slip.employee_id.analytic_account.id
    
                move_line_id = movel_pool.create(cr, uid, line, context=context)
                line_ids += [move_line_id]
            
            jamsostek_id=self.pool.get('hr.jamsostek').search(cr,uid,[('name','=',slip.employee_id.id)])
            jamsostek=self.pool.get('hr.jamsostek').browse(cr,uid,jamsostek_id)[0]
            if not slip.employee_id.employee_account:
                raise osv.except_osv(_('Warning !'), _('Please define Employee Payable Account for %s.') % slip.employee_id.name)
            if not jamsostek.branch_office:
                raise osv.except_osv(_('Warning !'), _('Please define Partner for Jamsostek.'))
            if jamsostek_id:
                line = {
                    'move_id':move_id,
                    'name': "Jamsostek Payable oleh Perusahaan untuk " + slip.employee_id.name,
                    'partner_id': jamsostek.branch_office.id,
                    'date': slip.date,
                    'account_id': jamsostek.branch_office.property_account_payable.id,
                    'debit': 0.0,
                    'credit': slip.jsostek_comp,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'ref':slip.number
                }
                
                move_id3=movel_pool.create(cr, uid, line, context=context)
                line_ids += [move_id3]
            #===================================================================
            # Line untuk Jamsostek oleh Perusahaan
            #===================================================================
            
            #===================================================================
            # Line untuk Iuran Pensiun oleh Perusahaan
            #===================================================================
            line = {
                'move_id':move_id,
                'name': "Iuran Pensiun oleh Perusahaan untuk " + slip.employee_id.name,
                'date': slip.date,
                'account_id': company_obj.com_retiring_acc.id,
                'debit': slip.basic*0.06,
                'credit': 0.0,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
                'analytic_account_id': False,
                'ref':slip.number
            }
            #Setting Analysis Account for Basic Salary
            if slip.employee_id.analytic_account:
                line['analytic_account_id'] = slip.employee_id.analytic_account.id

            move_line_id = movel_pool.create(cr, uid, line, context=context)
            line_ids += [move_line_id]

            if not slip.employee_id.employee_account.id:
                raise osv.except_osv(_('Warning !'), _('Please define Employee Payable Account for %s.') % slip.employee_id.name)
            
            line = {
                'move_id':move_id,
                'name': "Iuran Pensiun oleh Perusahaan untuk " + slip.employee_id.name,
                'partner_id': partner_id,
                'date': slip.date,
                'account_id': company_obj.emp_retiring_acc.id,
                'debit': 0.0,
                'credit': slip.basic*0.06,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
                'ref':slip.number
            }
            
            line_ids += [movel_pool.create(cr, uid, line, context=context)]
            #===================================================================
            #  Line untuk Iuran Cuti oleh Perusahaan
            #===================================================================

            for line in slip.line_ids2:
                name = "[%s] - %s / %s" % (line.code, line.name, slip.employee_id.name)
                amount = line.total

                if line.type == 'leaves':
                    continue

                rec = {
                    'move_id': move_id,
                    'name': name,
                    'date': slip.date,
                    'account_id': line.account_id.id,
                    'debit': 0.0,
                    'credit': 0.0,
                    'journal_id': slip.journal_id.id,
                    'period_id': period_id,
                    'analytic_account_id': False,
                    'ref': slip.number,
                    'quantity': 1
                }

                #Setting Analysis Account for Salary Slip Lines
                if line.analytic_account_id:
                    rec['analytic_account_id'] = line.analytic_account_id.id
                else:
                    if not slip.deg_id:
                        raise osv.except_osv(_('Configuration Error !'), _("Payslip cannot be approved due to one of the following reasons: \n 1. The Structure line %s has not been linked with an analytic account. \n Or \n 2. Payslip for %s is missing the configuration of Designation from 'Accounting Details'") % (line.name, slip.employee_id.name))
                    else:
                        rec['analytic_account_id'] = slip.deg_id.account_id.id

                if line.type == 'allowance' or line.type == 'otherpay':
                    #===========================================================
                    # Line untuk Allowance
                    #===========================================================
                    
                    rec['debit'] = amount
                    if not partner.property_account_payable:
                        raise osv.except_osv(_('Configuration Error !'), _('Please Configure Partners Payable Account!!'))
                    ded_rec = {
                        'move_id': move_id,
                        'name': name,
                        'partner_id': partner_id,
                        'date': slip.date,
                        'account_id': slip.employee_id.employee_account.id,
                        'debit': 0.0,
                        'quantity': 1,
                        'credit': amount,
                        'journal_id': slip.journal_id.id,
                        'period_id': period_id,
                        'ref': slip.number
                    }
                    line_ids += [movel_pool.create(cr, uid, ded_rec, context=context)]
                elif line.type == 'deduction' or line.type == 'otherdeduct':
                    
                    #===========================================================
                    # Line untuk Deduction
                    #===========================================================
                    
                    if not partner.property_account_receivable:
                        raise osv.except_osv(_('Configuration Error !'), _('Please Configure Partners Receivable Account!!'))
                    rec['credit'] = amount
                    total_deduct += amount
                    ded_rec = {
                        'move_id': move_id,
                        'name': name,
                        'partner_id': partner_id,
                        'date': slip.date,
                        'quantity': 1,
                        'account_id':slip.employee_id.employee_account.id,
                        'debit': amount,
                        'credit': 0.0,
                        'journal_id': slip.journal_id.id,
                        'period_id': period_id,
                        'ref': slip.number
                    }
                    line_ids += [movel_pool.create(cr, uid, ded_rec, context=context)]
                elif line.type == 'pension':
                    #===========================================================
                    # Line untuk Pension
                    #===========================================================
                    if not slip.employee_id.pension_acc:
                        raise osv.except_osv(_('Configuration Error !'), _('Please Configure Pension Receivable Account!!'))
                    rec['credit'] = amount
                    ded_rec = {
                        'move_id': move_id,
                        'name': name,
                        'partner_id': partner_id,
                        'date': slip.date,
                        'account_id': slip.employee_id.pension_acc.id,
                        'debit': amount,
                        'quantity': 1,
                        'credit': 0.0,
                        'journal_id': slip.journal_id.id,
                        'period_id': period_id,
                        'ref': slip.number
                    }
                    line_ids += [movel_pool.create(cr, uid, ded_rec, context=context)]
                    

                line_ids += [movel_pool.create(cr, uid, rec, context=context)]


            #===================================================================
            # Scripting for PPh 21 - START
            #===================================================================
            rec = {
                'move_id': move_id,
                'name': "[%s] - %s / %s" % (company_obj.pph21_cat.code, company_obj.pph21_cat.name, slip.employee_id.name),
                'date': slip.date,
                'account_id': company_obj.pph21_acc.id,
                'debit': 0.0,
                'credit': 0.0,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
                'analytic_account_id': False,
                'ref': slip.number,
                'quantity': 1
            }
            
            if not company_obj.pph21_cat:
                raise osv.except_osv(_('Warning !'), _('Please define Category of Salary Head for PPh 21'))
            rec['credit'] = slip.pph21
            total_deduct += slip.pph21
            pph21_rec = {
                'move_id':move_id,
                'name': "[%s] - %s / %s" % (company_obj.pph21_cat.code, company_obj.pph21_cat.name, slip.employee_id.name),
                'partner_id': partner_id,
                'date': slip.date,
                'account_id': slip.employee_id.employee_account.id,
                'debit': slip.pph21,
                'quantity':slip.working_days,
                'credit': 0.0,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
                'ref':slip.number
            }
            
            line_ids += [movel_pool.create(cr, uid, pph21_rec, context=context)]
            line_ids += [movel_pool.create(cr, uid, rec, context=context)]
            #===================================================================
            #-------------------------------------- # Scripting for PPh 21 - END
            #===================================================================
            
            #===================================================================
            # Scripting for Overtime - START >>> dipindah ke modul sendiri
            #===================================================================
#            rec = {
#                'move_id': move_id,
#                'name': "[%s] - %s / %s" % (slip.overtime_cat.code, slip.overtime_cat.name, slip.employee_id.name),
#                'date': slip.date,
#                'account_id': partner.property_account_payable.id,
#                'debit': 0.0,
#                'credit': 0.0,
#                'journal_id': slip.journal_id.id,
#                'period_id': period_id,
#                'analytic_account_id': False,
#                'ref': slip.number,
#                'quantity': 1
#            }
#            
#            if not slip.overtime_cat:
#                raise osv.except_osv(_('Warning !'), _('Please define Category of Salary Head for Overtime'))
#            rec['debit'] = slip.overtime_fee
#            otime_rec = {
#                'move_id': move_id,
#                'name': "[%s] - %s / %s" % (slip.overtime_cat.code, slip.overtime_cat.name, slip.employee_id.name),
#                'partner_id': partner_id,
#                'date': slip.date,
#                'account_id': slip.overtime_acc.id,
#                'debit': 0.0,
#                'quantity': 1,
#                'credit': slip.overtime_fee,
#                'journal_id': slip.journal_id.id,
#                'period_id': period_id,
#                'ref': slip.number
#            }
#            
#            line_ids += [movel_pool.create(cr, uid, otime_rec, context=context)]
#            line_ids += [movel_pool.create(cr, uid, rec, context=context)]
            #===================================================================
            #------------------------------------ # Scripting for Overtime - END
            #===================================================================
                
            adj_move_id = False
            
            #==================================================================#
            # -----------------Adjustment Entry REMOVED------------------------#
            #==================================================================#
            
            rec = {
                'state':'confirm',
                'move_line_ids':[(6, 0,line_ids)],
            }
            if not slip.period_id:
                rec['period_id'] = period_id

            dates = prev_bounds(slip.date)
            exp_ids = exp_pool.search(cr, uid, [('date_valid','>=',dates[0]), ('date_valid','<=',dates[1]), ('state','=','invoiced')], context=context)
            if exp_ids:
                acc = property_pool.get(cr, uid, 'property_account_expense_categ', 'product.category')
                for exp in exp_pool.browse(cr, uid, exp_ids, context=context):
                    exp_res = {
                        'name':exp.name,
                        'amount_type':'fix',
                        'type':'otherpay',
                        'category_id':exp.category_id.id,
                        'amount':exp.amount,
                        'slip_id':slip.id,
                        'expanse_id':exp.id,
                        'account_id':acc
                    }
                    payslip_pool.create(cr, uid, exp_res, context=context)

            self.write(cr, uid, [slip.id], rec, context=context)

        return True
    
    def process_sheet(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('account.move')
        movel_pool = self.pool.get('account.move.line')
        invoice_pool = self.pool.get('account.invoice')
        fiscalyear_pool = self.pool.get('account.fiscalyear')
        period_pool = self.pool.get('account.period')

        for slip in self.browse(cr, uid, ids, context=context):
            if not slip.bank_journal_id or not slip.journal_id:
                # Call super method to process sheet if journal_id or bank_journal_id are not specified.
                super(hr_payslip, self).process_sheet(cr, uid, [slip.id], context=context)
                continue
            line_ids = []
            partner = False
            partner_id = False
            exp_ids = []

            partner = slip.employee_id.bank_account_id.partner_id
            partner_id = partner.id

            fiscal_year_ids = fiscalyear_pool.search(cr, uid, [], context=context)
            if not fiscal_year_ids:
                raise osv.except_osv(_('Warning !'), _('Please define fiscal year for perticular contract'))
            fiscal_year_objs = fiscalyear_pool.read(cr, uid, fiscal_year_ids, ['date_start','date_stop'], context=context)
            year_exist = False
            for fiscal_year in fiscal_year_objs:
                if ((fiscal_year['date_start'] <= slip.date) and (fiscal_year['date_stop'] >= slip.date)):
                    year_exist = True
            if not year_exist:
                raise osv.except_osv(_('Warning !'), _('Fiscal Year is not defined for slip date %s') % slip.date)
            struct_time = time.strptime(slip.date, "%Y-%m-%d")
            slipdate = time.strftime("%Y-%m-%d",struct_time)
            search_periods=[]
            #search_periods = period_pool.search(cr, uid, [('date_start','<=',"slipdate"),('date_stop','>=',slipdate)], context=context)
            #print "select id from account_period where date_start <= '%s' and date_stop >= '%s'" %(slip.date,slip.date)
            cr.execute("select id from account_period where date_start <= '%s' and date_stop >= '%s'" %(slip.date,slip.date))
            for id in cr.fetchall()[0]:
                search_periods.append(id)
            #print searchres
            #print search_periods, slip.date, type(slip.date),slipdate,type(slipdate)
            if not search_periods:
                raise osv.except_osv(_('Warning !'), _('Period is not defined for slip date %s') % slip.date)
            period_id = search_periods[0]
            name = 'Payment of Salary to %s' % (slip.employee_id.name)
            move = {
                'journal_id': slip.bank_journal_id.id,
                'period_id': period_id,
                'date': slip.date,
                'type':'bank_pay_voucher',
                'ref':slip.number,
                'narration': name
            }
            move_id = move_pool.create(cr, uid, move, context=context)
            self.create_voucher(cr, uid, [slip.id], name, move_id)

            name = "To %s account" % (slip.employee_id.name)
            
            if not slip.employee_id.property_bank_account.id:
                raise osv.except_osv(_('Warning !'), _('Employee Bank Account is not defined for %s') % slip.employee_id.name)
            
            ded_rec = {
                'move_id': move_id,
                'name': name,
                'date': slip.date,
                'account_id': slip.employee_id.property_bank_account.id,
                'debit': 0.0,
                'credit': slip.total_pay,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
                'ref': slip.number
            }
            line_ids += [movel_pool.create(cr, uid, ded_rec, context=context)]
            name = "By %s account" % (slip.employee_id.property_bank_account.name)
            cre_rec = {
                'move_id': move_id,
                'name': name,
                'partner_id': partner_id,
                'date': slip.date,
                'account_id': slip.employee_id.employee_account.id,
                'debit': slip.total_pay,
                'credit': 0.0,
                'journal_id': slip.journal_id.id,
                'period_id': period_id,
                'ref': slip.number
            }
            line_ids += [movel_pool.create(cr, uid, cre_rec, context=context)]

            other_pay = slip.other_pay
            #Process all Reambuse Entries
            for line in slip.line_ids2:
                if line.type == 'otherpay' and line.expanse_id.invoice_id:
                    if not line.expanse_id.invoice_id.move_id:
                        raise osv.except_osv(_('Warning !'), _('Please Confirm all Expense Invoice appear for Reimbursement'))
                    invids = [line.expanse_id.invoice_id.id]
                    amount = line.total
                    acc_id = slip.bank_journal_id.default_credit_account_id and slip.bank_journal_id.default_credit_account_id.id
                    period_id = slip.period_id.id
                    journal_id = slip.bank_journal_id.id
                    name = '[%s]-%s' % (slip.number, line.name)
                    invoice_pool.pay_and_reconcile(cr, uid, invids, amount, acc_id, period_id, journal_id, False, period_id, False, context, name)
                    other_pay -= amount
                    #TODO: link this account entries to the Payment Lines also Expense Entries to Account Lines
                    l_ids = movel_pool.search(cr, uid, [('name','=',name)], context=context)
                    line_ids += l_ids

                    l_ids = movel_pool.search(cr, uid, [('invoice','=',line.expanse_id.invoice_id.id)], context=context)
                    exp_ids += l_ids

            #Process for Other payment if any
            other_move_id = False
            if slip.other_pay > 0:
                narration = 'Payment of Other Payeble amounts to %s' % (slip.employee_id.name)
                move = {
                    'journal_id': slip.bank_journal_id.id,
                    'period_id': period_id,
                    'date': slip.date,
                    'type':'bank_pay_voucher',
                    'ref':slip.number,
                    'narration': narration
                }
                other_move_id = move_pool.create(cr, uid, move, context=context)
                self.create_voucher(cr, uid, [slip.id], narration, move_id)

                name = "To %s account" % (slip.employee_id.name)
                ded_rec = {
                    'move_id':other_move_id,
                    'name':name,
                    'date':slip.date,
                    'account_id':slip.employee_id.property_bank_account.id,
                    'debit': 0.0,
                    'credit': other_pay,
                    'journal_id':slip.journal_id.id,
                    'period_id':period_id,
                    'ref':slip.number
                }
                line_ids += [movel_pool.create(cr, uid, ded_rec, context=context)]
                name = "By %s account" % (slip.employee_id.property_bank_account.name)
                cre_rec = {
                    'move_id':other_move_id,
                    'name':name,
                    'partner_id':partner_id,
                    'date':slip.date,
                    'account_id':partner.property_account_payable.id,
                    'debit': other_pay,
                    'credit':0.0,
                    'journal_id':slip.journal_id.id,
                    'period_id':period_id,
                    'ref':slip.number
                }
                line_ids += [movel_pool.create(cr, uid, cre_rec, context=context)]

            rec = {
                'state':'done',
                'move_payment_ids':[(6, 0, line_ids)],
                'paid':True
            }
            self.write(cr, uid, [slip.id], rec, context=context)
            for exp_id in exp_ids:
                self.write(cr, uid, [slip.id], {'move_line_ids':[(4, exp_id)]}, context=context)

        return True
    
    def _calculate(self, cr, uid, ids, field_names, arg, context=None):
        payslip=self.browse(cr,uid,ids[0])
        jamsostek_pool  = self.pool.get('hr.jamsostek')
        period_pool     = self.pool.get('account.period')
        company_obj = self.pool.get('res.users').browse(cr,uid,uid).company_id
        
        #=======================================================================
        # Month and year
        #=======================================================================
        today = time.strftime('%Y-%m-%d')
        now_date = datetime.fromtimestamp(time.mktime(time.strptime(today,"%Y-%m-%d")))
        nmy = tools.ustr(now_date.strftime('%B-%Y'))
        yy = tools.ustr(now_date.strftime('%Y'))
        #=======================================================================
        # Overtime calculation
        #=======================================================================
#        submission = self.pool.get('hr.overtime').search(cr,uid,[('name','=',payslip.employee_id.id),('state','=','done')])
#        tduration=0.0
#        for sb_id in submission:
#            sb=self.pool.get('hr.overtime').browse(cr,uid,sb_id)
#            overtime_date = sb.time_start
#            overtime_date = datetime.fromtimestamp(time.mktime(time.strptime(overtime_date,"%Y-%m-%d %H:%M:%S")))
#            omy=tools.ustr(overtime_date.strftime('%B-%Y'))
#            if nmy==omy:
#                tduration=tduration+sb.paid
                
        if payslip.contract_id.ptkp_amount==None:
            payslip.contract_id.ptkp_amount=0.0
            
        slip_line_obj = self.pool.get('hr.payslip.line')
        register_pool = self.pool.get('company.contribution')
        res = {}
        
        for rs in self.browse(cr, uid, ids, context=context):
            #print '===========',rs,"xxx",rs.line_ids
            allow = 0.0
            deduct = 0.0
            others = 0.0

            #===================================================================
            # Gaji Pokok + Allowance - Deduction
            #===================================================================
            obj = {'basic':rs.basic}
            if rs.igross > 0:
                obj['gross'] = rs.igross
            if rs.inet > 0:
                obj['net'] = rs.inet
            for line in rs.line_ids:
                amount = 0.0
                if line.amount_type == 'per':
                    try:
                        amount = line.amount * eval(str(line.category_id.base), obj)
                    except Exception, e:
                        raise osv.except_osv(_('Variable Error !'), _('Variable Error: %s ') % (e))
                elif line.amount_type in ('fix', 'func'):
                    amount = line.amount
                cd = line.category_id.code.lower()
                obj[cd] = amount
                contrib = 0.0
                if line.type == 'allowance':
                    allow += amount
                    others += contrib
                    amount -= contrib
                elif line.type == 'deduction':
                    deduct += amount
                    others -= contrib
                    amount += contrib
                elif line.type == 'advance':
                    others += amount
                elif line.type == 'loan':
                    others += amount
                elif line.type == 'otherpay':
                    others += amount
                elif line.type == 'pension':
                    others += amount

                company_contrib = 0.0
                for contrib_line in line.category_id.contribute_ids:
                    company_contrib += register_pool.compute(cr, uid, contrib_line.id, amount, context)

                slip_line_obj.write(cr, uid, [line.id], {'total':amount, 'company_contrib':company_contrib}, context=context)

            #===================================================================
            # Jamsostek Deduction
            #===================================================================
            jamsostek_emp=0
            jamsostek_comp=0
            jamsostek_amount=0
            today=time.strftime('%Y-%m-%d')
            print "rs.employee_id.id",rs.employee_id.id
            periods = period_pool.search(cr, uid, [('date_start','<=',rs.date),('date_stop','>=',rs.date)])
            jamsostek_ids   = jamsostek_pool.search(cr,uid,[('name','=',rs.employee_id.id),('period_id','=',periods and periods[0])])
            if jamsostek_ids:
                jamsostek = jamsostek_pool.browse(cr,uid,jamsostek_ids[0])
                jamsostek_amount    = jamsostek.total
                jamsostek_emp       = jamsostek.jht_by_employee
                jamsostek_comp      = jamsostek.total-jamsostek.jht_by_employee
#            deduct              += jamsostek_amount
#            others              -= contrib
#            jamsostek_amount    += contrib
            #===================================================================
            # Pension Allowance
            #===================================================================
            com_pension_cont    = rs.basic*0.06
#            allow               += com_pension_cont
#            others              += contrib
#            com_pension_cont    -= contrib
    
            #===================================================================
            # Pension Deduction
            #===================================================================
            self_pension_cont   = rs.basic*0.02
#            deduct              += self_pension_cont
#            others              -= contrib
#            self_pension_cont   += contrib
            
            
            offfice_cost    = (rs.basic + allow)*0.05
            if offfice_cost>500000:
                offfice_cost=500000
            elif offfice_cost<0:
                offfice_cost=0

# total deduction
            deduct = offfice_cost + self_pension_cont + jamsostek_emp

#            paid_tduration = int(tduration * (rs.basic + allow) / 173)

#            before_pph_y  = (rs.basic + allow - deduct + paid_tduration)*12
            penambah = allow+others
            
            #===================================================================
            # Tentang rs.thr_amount: THR tidak dikali 12 karena hanya diterima sekali setahun
            #===================================================================
            
            before_pph_y  = (rs.basic + penambah - deduct - rs.thr_amount)*12 + rs.thr_amount 
            ptkp_y = payslip.contract_id.ptkp_amount*12
            pkp_y = before_pph_y - ptkp_y
            
            if pkp_y<0:
                pkp_y=0
            
            if pkp_y <= 50000000:
                pph = (pkp_y * 0.05)/12
                pph_percent=5.0
            elif pkp_y <= 250000000:
                pph = (((pkp_y-50000000) * 0.15) + 2500000)/12
                pph_percent=15.0
            elif pkp_y <= 500000000:
                pph = (((pkp_y-250000000) * 0.25) + 32500000)/12
                pph_percent=25.0
            elif pkp_y > 500000000:
                pph = (((pkp_y-500000000) * 0.3) + 95000000)/12
                pph_percent=30.0
                
            
            
            record = {
                'allounce'      : penambah,
                'deduction'     : deduct,
                'grows'         : rs.basic + penambah,
                'net'           : rs.basic + penambah - deduct,
                'other_pay'     : others,
                'total_pay'     : rs.basic + allow - deduct - pph + offfice_cost,

                'ptkp_amount'   : ptkp_y/12,
                'pkp'           : pkp_y/12,
                'pph_percent'   : pph_percent,
                'pph21'         : pph,
#                'overtime_fee'  : paid_tduration,
#                'wageperhour'   : (rs.basic + allow)/173,
                'final_gross'   : rs.basic + allow ,
                'final_net'     : rs.basic + allow - deduct - pph,
                'final_payment' : rs.basic + allow - deduct - pph + offfice_cost,
                
                'jsostek_amount': jamsostek_amount,
                'jsostek_emp'   : jamsostek_emp,
                'jsostek_comp'  : jamsostek_comp,
                'com_pension'   : com_pension_cont,
                'self_pension'  : self_pension_cont,
                
                'fix_allowance' : allow,
                'office_cost'   : offfice_cost,
                #'thr_amount'    : 
            }
            #print "record==============>",record
            res[rs.id] = record

            #=======================================================================
            # Slip line for Jamsostek oleh Perusahaan ??????????????????????????????
            #=======================================================================
            slip_line_jsos      = slip_line_obj.search(cr,uid,[('slip_id','=',rs.id),('name','=','Iuran Jamsostek oleh perusahaan periode %s' % (nmy))])
            print "slip_line_jsos",slip_line_jsos,type(slip_line_jsos)
            if payslip.jsostek_comp>0:
                jamsostek_line      = {
                                       'account_id'         : company_obj.com_jamsostek_acc.id,
                                       'analytic_account_id': company_obj.com_jamsostek_aacc.id,
                                       'category_id'        : company_obj.com_jamsostek_cat.id,
                                       'type'               : company_obj.com_jamsostek_cat.type,
                                       'amount_type'        : 'fix',
                                       'code'               : company_obj.com_jamsostek_cat.code,
                                       'name'               : 'Iuran Jamsostek oleh perusahaan periode %s' % (nmy),
                                       'sequence'           : company_obj.com_jamsostek_cat.sequence,
                                       'amount'             : payslip.jsostek_comp,
                                       'total'              : payslip.jsostek_comp,
                                       'slip_id'            : rs.id
                                       }
                if not slip_line_jsos:
                    print "WOI INI KOK DI-CREATE"
                    slip_line_obj.create(cr,uid,jamsostek_line,context=None)
                else:
                    slip_line_obj.write(cr,uid,slip_line_jsos[0],jamsostek_line,context=None)
            
            
            #=======================================================================
            # Slip line for Jamsostek oleh Karyawan
            #=======================================================================
            #slip_line_jsos      = self.pool.get('hr.payslip.line').search(cr,uid,[('slip_id','=',ids[0]),('name','=','Potongan Jamsostek periode %s' % (nmy))])
            found = False
            for pps in rs.line_ids:
                if pps['name'] == 'Potongan Jamsostek oleh karyawan periode %s' % (nmy):
                    found = True
                    idpps = pps.id
                    continue
            #print 'slip_line_jsos****',slip_line_jsos
            
            if payslip.jsostek_emp>0:
                jamsostek_line      = {
                                       'account_id'         : company_obj.emp_jamsostek_acc.id,
                                       'analytic_account_id': company_obj.emp_jamsostek_aacc.id,
                                       'category_id'        : company_obj.emp_jamsostek_cat.id,
                                       'type'               : company_obj.emp_jamsostek_cat.type,
                                       'amount_type'        : 'fix',
                                       'code'               : company_obj.emp_jamsostek_cat.code,
                                       'name'               : 'Potongan Jamsostek oleh karyawan periode %s' % (nmy),
                                       'sequence'           : company_obj.emp_jamsostek_cat.sequence,
                                       'amount'             : payslip.jsostek_emp,
                                       'total'              : payslip.jsostek_emp,
                                       'slip_id'            : rs.id
                                       }
                if not found:
                    slip_line_obj.create(cr,uid,jamsostek_line,context=None)
                else:
                    slip_line_obj.write(cr,uid,[idpps],jamsostek_line,context=None)
            
            #=======================================================================
            # Slip line for Retiring Contribution - Deduction
            #=======================================================================
            slip_line_retiring  = slip_line_obj.search(cr,uid,[('slip_id','=',rs.id),('name','=','Iuran Dana Pensiun periode %s' % (nmy))])
            retiring_line       = {
                                   'account_id'         : company_obj.emp_retiring_acc.id,
                                   'analytic_account_id': company_obj.emp_retiring_aacc.id,
                                   'category_id'        : company_obj.emp_retiring_cat.id,
                                   'type'               : company_obj.emp_retiring_cat.type,
                                   'amount_type'        : 'per',
                                   'code'               : company_obj.emp_retiring_cat.code,
                                   'name'               : 'Iuran Dana Pensiun periode %s' % (nmy),
                                   'sequence'           : company_obj.emp_retiring_cat.sequence,
                                   'amount'             : 0.02,
                                   'total'              : self_pension_cont,
                                   'slip_id'            : rs.id
                                   }
            if not slip_line_retiring:
                slip_line_obj.create(cr,uid,retiring_line,context=None)
            else:
                slip_line_obj.write(cr,uid,slip_line_retiring[0],retiring_line,context=None)
    
            
            #=======================================================================
            # Slip line for Retiring Contribution - Allowance
            #=======================================================================
            slip_line_retiring_com  = slip_line_obj.search(cr,uid,[('slip_id','=',rs.id),('name','=','Iuran Dana Pensiun oleh perusahaan periode %s' % (nmy))])
            retiring_com_line       = {
                                   'account_id'         : company_obj.com_retiring_acc.id,
                                   'analytic_account_id': company_obj.com_retiring_aacc.id,
                                   'category_id'        : company_obj.com_retiring_cat.id,
                                   'type'               : company_obj.com_retiring_cat.type,
                                   'amount_type'        : 'per',
                                   'code'               : company_obj.com_retiring_cat.code,
                                   'name'               : 'Iuran Dana Pensiun oleh perusahaan periode %s' % (nmy),
                                   'sequence'           : company_obj.com_retiring_cat.sequence,
                                   'amount'             : 0.06,
                                   'total'              : com_pension_cont,
                                   'slip_id'            : rs.id
                                   }
            if not slip_line_retiring_com:
                slip_line_obj.create(cr,uid,retiring_com_line,context=None)
            else:
                slip_line_obj.write(cr,uid,slip_line_retiring_com[0],retiring_com_line,context=None)
    
            
            #=======================================================================
            # Slip line for Biaya Jabatan
            #=======================================================================
    
            slip_line_officecost    = slip_line_obj.search(cr,uid,[('slip_id','=',rs.id),('name','=','Biaya jabatan periode %s' % (nmy))])
            office_cost_line        = {
                                       'account_id'         : company_obj.officecost_acc.id,
                                       'analytic_account_id': company_obj.officecost_aacc.id,
                                       'category_id'        : company_obj.officecost_cat.id,
                                       'type'               : company_obj.officecost_cat.type,
                                       'amount_type'        : 'fix',
                                       'code'               : company_obj.officecost_cat.code,
                                       'name'               : 'Biaya jabatan periode %s' % (nmy),
                                       'sequence'           : company_obj.officecost_cat.sequence,
                                       'amount'             : offfice_cost,
                                       'total'              : offfice_cost,
                                       'slip_id'            : rs.id
                                       }
            if not slip_line_officecost:
                slip_line_obj.create(cr,uid,office_cost_line,context=None)
            else:
                slip_line_obj.write(cr,uid,slip_line_officecost[0],office_cost_line,context=None)
        
            #=============================================================================
            # THR Karyawan
            #=============================================================================
            if rs.thr_amount>0:
                slip_line_thr  = slip_line_obj.search(cr,uid,[('slip_id','=',rs.id),('name','=','THR tahun %s' % (yy))])
                thr_line       = {
                                       'account_id'         : company_obj.emp_thr_acc.id,
                                       'analytic_account_id': company_obj.emp_thr_aacc.id,
                                       'category_id'        : company_obj.emp_thr_cat.id,
                                       'type'               : company_obj.emp_thr_cat.type,
                                       'amount_type'        : 'fix',
                                       'code'               : company_obj.emp_thr_cat.code,
                                       'name'               : 'THR tahun %s' % (yy),
                                       'sequence'           : company_obj.emp_thr_cat.sequence,
                                       'amount'             : rs.thr_amount,
                                       'total'              : rs.thr_amount,
                                       'slip_id'            : rs.id
                                       }
                if not slip_line_thr:
                    slip_line_obj.create(cr,uid,thr_line,context=None)
                else:
                    slip_line_obj.write(cr,uid,slip_line_thr[0],thr_line,context=None)
                    
            #=============================================================================
            # Bonus Karyawan
            #=============================================================================
            if rs.thr_amount>0:
                slip_line_bonus  = slip_line_obj.search(cr,uid,[('slip_id','=',ids[0]),('name','=','Bonus periode %s' % (nmy))])
                bonus_line       = {
                                       'account_id'         : company_obj.emp_bonus_acc.id,
                                       'analytic_account_id': company_obj.emp_bonus_aacc.id,
                                       'category_id'        : company_obj.emp_bonus_cat.id,
                                       'type'               : company_obj.emp_bonus_cat.type,
                                       'amount_type'        : 'fix',
                                       'code'               : company_obj.emp_bonus_cat.code,
                                       'name'               : 'Bonus periode %s' % (nmy),
                                       'sequence'           : company_obj.emp_bonus_cat.sequence,
                                       'amount'             : rs.bonus_amount,
                                       'total'              : rs.bonus_amount,
                                       'slip_id'            : rs.id
                                       }
                if not slip_line_thr:
                    slip_line_obj.create(cr,uid,bonus_line,context=None)
                else:
                    slip_line_obj.write(cr,uid,slip_line_bonus[0],bonus_line,context=None)

        return res
    
    _columns = {
                'grows'         : fields.function(_calculate, method=True, store=True, multi='dc', string='Gross Salary', digits_compute=dp.get_precision('Account')),
                'net'           : fields.function(_calculate, method=True, store=True, multi='dc', string='Net Salary', digits_compute=dp.get_precision('Account')),
                'allounce'      : fields.function(_calculate, method=True, store=True, multi='dc', string='Allowance', digits_compute=dp.get_precision('Account')),
                'deduction'     : fields.function(_calculate, method=True, store=True, multi='dc', string='Deduction', digits_compute=dp.get_precision('Account')),
                'other_pay'     : fields.function(_calculate, method=True, store=True, multi='dc', string='Others', digits_compute=dp.get_precision('Account')),
                'total_pay'     : fields.function(_calculate, method=True, store=True, multi='dc', string='Total Payment', digits_compute=dp.get_precision('Account')),
                'ptkp_amount'   : fields.function(_calculate, method=True, store=True, multi='dc', string='PTKP (monthly)', digits_compute=dp.get_precision('Account'),help="Nontaxable Wages Amount (monthly)"),
                'pph_percent'   : fields.function(_calculate, method=True, store=True, multi='dc', string='PPh (%)', digits_compute=dp.get_precision('Account'),help="PPh in percent"),
                'pph21'         : fields.function(_calculate, method=True, store=True, multi='dc', string='PPh (monthly)', digits_compute=dp.get_precision('Account')),
                'pkp'           : fields.function(_calculate, method=True, store=True, multi='dc', string='PKP (monthly)', digits_compute=dp.get_precision('Account'), help="Taxable Wages (monthly)"),
#                'overtime_fee'  : fields.function(_calculate, method=True, store=True, multi='dc', string='Overtime Fee', digits_compute=dp.get_precision('Account'),help="Overtime fee"),
#                'wageperhour'   : fields.function(_calculate, method=True, store=True, multi='dc', string='Wages /hour', digits_compute=dp.get_precision('Account'),help="Wages per hour, according to Indonesian Labor Laws is equal to Gross Salary devided by 173"),
                'final_gross'   : fields.function(_calculate, method=True, store=True, multi='dc', string='Final Gross', digits_compute=dp.get_precision('Account'),help="Final Gross Salary after calculation with PPh21, overtime"),
                'final_net'     : fields.function(_calculate, method=True, store=True, multi='dc', string='Final Net', digits_compute=dp.get_precision('Account'),help="Final Net Salary after calculation with PPh21, overtime"),
                'final_payment' : fields.function(_calculate, method=True, store=True, multi='dc', string='Final Payment', digits_compute=dp.get_precision('Account'),help="Payment Gross Salary after calculation with PPh21, overtime"),
                
                'jsostek_emp'   : fields.function(_calculate, method=True, store=True, multi='dc', string='Jamsostek by Employee', digits_compute=dp.get_precision('Account'),help="Jamsostek Cost by Employee"),
                'jsostek_comp'  : fields.function(_calculate, method=True, store=True, multi='dc', string='Jamsostek by Company', digits_compute=dp.get_precision('Account'),help="Jamsostek Cost by Employee"),
                'jsostek_amount': fields.function(_calculate, method=True, store=True, multi='dc', string='Jamsostek', digits_compute=dp.get_precision('Account'),help="Jamsostek Cost"),
                'com_pension'   : fields.function(_calculate, method=True, store=True, multi='dc', string='Com. Pension Contr.', digits_compute=dp.get_precision('Account'), help="Company Pension Contribution - 6%"),
                'self_pension'  : fields.function(_calculate, method=True, store=True, multi='dc', string='Emp. Pension Contr.', digits_compute=dp.get_precision('Account'), help="Employee Pension Contribution - 2%"),
                'fix_allowance' : fields.function(_calculate, method=True, store=True, multi='dc', string='Fix Allowance', digits_compute=dp.get_precision('Account'), help="Employee Fix Allowance"),
                'office_cost'   : fields.function(_calculate, method=True, store=True, multi='dc', string='Office Cost', digits_compute=dp.get_precision('Account'), help="Employee Office Cost Allowance"),
                'thr_amount'    : fields.float('THR', digits_compute=dp.get_precision('Account'), help="Employee THR"),
                'bonus_amount'  : fields.float('Bonus', digits_compute=dp.get_precision('Account'), help="Employee Bonus"),
                'line_ids2' : fields.one2many('hr.payslip.line', 'slip_id', 'Payslip Line', required=False, readonly=True, states={'draft': [('readonly', False)]}),
                }
    
hr_payslip()