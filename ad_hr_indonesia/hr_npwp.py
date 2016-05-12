from osv import osv, fields
from tools.translate import _

class hr_employee(osv.osv):
    ''' inherited hr.employee '''
    _inherit = "hr.employee"
    _columns = {
        'npwp' : fields.char('NPWP No', size=20, required=False, help="Indonesian Tax Registration Number e.g 01.855.081.4-005.000"),
              }

    def onchange_format_npwp(self, cr, uid, ids, npwp):

        if len(npwp) == 0:
            return True

        warning = {
            "title": _("Bad NPWP format !"),
            "message": _("The NPWP format should be like this '01.855.081.4-005.000' or '018550814005000'")
        }

        if len(npwp) not in (15,20):
            return {'warning': warning}

        if len(npwp)==15:
            try:
                int(npwp)
            except:
                return {'warning': warning}
        
        if len(npwp)==20:
            try:
                int(npwp[:2])
                int(npwp[3:6])
                int(npwp[7:10])
                int(npwp[11:12])
                int(npwp[13:16])
                int(npwp[-3:])
            except:
                return {'warning': warning}

        vals = {}
        if len(npwp)==15:
            formatted_npwp = npwp[:2]+"."+npwp[2:5]+"."+npwp[5:8]+"."+npwp[8:9]+"-"+npwp[9:12]+"."+npwp[12:15]
            vals={
                "npwp" : formatted_npwp
            }
            return {"value": vals}

        return {"value": vals}

    def _check_npwp(self,cr,uid,ids,context=None):
        """npwp = self.browse(cr, uid, ids[0], context=context).npwp
        if not npwp:
            return True

        if len(npwp) not in (15,20):
            return False

        if len(npwp)==15:
            try:
                int(npwp)
            except:
                return False
        
        if len(npwp)==20:
            try:
                int(npwp[:2])
                int(npwp[3:6])
                int(npwp[7:10])
                int(npwp[11:12])
                int(npwp[13:16])
                int(npwp[-3:])
            except:
                return False
        
        if npwp[2:3] not in '.':
            return False
        if npwp[6:7] not in '.':
            return False
        if npwp[10:11] not in '.':
            return False
        if npwp[12:13] not in '-':
            return False
        if npwp[16:17] not in '.':
            return False"""
        return True
    
    _constraints = [
        (_check_npwp, _("Bad NPWP format ! \nThe NPWP format should be like this '01.855.081.4-005.000' or '018550814005000'"), ['npwp'])
        ]

hr_employee()
