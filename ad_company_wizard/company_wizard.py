import time
import datetime
from dateutil.relativedelta import relativedelta
import base64, urllib
import os
import random
import tools
from osv import osv, fields
class wizard_screen(osv.osv_memory):
    _name = 'ir.wizard.screen'

    def _get_image(self, cr, uid, context=None):
        path = os.path.join('base','res','config_pixmaps','%d.png'%random.randrange(1,4))
        image_file = file_data = tools.file_open(path,'rb')
        try:
            file_data = image_file.read()
            return base64.encodestring(file_data)
        finally:
            image_file.close()

    def _get_image_fn(self, cr, uid, ids, name, args, context=None):
        image = self._get_image(cr, uid, context)
        return dict.fromkeys(ids, image) # ok to use .fromkeys() as the image is same for all 

    _columns = {
        'config_logo': fields.function(_get_image_fn, string='Image', type='binary', method=True),
    }

    _defaults = {
        'config_logo': _get_image
    }
wizard_screen()
class res_partner_gbu(osv.osv):
    _inherit = "res.partner"
    def new_company(self, cr, uid, ids, context={}):
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
            data.write({"state":"company_addr"})
        return True
    def company_addr(self,cr,uid,ids,context={}):
        for data in self.browse(cr, uid, ids):
            print "DATA ADDRESS: ",data
            data.write({"state":"company_strc"})
        return True
    def company_strc(self,cr,uid,ids,context={}):
        for data in self.browse(cr, uid, ids):
            print "DATA STRUCTURE: ",data
            data.write({"state":"shareholder"})
        return True
    def shareholder(self,cr,uid,ids,context={}):
        for data in self.browse(cr, uid, ids):
            print "DATA SHAREHOLDER: ",data
            data.write({"state":"share_owning"})
        return True
    def share_owning(self,cr,uid,ids,context={}):
        for data in self.browse(cr, uid, ids):
            print "DATA SHARE OWNING: ",data
            data.write({"state":"confirm"})
        return True
    
    def _get_image(self, cr, uid, context=None):
        path = os.path.join('base','res','config_pixmaps','%d.png'%random.randrange(1,4))
        image_file = file_data = tools.file_open(path,'rb')
        try:
            file_data = image_file.read()
            return base64.encodestring(file_data)
        finally:
            image_file.close()

    def _get_image_fn(self, cr, uid, ids, name, args, context=None):
        image = self._get_image(cr, uid, context)
        return dict.fromkeys(ids, image) # ok to use .fromkeys() as the image is same for all 

    _columns = {
                'state': fields.selection([
                        ('company_name', 'New Company'),
                        ('company_addr', 'Company Address'),
                        ('company_strc', 'Company Structure'),
                        ('shareholder', 'Shareholders'),
                        ('share_owning', 'Share owning'),
                        ('confirm', 'Confirm'),
                        ],
                        'State', readonly=True, ),
                'company':fields.boolean('Corporate'),
                'config_logo': fields.function(_get_image_fn, string='Image', type='binary', method=True),
                }
    _defaults = {
                 'company': lambda *a: True,
                 'state': lambda * a: 'company_name',
                 'config_logo': _get_image
                 }
res_partner_gbu()