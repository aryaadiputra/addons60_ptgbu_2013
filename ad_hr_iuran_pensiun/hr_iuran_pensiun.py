import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from osv import osv,fields
import tools
from tools.translate import _


class hr_employee_retirement(osv.osv):
    _name           ="hr.employee.retirement"
    _description    =" Employee's Retirement"
    _columns        ={
                      'name'                : fields.many2one('hr.employee','Name' , required=True),
                      'nik'                 : fields.char('NIK', size=16),
                      'tmt_bsp'             : fields.date('TMT BSP'),
                      'sk_number'           : fields.char('Admission Letter', size=16),
                      'date_of_birth'       : fields.date('Date of Birth'),
                      'date_of_retirement'  : fields.date('Date of Retirement Plan'),
                      'wage'                : fields.float('Gross Wage'),
                      'retirement'          : fields.float('DPK Amount'),
                      'wage'                : fields.float('Monthly Wage'),
                      'total'               : fields.float('Monthly Pension Amount'),
                      'tot_by_employee'     : fields.float('Employee Contribution'),
                      'tot_by_company'      : fields.float('Company Contribution'),
                      'total_pension'       : fields.float('Total Pension Amount YTD'),
                      'period_id'           : fields.many2one('account.period','Period',required=True),
                      'state'               : fields.selection([('draft','Draft'),('registered','Registered')],'State',readonly=True)
                      }
    
    _defaults = {
                 'state'    : 'draft',
                 }
    
    def compute_pensiun(self,cr,uid,ids,context={}):
        data={}
        for pensiun in self.browse(cr,uid,ids):
            data['total']=0.08*pensiun.wage
            data['tot_by_employee']=0.02*pensiun.wage
            data['tot_by_company']=0.06*pensiun.wage
            data['total_pension']=0
            sum_paid_ids = self.search(cr,uid,[('name','=',pensiun.name.id)])
            self.write(cr,uid,ids,data)
            for sum_paid in self.browse(cr,uid,sum_paid_ids):
                data['total_pension']+=sum_paid.tot_by_employee
            data['state']='registered'    
            self.write(cr,uid,ids,data)
        return True
    
    def cancel(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"draft"})
        return True
    
    def onchange_period_id(self, cr, uid, ids,period_id):
        return {'value':{'name':False}}
    
    def onchange_employee_id(self, cr, uid, ids, emp_id,period_id):
        val = {
               'nik': False,
               'sk_number': False,
               'tmt_bsp' : False,
               'date_of_birth' : False,
               'wage':False,
            }
        now = time.strftime('%Y-%m-%d')
        if not period_id:
            raise osv.except_osv(_('No Period Defined !'), _('No Period Defined ! Please define the period first.'))
        else:
            period = self.pool.get('account.period').browse(cr, uid, period_id)
        if emp_id and period_id:
            ispensionexist=self.search(cr,uid,[('name','=',emp_id),('period_id','=',period_id)])
            if ispensionexist:
                raise osv.except_osv(_('Pension in Period Exist !'), _('Pension for this employee in defined period already exist, please check defined Period.'))
            else:
                emp = self.pool.get('hr.employee').browse(cr, uid, emp_id)
                nik = emp.nik or False
                adm = emp.admission_letter or False
                tmt = emp.doj or False
                dob = emp.birthday or False
                date_of_retirement = emp.retiring_date
                #q=['&','|',('date_end','>=',period.date_stop),('date_end','=',False),('employee_id','=',emp_id),('date_start','<=',period.date_stop)]
                q=[('employee_id','=',emp_id),('date_start','<=',now),'|',('date_end','>=',now),('date_end','=',False)]
                
                contract_ids=self.pool.get('hr.contract').search(cr,uid,q)
                print contract_ids
                if contract_ids:
                    for c in self.pool.get('hr.contract').browse(cr,uid,contract_ids):
                        wage=c.wage
                else:
                    raise osv.except_osv(_('No Contract'), _('The employee you choose has no available contract.'))
                val = {
                       'nik': nik,
                       'sk_number': adm,
                       'tmt_bsp' : tmt,
                       'date_of_birth' : dob,
                       'wage':wage,
                       'date_of_retirement':date_of_retirement,
                    }
        return {'value': val}
        

hr_employee_retirement()

class print_iuran_pensiun(osv.osv):
    _name       = "iuran.pensiun"
    _columns    = {
                   'period'     : fields.many2one('account.period','Period', required=True),
                   'name'       : fields.char('Name', size=32, readonly=True, states={'new': [('readonly', False)]}),
                   'employee'   : fields.many2many('hr.employee','employee_pensiun_rel','employee_id','pensiun_id','Employee'),
                   'state'      : fields.selection([('draft','Draft'),
                                                    ('approved','Approved'),
                                                    ('paid','Paid')], 'State', readonly=True),
                   }
    
    _defaults = {
                 'state'    : 'draft',
                 }
    
    def onchange_employee_list(self,cr,uid,ids,emp):
        now = time.strftime('%Y-%m-%d')
        if emp:
            ids=[]
            for eid in emp[0][2]:
                contract = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',eid)])
                if len(contract)<>0:
                    for c in self.pool.get('hr.contract').browse(cr,uid,contract):
                        if (now<c.date_end or not c.date_end) and now>=c.date_start:
                            ids.append(eid)
        res = {
               'employee'   : ids,
               }
        return {'value': res}
    
    def button_approve(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            ttyme = datetime.fromtimestamp(time.mktime(time.strptime(chk.period.date_start,"%Y-%m-%d")))
            record = {
                      'state':'approved',
                      'name':'Iuran Pensiun periode %s' % (tools.ustr(ttyme.strftime('%B-%Y'))),
                      }
            chk.write(record)
        return True
    
    def button_draft(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"draft"})
        return True
    
    def button_cancel(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"draft"})
        return True
    
    def button_paid(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"paid"})
        return True
    
    def get_emp_ids(self,cr,uid,ids,context=None):
        contract = self.pool.get('hr.contract').search(cr,uid,[()])
        return True
    
    def print_iuran(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas           = {'ids': context.get('active_ids', [])}
        datas['model']  = 'hr.employee'
        datas['form']   = self.read(cr, uid, ids)[0]
        dict = {
            'type': 'ir.actions.report.xml',
            'report_name': 'print.iuran.pensiun',
            'report_type': 'webkit',
            'datas': datas,
        }
        return dict 
    
print_iuran_pensiun()
