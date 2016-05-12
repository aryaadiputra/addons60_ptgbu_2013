from osv import osv, fields

class product_template(osv.osv):
    _inherit = "product.template"
    _description = "Product Template"
    
    _columns = {
        'categ_id': fields.many2one('product.category','Category', required=True, change_default=True, domain="[('type','=','normal')]" ,help="Select category for the current product"),
        }
    def _default_category(self, cr, uid, context=None):
        if context is None:
            context = {}
        if 'categ_id' in context and context['categ_id']:
            return context['categ_id']
        md = self.pool.get('ir.model.data')
        res = False#md.get_object_reference(cr, uid, '', '') or False
        return res and res[1] or False
    
    _defaults = {
        'categ_id' : _default_category,
    }
    
product_template()