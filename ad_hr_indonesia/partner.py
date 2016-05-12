from osv import osv,fields

class res_partner(osv.osv):
    _inherit        = "res.partner"
    _columns        = {
                       'employee'       : fields.boolean('Employee',help='Check this box if the partner is an employee'),
                       }
res_partner()