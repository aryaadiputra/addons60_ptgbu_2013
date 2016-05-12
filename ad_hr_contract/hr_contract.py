from osv import osv,fields
from tools.translate import _
import time

class hr_contract(osv.osv):
    _inherit        = "hr.contract"
    
    _columns        = {
                       'department' : fields.many2one('hr.department','Department'),
                       'level'      : fields.many2one('hr.job.level','Level'),
		       'nomor_sk'   : fields.char('Nomor SK', size=64),
                       #'employee_id': fields.many2one('hr.employee','Employee')
                       }

#<<<<<<< TREE
#    def onchange_employee_id(self, cr, uid, ids, employee_id,context={}):
#        if employee_id:
#            emp_data=self.pool.get('hr.employee').browse(cr,uid,[employee_id])[0]
#            
#            val = {
#                   'department': emp_data.department_id and emp_data.department_id.id or False,
#                   'level': emp_data.current_job_level and emp_data.current_job_level.id or False,
#                   'job_id':emp_data.job_id and emp_data.job_id.id or False,
#                   'struct_id':emp_data.current_job_level.sal_struc and emp_data.current_job_level.sal_struc.id or False,
#                }
#            print "value===",val
#            return {'value':val}
#        return True
#=======
#    
#    
    def onchange_employee_id(self, cr, uid, ids, employee_id,context={}):
        if employee_id:
            emp_data=self.pool.get('hr.employee').browse(cr,uid,[employee_id])[0]
            
            val = {
                   'department':emp_data.department_id and emp_data.department_id.id or False,
                   'level':emp_data.current_job_level and emp_data.current_job_level.id or False,
                   'job_id': emp_data.job_id and emp_data.job_id.id or False,
                   'struct_id': emp_data.current_job_level.sal_struc and emp_data.current_job_level.sal_struc.id or False,
                   'name': emp_data.admission_letter,
                }
            return {'value':val}
        return True
    
#>>>>>>> MERGE-SOURCE
        
    def write(self,cr,uid,ids,data,context=None):
        print data
        if 'date_end' in data.keys():
            print "data['date_end']",data['date_end']
            contract        = self.browse(cr,uid,ids[0])
            other_contract  = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',contract.employee_id.id)])
            other_contract.remove(ids[0])
            for others in self.browse(cr,uid,other_contract):
                if data['date_end'] >= others.date_start and data['date_end'] <= others.date_end:
                    raise osv.except_osv(_('Overlap Date End'), _('Date End is overlap with the other contract !\n[%s: %s - %s]') % (others.name, others.date_start, others.date_end))
                if data['date_end']==False:
                    if others.date_end>time.strftime("%Y-%m-%d") or others.date_end==False:
                        raise osv.except_osv(_('Overlap Date End'), _('Date End is overlap with the other contract !\n[%s: %s - %s]') % (others.name, others.date_start, others.date_end))
        
        if 'date_start' in data.keys():
            contract        = self.browse(cr,uid,ids[0])
            other_contract  = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',contract.employee_id.id)])
            other_contract.remove(ids[0])
            for others in self.browse(cr,uid,other_contract):
                if data['date_start'] > others.date_start and not others.date_end:
                    raise osv.except_osv(_('Contract does not terminated'), _('There is a not-terminated-contract for %s !\n[%s: %s - %s]') % (others.employee_id.name, others.name, others.date_start, others.date_end))
                if data['date_start'] <= others.date_end and data['date_start'] >= others.date_start:
                    raise osv.except_osv(_('Overlap Date Start'), _('Date Start is overlap with the other contract !\n[%s: %s - %s]') % (others.name, others.date_start, others.date_end))
        return super(hr_contract,self).write(cr,uid,ids,data,context=context)
    
    def create(self,cr,uid,data,context=None):
        other_contract  = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',data['employee_id'])])
        if data['date_end']:
            for others in self.browse(cr,uid,other_contract):
                if data['date_end'] >= others.date_start and data['date_end'] <= others.date_end:
                    raise osv.except_osv(_('Overlap Date End'), _('Date End is overlap with with the other contract !\n[%s: %s - %s]') % (others.name, others.date_start, others.date_end))
        else:
            for others in self.browse(cr,uid,other_contract):
                if others.date_end>time.strftime("%Y-%m-%d") or others.date_end==False:
                    raise osv.except_osv(_('Overlap Date End'), _('Date End is overlap with the other contract !\n[%s: %s - %s]') % (others.name, others.date_start, others.date_end))
        
        if data['date_start']:
            other_contract  = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',data['employee_id'])])
            for others in self.browse(cr,uid,other_contract):
                if data['date_start'] > others.date_start and not others.date_end:
                    raise osv.except_osv(_('Contract does not terminated'), _('There is a not-terminated-contract for %s !\n[%s: %s - %s]') % (others.employee_id.name, others.name, others.date_start, others.date_end))
                if data['date_start'] <= others.date_end and data['date_start'] >= others.date_start:
                    raise osv.except_osv(_('Overlap Date Start'), _('Date Start is overlap with with the other contract !\n[%s: %s - %s]') % (others.name, others.date_start, others.date_end))

        return super(hr_contract,self).create(cr,uid,data,context=context)
hr_contract()
