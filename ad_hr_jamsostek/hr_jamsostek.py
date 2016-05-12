from osv import osv,fields
import decimal_precision as dp
from tools.translate import _
import time
import tools
from datetime import date
from datetime import datetime
from datetime import timedelta
import pooler

class hr_jamsostek(osv.osv):
    _name = "hr.jamsostek"
    _description = "Jamsostek class"
    
    def _calculate(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        jht_amount      = 0
        jpk_amount      = 0
        jkk_amount      = 0
        jk_amount       = 0
        tk_lhk_amount   = 0
        married         =['married','sudah menikah','menikah','berkeluarga']
            
        for rs in self.browse(cr, uid, ids, context=context):
            contract_ids    = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',rs.name.id)])
            #print "contract_ids",contract_ids,rs.contract_id.name
            if len(contract_ids)==0:
                raise osv.except_osv(_('No Contract Found!'), _('No contract found for this employee!\nPlease create contract for this employee first.'))
            else:
                #contract        =self.pool.get('hr.contract').browse(cr,uid,contract_ids[0])
                contract        = self.browse(cr, uid, ids[0]).contract_id
            jht_amount = 0.0
            jht_by_employee = 0.0
            jht_by_company = 0.0
            jpk_amount = 0.0
            jkk_amount = 0.0
            jk_amount = 0.0
            if rs.jht:
                jht_amount=(contract.wage+contract.advantages_gross)*0.057
                jht_by_employee=(contract.wage+contract.advantages_gross)*0.02
                jht_by_company=(contract.wage+contract.advantages_gross)*0.037

            if rs.jpk:
                if rs.name.marital:
                    if rs.name.marital.name.lower() in married:
                        jpk_amount=(contract.wage+contract.advantages_gross)*0.06
                        if contract.wage>1000000:
                            jpk_amount=1000000*0.06
                    else:
                        jpk_amount=contract.wage*0.03
                        if contract.wage>1000000:
                            jpk_amount=1000000*0.03
                else:
                    raise osv.except_osv(_('No Marital Status Found!'), _('No marital status found for this employee!'))
            
            if rs.jkk:
                jkk_amount=(contract.wage+contract.advantages_gross)*0.008
                
            if rs.jk:
                jk_amount=(contract.wage+contract.advantages_gross)*0.003
            
            
            record = {
                      'jht_amount'      : jht_amount,
                      'jht_by_employee' : jht_by_employee,
                      'jht_by_company'  : jht_by_company,
                      'jpk_amount'      : jpk_amount,
                      'jkk_amount'      : jkk_amount,
                      'jk_amount'       : jk_amount,
                      'tk_lhk_amount'   : tk_lhk_amount,
                      'total'           : jht_amount+jpk_amount+jkk_amount+jk_amount+tk_lhk_amount,
                      'contract_wage'   : (contract.wage+contract.advantages_gross),
                      }
            res[rs.id] = record
        return res
    
    def _get_info(self, cr, uid, ids, field_names, arg, context=None):
        res= {}
        for jsostek in self.browse(cr,uid,ids,context):
            emp_id      = jsostek.name.id
            contract_id = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',emp_id),'|',('date_end','>=',time.strftime("%Y-%m-%d")),('date_end','=',False)])
            if not contract_id:
                raise osv.except_osv(_('No Valid Contract Found!'), _('No valid contract found for this employee!\nPlease create contract for this employee first.'))
            else:
                contract_id = contract_id[0]
            department_id        = jsostek.name.department_id.id
            section_id           = jsostek.name.section.id
            job_id               = jsostek.name.job_id.id
            current_job_level_id = jsostek.name.current_job_level.id
            record={
                    #'contract_id':contract_id or False,
                    'department_id':department_id or False,
                    'section_id':section_id or False,
                    'job_id':job_id,
                    'current_job_level_id':current_job_level_id,
                    }
            res[jsostek.id]=record
            #self.write(cr, uid, ids, {'contract_id': contract_id})
        return res
    
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        res = {}
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
            res['jnumber'] = employee.insurance_id
        return {'value': res}
    
    def onchange_period(self, cr, uid, ids, employee_id, period_id, context=None):
        res = {}
        period_obj  = self.pool.get('account.period')
        employee_obj  = self.pool.get('hr.employee')
        period      = period_obj.browse(cr, uid, period_id)
        contract_ids = self.pool.get('hr.contract').search(cr, uid, [('employee_id','=',employee_id),('date_start','<=',period.date_start),'|',('date_end','>=',period.date_start),('date_end','=',False)])
        if not contract_ids:
            raise osv.except_osv(_('No Valid Contract Found!'), _('No valid contract found for this employee!\nPlease create contract for this employee first.'))
        contract = self.pool.get('hr.contract').browse(cr, uid, contract_ids)[0]
        #jsostek = self.browse(cr, uid, ids)[0]
        if employee_id:
            emp = employee_obj.browse(cr, uid, employee_id)
            department_id        = emp.department_id.id
            section_id           = emp.section.id
            job_id               = emp.job_id.id
            current_job_level_id = emp.current_job_level.id
        res = {
            'contract_id': contract.id or False,
            'department_id': department_id or False,
            'section_id': section_id or False,
            'job_id': job_id,
            'current_job_level_id': current_job_level_id,
        }
        return {'value': res}
    
    _columns = {
                'jnumber'       : fields.char('Jamsostek Number',size=32,required=True,readonly=True, states={'draft':[('readonly',False)]}),
                'name'          : fields.many2one('hr.employee','Employee Name',required=True,readonly=True,states={'draft':[('readonly',False)]}),
                #'contract_id'   : fields.function(_get_info,method=True,string="Contract",type="many2one",obj="hr.contract",store=True,multi='dc'),
                'contract_id'   : fields.many2one('hr.contract', 'Contract',readonly=True,states={'draft':[('readonly',False)]}),
                'department_id' : fields.function(_get_info,method=True,type="many2one",string="Department",obj="hr.department",store=True,multi='dc'),
                'section_id'    : fields.function(_get_info,method=True,type="many2one",string="Section",obj="hr.section",store=True,multi='dc'),
                'job_id'        : fields.function(_get_info,method=True,type="many2one",string="Job",obj="hr.job",store=True,multi='dc'),
                'current_job_level_id': fields.function(_get_info,method=True,type="many2one",string="Current Job Level",obj="hr.department",store=True,multi='dc'),
                'emp_status'    : fields.char('Employee Status',size=64,readonly=True,states={'draft':[('readonly',False)]}),
                'reg_date'      : fields.date('Registered Date',readonly=True,states={'draft':[('readonly',False)]}),
                'branch_office' : fields.many2one('res.partner','Jamsostek Branch Office'),
                'jht'           : fields.boolean('Jaminan Hari Tua (JHT)',help='Check this box for JHT',required=True,readonly=True,states={'draft':[('readonly',False)]}),
                'jpk'           : fields.boolean('Jaminan Pemeliharaan Kesehatan (JPK)',help='Check this box for JPK',readonly=True,states={'draft':[('readonly',False)]}),
                'jkk'           : fields.boolean('Jaminan Kecelakaan Kerja (JKK)',help='Check this box for JKK',states={'draft':[('readonly',False)]}),
                'jk'            : fields.boolean('Jaminan Kematian',help='Check this box for JK',readonly=True,states={'draft':[('readonly',False)]}),
                'tk_lhk'        : fields.boolean('Luar Hubungan Kerja',help='Check this box for TK-LHK',readonly=True,states={'draft':[('readonly',False)]}),
                'tax_type'      : fields.selection([('k1','K1'),
                                                    ('k2','K2'),
                                                    ('k3','K3')],'Tax Type'),
                'bank_account'  : fields.char('Bank Account',size=32),
                'note'          : fields.text('Notes'),
                'period_id'     : fields.many2one('account.period','Period',readonly=True,states={'draft':[('readonly',False)]}),
                'contract_wage' : fields.function(_calculate, method=True, store=True, multi='dc', string='Wage', digits_compute=dp.get_precision('Account')),
                'jht_amount'    : fields.function(_calculate, method=True, store=True, multi='dc', string='JHT Amount', digits_compute=dp.get_precision('Account')),
                'jht_by_employee'    : fields.function(_calculate, method=True, store=True, multi='dc', string='JHT By Employee', digits_compute=dp.get_precision('Account')),
                'jht_by_company'    : fields.function(_calculate, method=True, store=True, multi='dc', string='JHT By Company', digits_compute=dp.get_precision('Account')),
                'jpk_amount'    : fields.function(_calculate, method=True, store=True, multi='dc', string='JPK Amount', digits_compute=dp.get_precision('Account')),
                'jkk_amount'    : fields.function(_calculate, method=True, store=True, multi='dc', string='JKK Amount', digits_compute=dp.get_precision('Account')),
                'jk_amount'     : fields.function(_calculate, method=True, store=True, multi='dc', string='JK Amount', digits_compute=dp.get_precision('Account')),
                'tk_lhk_amount' : fields.function(_calculate, method=True, store=True, multi='dc', string='TK-LHK Amount', digits_compute=dp.get_precision('Account')),
                'total'         : fields.function(_calculate, method=True, store=True, multi='dc', string='Total', digits_compute=dp.get_precision('Account')),
                'state'         : fields.selection([('draft','Draft'),('registered','Registered')],'State',readonly=True),
                }
    _defaults ={
                'state'         : 'draft',
                }
    
    def register(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'registered'})
        return True
    
    def cancel(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'draft'})
        return True
    
#    def onchange_employee(self,cr,uid,ids,employee_id,context=None):
#        val={}
#        if employee_id:
#            pass
#        return {'values':val}
#    
#
#    def compute_sheet(self,cr,uid,ids,context=None):
#        res = {}
#        jht_amount      = 0
#        jpk_amount      = 0
#        jkk_amount      = 0
#        jk_amount       = 0
#        tk_lhk_amount   = 0
#        married         =['married','sudah menikah','menikah','berkeluarga']
#            
#        for rs in self.browse(cr, uid, ids, context=context):
#            contract_ids    = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',rs.name.id)])
#            
#            if len(contract_ids)==0:
#                raise osv.except_osv(_('No Contract Found!'), _('No contract found for this employee!\nPlease create contract for this employee first.'))
#            else:
#                contract        =self.pool.get('hr.contract').browse(cr,uid,contract_ids[0])
#            
#            if rs.jht==True:
#                jht_amount=(contract.wage+contract.advantages_gross)*0.057
#                jht_by_employee=(contract.wage+contract.advantages_gross)*0.02
#                jht_by_company=(contract.wage+contract.advantages_gross)*0.037
#
#            if rs.jpk==True:
#                if rs.name.marital:
#                    if rs.name.marital.name.lower() in married:
#                        jpk_amount=(contract.wage+contract.advantages_gross)*0.06
#                        if contract.wage>1000000:
#                            jpk_amount=1000000*0.06
#                    else:
#                        jpk_amount=contract.wage*0.03
#                        if contract.wage>1000000:
#                            jpk_amount=1000000*0.03
#                else:
#                    raise osv.except_osv(_('No Marital Status Found!'), _('No marital status found for this employee!'))
#            
#            if rs.jkk==True:
#                jkk_amount=(contract.wage+contract.advantages_gross)*0.008
#                
#            if rs.jk==True:
#                jk_amount=(contract.wage+contract.advantages_gross)*0.003
#            
#            
#            
#            record = {
#                      'jht_amount'      : jht_amount,
#                      'jht_by_employee' : jht_by_employee,
#                      'jht_by_company'  : jht_by_company,
#                      'jpk_amount'      : jpk_amount,
#                      'jkk_amount'      : jkk_amount,
#                      'jk_amount'       : jk_amount,
#                      'tk_lhk_amount'   : tk_lhk_amount,
#                      'total'           : jht_amount+jpk_amount+jkk_amount+jk_amount+tk_lhk_amount,
#                      'contract_wage'   : contract.wage+contract.advantages_gross,
#                      }
#            print "XXXXXXXXXXXXXXX",record
#            #self.write(cr,uid,[rs.id],record)
#        return {'value':record}
hr_jamsostek()