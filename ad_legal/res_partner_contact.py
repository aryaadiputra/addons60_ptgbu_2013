from osv import osv
from osv import fields

class res_partner_contact(osv.osv):
    _inherit = "res.partner.contact"
    _columns = {
                'ktp'           : fields.binary("KTP"),
                'npwp'          : fields.binary("NPWP"),
                'shareowning'   : fields.one2many('res.partner.shareholders','contact','Shareowning'),
                }
res_partner_contact()