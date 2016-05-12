from osv import fields,osv

class hr_report_wizard(osv.osv_memory):
    _name = "hr.report.wizard"
    type = [('list',"Employee Report List")]
    placement = [("bsp","BSP only"),("bob",'BOB only'),("all","BSP & BOB"),]
    group= [('department','Department'),('section','Section'),('none',"No Grouping"),('level','Job Level'),
            ('location','Work Location'),('bagian',"Function"),('gender','Gender'),('age',"Age"),('workexperience',"Working Experience Time")]
    
    def onchange_placement(self,cr,uid,ids,placement,context={}):
        if placement=="bob":
            return {'value':{'filter_dept':False,'filter_sect':False},'domain':{'filter_dept':[('placement','=','bob')],'filter_sect':[('placement','=','bsp')]}}
        elif placement=="bsp":
            return {'value':{'filter_dept':False,'filter_sect':False},'domain':{'filter_dept':[('placement','=','bsp')],'filter_sect':[('placement','=','bsp')]}}
        else:
            return {'value':{'filter_dept':False,'filter_sect':False},'domain':{'filter_dept':[],'filter_sect':[]}}
    
    def onchange_dept(self,cr,uid,ids,dept,placement,context={}):
        if placement=="bob":
            return {'domain':{'filter_sect':[('placement','=','bob'),'|',('department','in',dept[0][2]),('department','=',False)]}}
        elif placement=="bsp":
            return {'domain':{'filter_sect':[('placement','=','bsp'),('department','in',dept[0][2]),]}}
        else:
            if len(dept[0][2])>0:
                depts=self.pool.get('hr.department').browse(cr,uid,dept[0][2])
                for d in depts:
                    if d.placement=='bob':
                        return {'domain':{'filter_sect':['|',('department','in',dept[0][2]),('department','=',False)]}}
                return {'domain':{'filter_sect':[('department','in',dept[0][2])]}}
            else:
                return {'domain':{'filter_sect':[]}}
                
    _columns = {
        'type':fields.selection(type,"Reporting Type",required=True),
        'placement':fields.selection(placement,"Placement",required=True),
        'group':fields.selection(group,"Group by",required=True),
        'active':fields.selection([('active','Active'),('inactive','Non Active'),('all','All')],'Employee State',required=True),
        'filter_dept':fields.many2many('hr.department','dept_report_rel','department_id','wiz_id',"Department",required=True),
        'filter_sect':fields.many2many('hr.section','sect_report_rel','sect_id','wiz_id',"Section",required=True)
                }
    
    _defaults = {
        'type': lambda *rep_type:'list',
        'placement': lambda *placement:'all',
        'group':lambda *group:'department',
        'active':lambda *active:'active',
        'filter_dept':lambda self, cr, uid, *c: self.pool.get('hr.department').search(cr, uid, []),
        'filter_sect':lambda self, cr, uid, *d: self.pool.get('hr.section').search(cr, uid, []),
                 }
    
    def report_hr_custom(self, cr, uid, ids, context):
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'hr.report.wizard'
        datas['form'] = self.read(cr, uid, ids)[0]
        form = datas['form']
        if form['type']=='list':
            if form['group']=='department':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.custom.department.list',
                    'report_type': 'webkit',
                    'datas': datas,
                }
            elif form['group']=='section':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.custom.section.list',
                    'report_type': 'webkit',
                    'datas': datas,
                }
            elif form['group']=='location':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.custom.location.list',
                    'report_type': 'webkit',
                    'datas': datas,
                }
            elif form['group']=='gender':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.custom.gender.list',
                    'report_type': 'webkit',
                    'datas': datas,
                }
            elif form['group']=='level':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.custom.joblevel.list',
                    'report_type': 'webkit',
                    'datas': datas,
                }
            elif form['group']=='bagian':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.custom.bagian.list',
                    'report_type': 'webkit',
                    'datas': datas,
                }
            elif form['group']=='age':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.custom.age.list',
                    'report_type': 'webkit',
                    'datas': datas,
                }
            elif form['group']=='workexperience':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.custom.workexperience.list',
                    'report_type': 'webkit',
                    'datas': datas,
                }
        elif form['type']=='contract':
            if form['group']=='department':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.contract.list',
                    'report_type': 'webkit',
                    'datas': datas,
                }
            elif form['group']=='section':
                return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'report.hr.custom.section.list',
                    'report_type': 'webkit',
                    'datas': datas,
                }
    
hr_report_wizard()