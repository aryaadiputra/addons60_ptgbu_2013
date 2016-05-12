from osv import osv
from osv import fields
from tools.translate import _

class create_doc(osv.osv):
    _inherit = "document.directory"
    def onchange_parent(self, cr, uid, ids, part):
        if not part:
            return {'value': {'level': 0}}
        addr = self.pool.get('document.directory').browse(cr, uid, part)
        val = {
               'level': addr.level+1
        }
        print val
        return {'value': val}
    _columns = {
                'partner':fields.many2one('res.partner','Related Partner'),
                'partner_template':fields.many2one('partner.template','Related Partner Template'),
                'filled':fields.boolean('Must have',help='Check this box if this directory must have an appropriate document'),
                'level':fields.integer('Directory Level'),
                }
create_doc()

class res_partner_structure(osv.osv):
    _name = "res.partner.structure"

    _columns = {
                'employee_id': fields.many2one('hr.employee', 'Name'),
                'position' : fields.integer('Position'),
                }
res_partner_structure()

class res_partner_address(osv.osv):
    _inherit = "res.partner.address"
    _columns ={
               'structure_id' : fields.many2many('res.partner.structure','structure_rel','name','structure_id','Structure')
               }
res_partner_address()

class res_partner_shareholders(osv.osv):
    _name = "res.partner.shareholders"

    _columns = {
                'share_certificates'    : fields.char('Share Certificates',size=128),
                'share_owner':fields.many2one('res.partner', 'Partner Name'),
                'share_owning': fields.many2one('res.partner', 'Partner Name'),
                'name':fields.many2one('res.partner', 'Partner Name'),
                'is_person':fields.boolean('Is Person',help="Check this box if the shareholder is a person."),
                'contact':fields.many2one('res.partner.contact','Contact Name'),
                'share' : fields.integer('Share'),
                'share_value':fields.integer('Share Value'),
                'share_percent':fields.float('Share (%)',digits=(3,2)),
                'start_date':fields.date('Start Date'),
                'stop_date':fields.date('Stop Date'),
                }
    
    
    def create(self,cr,uid,values,context=None):
        sharelist=self.pool.get("res.partner.shareholders").search(cr,uid,[('name','=',values['name'])])
        contactlist=self.pool.get("res.partner.shareholders").search(cr,uid,[('contact','=',values['contact'])])
        partner=self.pool.get("res.partner").browse(cr,uid,values['name'])
        values['share_value']=partner['value_per_share']*values['share']
        values['share_percent']=float(values['share'])/float(partner['total_share'])*100
        
        if values['is_person']==1:
            values['share_owning']=False
            if len(contactlist)>0:
                raise osv.except_osv(_('Bad shareholder'), _("Shareholder you input has been saved before."))
        else:
            values['contact']=False
        
        owned_share=0
        if len(sharelist)>0:
            for shareline in sharelist:
                shareholder=self.pool.get("res.partner.shareholders").browse(cr,uid,shareline)
                owned_share=owned_share+shareholder['share']
                
                if shareholder['share_owning']['id']==values['share_owning']:
                    raise osv.except_osv(_('Bad shareholder'), _("Shareholder you input has been saved before."))
                
            owned_share=owned_share+values['share']
            owned_share_percent = float(owned_share)/float(partner['total_share'])*100
            not_owned_share = partner['total_share']-owned_share
            not_owned_share_percent = float(not_owned_share)/float(partner['total_share'])*100
            
            data={
                  'owned_share_amount':owned_share,
                  'owned_share_percent':owned_share_percent,
                  'not_owned_share_amount':not_owned_share,
                  'not_owned_share_percent':not_owned_share_percent
            }
            
            if owned_share<=partner['total_share']:
                self.pool.get("res.partner").write(cr,uid,values['name'],data)
            else:
                raise osv.except_osv(_('Bad amount'), _("Total amount share you input is higher than company's share total."))
        else:
            owned_share=owned_share+values['share']
            owned_share_percent = float(owned_share)/float(partner['total_share'])*100
            not_owned_share = partner['total_share']-owned_share
            not_owned_share_percent = float(not_owned_share)/float(partner['total_share'])*100
            
            data={'owned_share_amount':owned_share,
                  'owned_share_percent':owned_share_percent,
                  'not_owned_share_amount':not_owned_share,
                  'not_owned_share_percent':not_owned_share_percent
            }
            
            if owned_share<=partner['total_share']:
                self.pool.get("res.partner").write(cr,uid,values['name'],data)
            else:
                raise osv.except_osv(_('Bad amount'), _("Total amount share you input is higher than company's share total."))
        
        ids = super(res_partner_shareholders, self).create(cr, uid, values, context)
        return ids
    
    def unlink(self, cr, uid, ids, context=None):
        for id in ids:
            shareholder=self.pool.get("res.partner.shareholders").browse(cr,uid,id)
            partner=shareholder['name']
            
            owned_share=partner['owned_share_amount']-shareholder['share']
            owned_share_percent = float(owned_share)/float(partner['total_share'])*100
            not_owned_share = partner['total_share']-owned_share
            not_owned_share_percent = float(not_owned_share)/float(partner['total_share'])*100
            
            data={'owned_share_amount':owned_share,
                  'owned_share_percent':owned_share_percent,
                  'not_owned_share_amount':not_owned_share,
                  'not_owned_share_percent':not_owned_share_percent
            }
            
            self.pool.get("res.partner").write(cr,uid,partner['id'],data)
            
        result = super(res_partner_shareholders, self).unlink(cr, uid, ids, context=context)
        return result
    
    def write(self,cr,uid,ids,vals,context=None):
        shareholder=self.pool.get("res.partner.shareholders").browse(cr,uid,ids[0])
        contactlist=self.pool.get("res.partner.shareholders").search(cr,uid,[('contact','=',vals['contact'])])
        partner=shareholder['name']
        sharelist=self.pool.get("res.partner.shareholders").search(cr,uid,[('name','=',partner['id'])])
        
        if vals['is_person']==1:
            vals['share_owning']=False
            if len(contactlist)>0:
                raise osv.except_osv(_('Bad shareholder'), _("Shareholder you input has been saved before."))
        else:
            vals['contact']=False
        
        for shareline in sharelist:
            shareholder2=self.pool.get("res.partner.shareholders").browse(cr,uid,shareline)
            if shareholder2['share_owning']['id']==vals['share_owning'] or shareholder2['contact']==vals['contact']:
                raise osv.except_osv(_('Bad shareholder'), _("Shareholder you input has been saved before."))
        
        owned_share=partner['owned_share_amount']-shareholder['share']+vals['share']
        owned_share_percent = float(owned_share)/float(partner['total_share'])*100
        not_owned_share = partner['total_share']-owned_share
        not_owned_share_percent = float(not_owned_share)/float(partner['total_share'])*100
        
        data={'owned_share_amount':owned_share,
              'owned_share_percent':owned_share_percent,
              'not_owned_share_amount':not_owned_share,
              'not_owned_share_percent':not_owned_share_percent
        }
        
        self.pool.get("res.partner").write(cr,uid,partner['id'],data)
        vals['share_value']=partner['value_per_share']*vals['share']
        vals['share_percent']=float(vals['share'])/float(partner['total_share'])*100
        super(res_partner_shareholders, self).write(cr, uid, ids, vals, context=context)
        return True
    
    _defaults = {
                'share_owner' : lambda obj, cr, uid,context: obj.pool.get('ir.sequence').get(cr, uid, 'res.partner.shareholders'),
                }
res_partner_shareholders()

class function_line(osv.osv):
    _inherit = "res.partner.job"
    _columns = {
                'function_id' : fields.many2one('res.partner','Function ID'),
                }
function_line()

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns ={
            'company': fields.boolean('Company', help="Check this box if this is a company."),
            'government': fields.boolean('Government', help="Check this box if this is a government office."),
            'directory':fields.one2many('document.directory','partner','Directory List'),
            'attachment_ids': fields.one2many('ir.attachment','partner_id','Attachments'),
            'job_structure' : fields.one2many('res.partner.job','function_id','Partner Function'),
            'shareowner_id' : fields.one2many('res.partner.shareholders','name','Shareholder List'),
            'shareholder_id' : fields.one2many('res.partner.shareholders','share_owning','Share List'),
            'total_value':fields.integer('Total Company Value (Rp)'),
            'total_share':fields.integer('Total Share'),
            'value_per_share':fields.integer('Value per share (Rp)'),
            'owned_share_amount':fields.integer('Owned Share',readonly=True),
            'owned_share_percent':fields.float('Owned Share (%)',digits=(3,2),readonly=True),
            'not_owned_share_amount':fields.integer('Not Owned Share',readonly=True),
            'not_owned_share_percent':fields.float('Not Owned (%)',digits=(3,2),readonly=True),
            #'line_ids': fields.one2many('expenses.structure.line', 'line_id', 'Expense Lines',),
               }
    
    def onchange_total_value(self,cr,uid,ids,value):
        if value:
            return value
        
    def onchange_total_share(self,cr,uid,ids,value,share):
        if share:
            values = self.onchange_total_value(cr, uid, ids, value)
            val_per_share = values/share
            ret = {
                   'value_per_share':val_per_share
                   }
        return {'value':ret}
        
    def onchange_parent(self, cr, uid, ids, part):
        if not part:
            return {'value': {'level': 0}}
        addr = self.pool.get('document.directory').browse(cr, uid, part)
        val = {
               'level': addr.level+1
        }
        return {'value': val}
    
    def structure_directory(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids):
            pt = {'name' : data.name, 
                  'parent_id' : False,
                  'level':0, 
                  'type' : 'directory', 
                  'storage_id' : 1, 
                  'resource_find_all' : 1, 
                  'ressource_type_id' : False, 
                  'owner' : uid, 
                  'partner' : data.id,
                  'partner_template' : data.partner_category.partner_template.id,
                  }
            id_pt = self.pool.get('document.directory').create(cr, uid, pt)
            p = []
            for x in data.partner_category.directory_str:
                if x.level==2:
                    dir_lv1 = {'name' : x.name, 
                      'parent_id' : id_pt,
                      'level':1, 
                      'type' : 'directory', 
                      'storage_id' : 1, 
                      'resource_find_all' : 1, 
                      'ressource_type_id' : False, 
                      'owner' : uid, 
                      'partner' : data.id,
                      'partner_template' : data.partner_category.partner_template.id,}
                    id_dir_lv1 = self.pool.get('document.directory').create(cr, uid, dir_lv1)
                    
                    child=self.pool.get('document.directory').search(cr, uid,[('parent_id', 'child_of', x.id)])
                    if len(child)>1:
                        child.remove(x.id)
                        for c in child:
                            child_dir=self.pool.get('document.directory').browse(cr,uid,c)
                            if child_dir.level != 3:
                                continue
                            dir_lv2 = {'name' : child_dir.name, 
                              'parent_id' : id_dir_lv1,
                              'level':2, 
                              'type' : 'directory', 
                              'storage_id' : 1, 
                              'resource_find_all' : 1, 
                              'ressource_type_id' : False, 
                              'owner' : uid, 
                              'partner' : data.id,
                              'partner_template' : data.partner_category.partner_template.id,}
                            id_dir_lv2 = self.pool.get('document.directory').create(cr, uid, dir_lv2)
                            child=self.pool.get('document.directory').search(cr, uid,[('parent_id', 'child_of', c)])
                            if len(child)>1:
                                child.remove(c)
                                for child2 in child:
                                    child_dir=self.pool.get('document.directory').browse(cr,uid,child2)
                                    dir_lv3 = {'name' : child_dir.name, 
                                      'parent_id' : id_dir_lv2,
                                      'level':3, 
                                      'type' : 'directory', 
                                      'storage_id' : 1, 
                                      'resource_find_all' : 1, 
                                      'ressource_type_id' : False, 
                                      'owner' : uid, 
                                      'partner' : data.id,
                                      'partner_template' : data.partner_category.partner_template.id,}
                                    id_dir_lv3 = self.pool.get('document.directory').create(cr, uid, dir_lv3)
            data.write({"state":"confirm"})
        return True
    
    def rem_directory_strucutre(self,cr,uid,ids,context=None):
        val = self.browse(cr,uid,ids)[0]
        remove =[]
        
        parent = self.pool.get('document.directory').search(cr, uid,[('name','=',val.name)])
        remove = remove+parent
        if parent:
            for parent in parent :
                child1 = self.pool.get('document.directory').search(cr, uid,[('parent_id','=',parent)])
                remove = remove+child1
                if child1:
                    for child1 in child1 :
                        child2 = self.pool.get('document.directory').search(cr, uid,[('parent_id','=',child1)])
                        remove = remove+child2
                        if child2:
                            for child2 in child2 :
                                child3 = self.pool.get('document.directory').search(cr, uid,[('parent_id','=',child2)])
                                remove = remove+child3
                                if child3:
                                    for child3 in child3 :
                                        child4 = self.pool.get('document.directory').search(cr, uid,[('parent_id','=',child3)])
                                        remove = remove+child4
                                        if child4:
                                            for child4 in child4 :
                                                child5 = self.pool.get('document.directory').search(cr, uid,[('parent_id','=',child4)])
                                                remove = remove+child5
                                                if child5:
                                                    for child5 in child5 :
                                                        child6 = self.pool.get('document.directory').search(cr, uid,[('parent_id','=',child5)])
                                                        remove = remove+child6

        self.pool.get('document.directory').unlink(cr, uid,remove)
        return True
        
res_partner()