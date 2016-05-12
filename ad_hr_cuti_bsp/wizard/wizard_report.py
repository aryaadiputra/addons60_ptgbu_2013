from osv import fields, osv

class hr_cuti_report(osv.osv_memory):
    _name = "hr.cuti.report"
    _description = "Report Cuti"
    
    _columns = {
        'filter': fields.selection([('employee','Employee'),('department','Department')], 'Filter', size=32, required=True, help="Choose your filter"),
        'employee_id':fields.many2many('hr.employee','cuti_employee_rel','employee_id','cuti_id',"Employee",domain=[('type','=','bsp')],required=False),
        'department_id':fields.many2many('hr.department','cuti_department','department_id','cuti_id',"Department",domain=[('placement','=','bsp')],required=False),
        'start_date':fields.date("Dari",required=True),
        'end_date':fields.date("Sampai",required=True),
                }
    _defaults = {
        'filter':'department', 
                 }
    
    def report_cuti_bsp(self, cr, uid, ids, context):
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'hr.cuti.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        if datas['form']['filter']=='employee':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'report.cuti.bsp',
                'report_type': 'webkit',
                'datas': datas,
            }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'report.cuti.bsp.department',
                'report_type': 'webkit',
                'datas': datas,
            }
       
hr_cuti_report()