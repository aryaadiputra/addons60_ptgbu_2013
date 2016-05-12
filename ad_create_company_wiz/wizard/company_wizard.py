from osv import fields
from osv import osv
import wizard
import pooler
from tools.translate import _
import ir
#call(["ls", "-l"])

view1="""<?xml version="1.0"?>
<form string="Create New Company Wizard">
    <group colspan="4" width="600" height="250">
        <label string="This form allows you to fill the information about the company you want to input" colspan="2" />
        <separator colspan="4" /><newline />
        <field name="name" /><newline/>
        <field name="lang" /> <newline /> <newline />
        
        <separator string="Category" colspan="4" /><newline />
        <field colspan="4" name="category" nolabel="1" />
    </group>
</form>
"""

view2="""<?xml version="1.0"?>
<form string="Legal Document">
    <group colspan="4" width="1000" height="300">
        <field name="address" colspan="4" nolabel="1" />
    </group>
</form>
"""

view3="""<?xml version="1.0"?>
<form string="Company Structure">
    <group colspan="4" width="1000" height="300">
        <field name="job_structure" colspan="4" nolabel="1" />
    </group>
</form>
"""

view4="""<?xml version="1.0"?>
<form string="Shareholders">
    <group colspan="4" width="1000" height="300">
        <field name="shareholds" colspan="4" nolabel="1" />
    </group>
</form>
"""

view5="""<?xml version="1.0"?>
<form string="Comfirmation">
    <group colspan="4" width="300">
        <label string="The new company has been saved. You can do some adjustment to the company in menu \n Corporates >> Directories >> Companies" colspan="4" />
    </group>
</form>
"""

fields1={
    "name" : {
        "type" : "char",
        "string" : "Company Name",
        "required" : True,
        "size" : 1024,
    },
    "lang" : {
        "type" : "selection",
        "selection" : [("en_US","English"),("id_ID","Bahasa Indonesia")],
        "string" : "Language",
        "help" : "If the selected language is loaded in the system, all documents related to this partner will be printed in this language. If not, it will be english."
    },
    "category" : {
        "type" : "many2many",
        "relation" : "res.partner.category",
        "string" : "Categories",
    }
}

fields2 = {
    "address" : {
        "type" : "one2many",
        "relation" : "res.partner.address",
        "string" : "Address",
    },
}

fields3={
    "job_structure" : {
        "type" : "one2many",
        "relation" : "res.partner.job",
        "string" : "Partner Function",
    },
}

fields4 = {
    "shareholds" : {
        "type" : "many2many",
        "relation" : "res.partner.shareholders",
        "string" : "Shareholders",
    },
}

class company_wizard(wizard.interface):
    _inherit = 'res.partner'
    
    def _init(self,cr,uid,data,context):
        return {
            "name" : "",
            "lang" : "en_US",
        }

    def _new_address(self,cr,uid,data,context):
        print "DATA ADDRESS :", data
        form = data['form']['address']
        print "FORM : ",form
        if len(form)!=0:
            addr = form[0][2]
            print "ADDRESS : ",addr
            pool = pooler.get_pool(cr.dbname)
            pool.get('res.partner.address').create(cr,uid,addr)
        return{}
    
    def _new_company(self,cr,uid,data,context):
        
        form = data['form']
        print "FORM:",form,"\n"
        company_name = form['name']
        language = form['lang']
        
        category = form['category'][0]
        categories = category[2]
#        categories0 = categories[0] 
        print "Company Name : ",company_name
        print "category",category
        print "categories",categories
#        print "categories0",categories0
        
        company = {'name' : company_name,
                   'company' : True,
                   'lang' : language,
        }
        pool = pooler.get_pool(cr.dbname)
        pool.get('res.partner').create(cr,uid,company)
        
        self.idpartner = pool.get('res.partner').search(cr,uid,[('name','=',company_name)])[0]
        pool = pooler.get_pool(cr.dbname)
        
#        sql = "insert into res_partner_address(partner_id) values('"+str(self.idpartner)+"')"
#        cr.execute(sql)
        if categories:
            for cat_id in categories:
                data = {
                        'partner_id':self.idpartner,
                        'category_id':cat_id,
                        }
                x = data['partner_id']
                sql="insert into res_partner_category_rel(partner_id,category_id) values ('"+str(x)+"','"+str(cat_id)+"')"
                print "SQL : ",sql
                cr.execute(sql)
        return {}
    
    def _new_structure(self,cr,uid,data,context):
        print "DATA",data
        form = data['form']['job_structure']
        print "FORM :",form
#        job_structure = form[0]
#        print "JOB STRUCTURE:",job_structure
        print "LENGTH FORM[0]",len(form)
        if len(form)!=0:
            structure = form[0][2]
            print "STRUCTURE :",structure
            structure['function_id'] = self.idpartner
            print "NEW STRUCTURE :", structure
            pool = pooler.get_pool(cr.dbname)
            pool.get('res.partner.job').create(cr,uid,structure)
        return {}
    
    def _new_shareholds(self,cr,uid,data,context):
        print "SHAREHOLDS DATA : ",data
        shareholds = data['form']['shareholds'][0][2]
        print "SHAREHOLDS : ",shareholds
        if shareholds:
            for share in shareholds:
                data = {
                        'partner_id':self.idpartner,
                        'shareholder_id':share,
                        }
                sql="insert into shareholders_rel(partner_id,shareholder_id) values('"+str(data['partner_id'])+"','"+str(share)+"')"
                print "SQL : ", sql
                cr.execute(sql)
        return {}
    
    def _save(self,cr,uid,data,context):
        print "save"
        return True

    states={
        "init": {
            "actions": [_init],
            "result": {
                "type": "form",
                "arch": view1,
                "fields": fields1,
                "state": [("end","Cancel"),("address","Save & Next")],
            },
        },
        "address": {
            "actions": [_new_company],
            "result": {
                "type": "form",
                "arch": view2,
                "fields": fields2,
                "state": [("company_skip","Skip"),("company","Save & Next")],
            },
        },
        "company_skip": {
            "actions": [],
            "result": {
                "type": "form",
                "arch": view3,
                "fields": fields3,
                "state": [("structure_skip","Skip"),("structure","Save & Next")],
            }
        },
        "company": {
            "actions": [_new_address],
            "result": {
                "type": "form",
                "arch": view3,
                "fields": fields3,
                "state": [("structure_skip","Skip"),("structure","Save & Next")],
            }
        },
        "structure_skip": {
            "actions": [],
            "result": {
                "type": "form",
                "arch": view4,
                "fields": fields4,
                "state": [("confirm","Skip"),("save","Save & Next")],
            }
        },
        "structure": {
            "actions": [_new_structure],
            "result": {
                "type": "form",
                "arch": view4,
                "fields": fields4,
                "state": [("confirm","Skip"),("confirm","Save & Close")],
            }
        },
        "confirm": {
            "actions": [_new_shareholds],
            "result": {
                "type": "form",
                "arch": view5,
                "fields": fields3,
                "state": [("end","OK")],
            }
        },
#        "save": {
#            "actions": [_new_shareholds],
#            "result": {
#                "type": "action",
#                "action": _save,
#                "state": "end",
#            }
#        },
    }
company_wizard("new.company.wizard")