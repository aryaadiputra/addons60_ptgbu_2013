from osv import osv,fields

class res_organization_structures(osv.osv):
    _name    = "res.organization.structures"
    
    def _get_job_level(self,cr,uid,ids,field,arg,context={}):
        orgs=self.browse(cr,uid,ids,context=context)
        result = {}
        for org in orgs :
            result[org.id] = org.head and org.head.current_job_level.id or False
        return result
    
    def _get_struct_name(self,cr,uid,ids,field,arg,context={}):
        orgs=self.browse(cr,uid,ids,context=context)
        result = {}
        for org in orgs :
            #print org.job_id.name
            result[org.id] = org.job_id and org.job_id.name or False
        return result
    
    _columns = {
                'name'      : fields.function(_get_struct_name,method=True,type='char',size=64,string='Name',help="Structure name",store=True),
                'parent_id' : fields.many2one('res.organization.structures','Parent'),
                'child'     : fields.one2many('res.organization.structures','parent_id','Child'),
                'head'      : fields.many2one('hr.employee','Head'),
                'type'      : fields.selection([('bob','BOB'),('bsp','Kantor Pusat')],"Type"),
                'job_id'    : fields.many2one("hr.job",'Job',help="Job of the Head"),
                'job_level' : fields.function(_get_job_level,method=True,type='many2one',obj="hr.job.level",string='Job Level',help="Job Level of the Head",store=True),
                'history_ids'  : fields.one2many("org.structure.history",'structure_id',"Head History",readonly=True)
                }
    
    def onchange_job_id(self,cr,uid,ids,job_id,context={}):
        if job_id:
            job=self.pool.get('hr.job').browse(cr,uid,job_id)
            employee=self.pool.get('hr.employee').search(cr,uid,[('job_id','=',job_id)])
            employee_id=False
            if employee:
                employee_id=employee[0]
            
            val={'value':{
                         'type':job.placement,
                         'head':employee_id
                         }}
            return val
        else:
            return {'value':{}}
    
    _defaults = {
                'type': lambda *a:'bsp',
                 }
    
    _sql_constraints = [
        ('no_selfparent', 'check(parent_id <> id)', 'Cannot be parent of itself!'),
    ]

res_organization_structures()

class org_structure_history(osv.osv):
    _name = "org.structure.history"
    _columns = {
        'employee_id':fields.many2one('hr.employee',"Employee Name"),
        'date_changed' : fields.date("Mutation Date"),
        'structure_id':fields.many2one('res.organization.structures',"Structure Name"),
                }
    
org_structure_history()

class res_organization_structure_wizard(osv.osv_memory):
    _name="res.organization.structures.wiz"
    _columns = {
        'type':fields.selection([('bob','BOB'),('bsp','Kantor Pusat')],"Type",required=True),
                }
    
    def org_struct_open_window(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        #period_obj = self.pool.get('account.period')
        #fy_obj = self.pool.get('account.fiscalyear')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        
        
        #result['periods'] = []
        if data['type']=='bob':
            result = mod_obj.get_object_reference(cr, uid, 'organization_structure', 'action_company_structure3')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            idbob=self.pool.get('res.organization.structures').search(cr,uid,[('type','in',('main','bob'))])
            result['context'] = str({'active_ids': idbob,})
        else:
            result = mod_obj.get_object_reference(cr, uid, 'organization_structure', 'action_company_structure2')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
            idhead=self.pool.get('res.organization.structures').search(cr,uid,[('type','in',('main','head'))])
            result['context'] = str({'active_ids': idhead,})
            
        print "result"
        return result
    
res_organization_structure_wizard()