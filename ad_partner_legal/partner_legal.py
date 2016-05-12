from osv import osv, fields

class ir_attachment(osv.osv):
    _inherit    = "ir.attachment"
    _columns={
              'partner_id'       : fields.many2one('res.partner','Related Partner'),
              }
ir_attachment()

class partner_legal(osv.osv):
    _inherit    = "res.partner"
    _columns    = {
                   'isic'           : fields.many2one('kbli.kbli','ISIC'),
                   'document'       : fields.one2many('ir.attachment','partner_id','Document'),
                   'director'       : fields.many2one('hr.employee','Director'),
                   }
partner_legal()