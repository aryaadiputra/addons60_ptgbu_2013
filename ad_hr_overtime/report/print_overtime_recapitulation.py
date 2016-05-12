from osv import osv, fields
from report import report_sxw
from datetime import datetime
from datetime import date
from tools.translate import _
import tools
import time

class or_wizard(osv.osv_memory):
    _name       = 'or.wizard'
    
    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('periode', False):
            return context.get('periode')
        periods = self.pool.get('account.period').find(cr, uid)
        return periods and periods[0] or False
    
    _columns    = {
            'name'       : fields.selection([('employee','All Employee'),
                                         ('type','Employee Type')],'Print By',required=True),
            'type'       : fields.selection([('permanent','Permanent Employee'),
                                         ('outsource','Outsources Employee')],'Employee Status'),
            'date'       : fields.date('Date'),
            'periode'   : fields.many2one('account.period', 'Periode'),
            'filter'     : fields.selection([('date','Date'),('periode','Periode')], 'Filter By'),
            #'date_end'   : fields.date('Date End',required=True),
            'employee'   : fields.many2many('hr.employee','or_employee_rel','employee_id','wizard_id','Employee',domain=['|',('type','=','bsp'),('status','=','outsource'),('current_job_level.job_level','in',(1,2,3,4,5,6))]),
            'permanent'  : fields.many2many('hr.employee','or_permanent_rel','employee_id','wizard_id','Permanent Employee',domain=['|',('type','=','bsp'),('current_job_level.job_level','in',(1,2,3,4,5,6))]),
            'outsource'  : fields.many2many('hr.employee','or_outsource_rel','employee_id','wizard_id','Outsource Employee',domain=[('status','=','outsource')]),
   }
    _defaults   = {
            #'date'       : time.strftime('%Y-%m-%d'),
            #'date_end'   : time.strftime('%Y-%m-%d'),
            'filter'     : 'periode',
            'periode'    : _get_period,
            'name'       : 'employee',
            'type'       : 'permanent'
   }
    def report_overtime(self, cr, uid, ids, context):
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'or.wizard'
        datas['form'] = self.read(cr, uid, ids)[0]
        #print 'datas==============',datas
        if datas['form']['name']=='employee':
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'employee.overtime.recapitulation',
                    'report_type': 'webkit',
                    'datas': datas,
                    }
        else:
            if datas['form']['type']=='permanent':
                return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'employee.permanent.overtime.recapitulation',
                        'report_type': 'webkit',
                        'datas': datas,
                        }
            else:
                return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'employee.outsource.overtime.recapitulation',
                        'report_type': 'webkit',
                        'datas': datas,
                        }
or_wizard()

class overtime_recapitulation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(overtime_recapitulation, self).__init__(cr, uid, name, context=context)
        #print 'self.localcontext',self.localcontext
        self.localcontext.update({
                  'get_object'      : self._get_object,
                  'get_periode'     : self._get_periode,
                  'get_overtime'    : self._get_overtime,
                  'convert_date'    : self._convert_date,
                  'convert_time'    : self._convert_time,
                  'is_holiday'      : self._is_holiday,
                  'get_contract'    : self._get_contract,
                  'get_current_date': self._get_current_date,
                  'get_dept'        : self._get_dept,
          })
        #print 'name+++++',name
        #print self.localcontext
        
    def _get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['form']['id']])
        return obj_data
    
    def _get_periode(self, data):
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(data,"%Y-%m-%d")))
        bulan = tools.ustr(ttyme.strftime('%m'))
    	if bulan == '01':
    	    mo = 'Januari'
    	elif bulan == '02':
            mo = 'Februari'	
    	elif bulan == '03':
            mo = 'Maret'
    	elif bulan == '04':
            mo = 'April'
    	elif bulan == '05':
            mo = 'Mei'
    	elif bulan == '06':
            mo = 'Juni'
    	elif bulan == '07':
            mo = 'Juli'
    	elif bulan == '08':
            mo = 'Agustus'
    	elif bulan == '09':
            mo = 'September'
    	elif bulan == '10':
            mo = 'Oktober'
    	elif bulan == '11':
            mo = 'November'
    	elif bulan == '12':
            mo = 'Desember'
    	else:
    	    mo = tools.ustr(ttyme.strftime('%B'))
    	tahun = tools.ustr(ttyme.strftime('%Y'))
        #print "tahun, mo",tahun, mo
        return "%s %s" % (mo,tahun)
    
    def _get_overtime(self, emp, filter, date, periode):
        if date:
            ttyme_start = datetime.fromtimestamp(time.mktime(time.strptime(date,"%Y-%m-%d")))
        #ttyme_end = datetime.fromtimestamp(time.mktime(time.strptime(date_end,"%Y-%m-%d")))
        #print "ttyme_start,ttyme_end",ttyme_start,ttyme_end
        #periode = tools.ustr(ttyme_start.strftime('%B %Y'))
        #print "date",date
        if filter == 'periode':
            overtime_id = self.pool.get('hr.overtime').search(self.cr, self.uid, [('periode','=',periode),('name','=',emp),('state','=','done'),])
        else:
            overtime_id = self.pool.get('hr.overtime').search(self.cr, self.uid, [('date','=',date),('name','=',emp),('state','=','done'),])
        #print "here we are =====>",overtime_id
        overtime    = self.pool.get('hr.overtime').browse(self.cr, self.uid, overtime_id)
        return overtime
    
    def _convert_date(self, data):
        ttyme   = datetime.fromtimestamp(time.mktime(time.strptime(data,"%Y-%m-%d %H:%M:%S")))
        date    = tools.ustr(ttyme.strftime('%d/%m/%Y'))
        return date
    
    def _convert_time(self, data):
        ttyme   = datetime.fromtimestamp(time.mktime(time.strptime(data,"%Y-%m-%d %H:%M:%S")))
        jam     = tools.ustr(ttyme.strftime('%H:%M'))
        return jam
    
    def _is_holiday(self, data):
        ttyme   = datetime.fromtimestamp(time.mktime(time.strptime(data,"%Y-%m-%d %H:%M:%S")))
        date    = ttyme.strftime('%Y-%m-%d')
        ids     = self.pool.get('hr.holiday.year').search(self.cr, self.uid, [('date','=',date)])
        x = time.strftime('%w', time.strptime(date,'%Y-%m-%d'))
        
        if len(ids) > 0 or x in ['6','0']:
            return True
        else:
            return False
    
    def _get_contract(self, emp, date):
        contract_ids    = self.pool.get('hr.contract').search(self.cr, self.uid, [('employee_id','=',emp),('date_start','<',date),'|',('date_end','>',date),('date_end','=',False)])
        contract        = self.pool.get('hr.contract').browse(self.cr, self.uid, contract_ids)
        if  len(contract)<>0:
            contract    = contract[0]
        else:
            contract    = False
        return contract
    
    def _get_current_date(self):
        current = time.strftime('%Y-%m-%d')
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(current,"%Y-%m-%d")))
        current = tools.ustr(ttyme.strftime('%e %B %Y'))
        return current
    
    def _get_dept(self):
        dept_id     = self.pool.get('hr.department').search(self.cr, self.uid, [('name','ilike','sdm')])
        dept        = self.pool.get('hr.department').browse(self.cr, self.uid, dept_id)
        if len(dept)<>0:
            dept_name   = dept[0]
        else:
            dept_name   = False
        return dept_name
    
report_sxw.report_sxw('report.employee.overtime.recapitulation', 'hr.overtime', 'ad_hr_overtime/report/print_employee_overtime_recapitulation.mako', parser=overtime_recapitulation, header = False)
report_sxw.report_sxw('report.employee.permanent.overtime.recapitulation', 'hr.overtime', 'ad_hr_overtime/report/print_employee_permanent_overtime_recapitulation.mako', parser=overtime_recapitulation, header = False)
report_sxw.report_sxw('report.employee.outsource.overtime.recapitulation', 'hr.overtime', 'ad_hr_overtime/report/print_employee_outsource_overtime_recapitulation.mako', parser=overtime_recapitulation, header = False)
