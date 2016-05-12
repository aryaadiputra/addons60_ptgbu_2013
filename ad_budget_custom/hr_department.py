from osv import fields, osv
import tools

class hr_department(osv.osv):
    _inherit = 'hr.department'
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            
            res.append((record['id'], name))
        return res
    
    _columns = {
            'division_id': fields.many2one('hr.division', 'Division'),  
                }
hr_department()