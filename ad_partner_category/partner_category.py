from osv import osv
from osv import fields


class partner_category(osv.osv):
    _name = "partner.category"
    _description = 'Partner Category'
    _columns = {
                'name':fields.char('Category',size=128),
                'partner_template' : fields.many2one('partner.template','Related Company Template'),
#                'directory_structure':fields.char('Struktur',size=128,required=True),
                'directory_str':fields.one2many('document.directory','category_id','Directory Structure'),
                }
partner_category()

class document_directory(osv.osv):
    _inherit = "document.directory"
    _description = 'Directory'
    _columns = {
                'category_id':fields.many2one('partner.category','Company Category'),
                }
document_directory()

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
                'partner_category':fields.many2one('partner.category','Category'),
                }
res_partner()