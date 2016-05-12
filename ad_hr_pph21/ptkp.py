from osv import osv,fields
import time

class ptkp_conf(osv.osv):
    _name = "ptkp.conf"
    _columns = {
                'name'          : fields.selection([('tk0','TK/-'),
                                                    ('tk1','TK/1'),
                                                    ('tk2','TK/2'),
                                                    ('tk3','TK/3'),
                                                    ('k0' ,'K/-'),
                                                    ('k1' ,'K/1'),
                                                    ('k2' ,'K/2'),
                                                    ('k3' ,'K/3'),
                                                    ('ki0','K/I/-'),
                                                    ('ki1','K/I/1'),
                                                    ('ki2','K/I/2'),
                                                    ('ki3','K/I/3'),
                                                    ], 'PTKP', required=True),
                'ptkp_amount'   : fields.float('PTKP Amount (monthly)',help="Nontaxable Wages Amount (monthly)"),
                'note'          : fields.text('Note'),
                }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        for ptkp in self.browse(cr, uid, ids, context=context):
            if ptkp.name=="tk0":
                name="TK/-"
            elif ptkp.name=="tk1":
                name="TK/1"
            elif ptkp.name=="tk2":
                name="TK/2"
            elif ptkp.name=="tk3":
                name="TK/3"
            elif ptkp.name=="k0":
                name="K/-"
            elif ptkp.name=="k1":
                name="K/1"
            elif ptkp.name=="k2":
                name="K/2"
            elif ptkp.name=="k3":
                name="K/3"
            elif ptkp.name=="ki0":
                name="K/I/-"
            elif ptkp.name=="ki1":
                name="K/I/1"
            elif ptkp.name=="ki2":
                name="K/I/2"
            elif ptkp.name=="ki3":
                name="K/I/3"
            res.append((ptkp.id, name))
        return res
ptkp_conf()

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    def _get_ptkp(self, cr, uid, ids, name, arg, context):
        result={}
        contract_pool   = self.pool.get('hr.contract')
        ptkp_pool       = self.pool.get('ptkp.conf')
        for e in self.browse(cr,uid,ids):
            contract_id = contract_pool.search(cr,uid,[('employee_id','=',ids[0]),'|',('date_end','>=', time.strftime('%Y-%m-%d')),('date_end','=',False)])
            if len(contract_id)>0:
                contract    = contract_pool.browse(cr,uid,contract_id[0])
                ptkp    = ptkp_pool.search(cr,uid,[('name','=',contract.ptkp)])
                ptkp    = ptkp[0]
            else:
                ptkp    = False 
            result[e.id] = ptkp
        return result
    
    _columns = {
                'ptkp'              : fields.function(_get_ptkp, method=True, type='many2one', relation='ptkp.conf', string='PTKP'),
                }
hr_employee()