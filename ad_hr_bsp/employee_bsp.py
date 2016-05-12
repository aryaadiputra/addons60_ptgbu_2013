from osv import osv
from osv import fields
import time

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _columns = {
                'no_ktp'        : fields.char('No.KTP', size=20, help="Nomor Kartu Tanda Penduduk"), 
                'gol'           : fields.char('Golongan', size=20, help="Golongan Karyawan"),
                'no_pekerja'    : fields.char('No.Pekerja', size=20, help="Nomor Pekerja Karyawan"),
                'work_location' : fields.selection([('pekanbaru','Pekanbaru'),
                                                    ('pedada','Pedada'),
                                                    ('west','West Area'),
                                                    ('jakarta','Jakarta')], 'Office Location'),
                'non_active'    : fields.boolean('Non Active'),
                'is_staff'      : fields.boolean('Staff'),
                'non_staff'     : fields.boolean('Non Staff'),
                'type'          : fields.selection([('bob','Rosters'),
                                                    ('bsp','Head Office')], 'Placement'),
                'rosters_type_id'    : fields.many2one('rosters.schedule.type','Rosters Type'),
                'nik_bob'       : fields.char('NIK OnSite', size=20, help="NIK untuk pegawai OnSite"),
                'doj_bob'       : fields.date('TMT OnSite'),
                'doj'           : fields.date('TMT Head Office'),
                'status'        : fields.selection([('contract','Karyawan PKWT (Kontrak)'),
                                                    ('permanent','Karyawan PKWTT (Permanen)'),
                                                    ('outsource','Karyawan Outsource')],
                                                   'Employement Status', help="PWT = Perjanjian Waktu Tertentu\nPKWTT = Perjanjian Kerja Waktu Tidak Tertentu"),
                'section'       : fields.many2one('hr.section','Division'),
                'kasie'         : fields.related('section', 'chief_id', relation='hr.employee', string='Kasie', type='many2one', store=True, select=True, readonly=True, help="It is linked with leader of a Section"),
                
                'pension_acc'   : fields.many2one('account.account','Pension Account'),
                }
    
    def onchange_active(self,cr,uid,ids,active,non_active):
        val={}
        if active:
            if non_active:
                val['non_active']=False
        return {'value':val}
    def onchange_non_active(self,cr,uid,ids,active,non_active):
        val={}
        if non_active:
            if active:
                val['active']=False
        return {'value':val}
    def onchange_staff(self,cr,uid,ids,staff,non_staff):
        val={}
        if staff:
            if non_staff:
                val['non_staff']=False
        return {'value':val}
    def onchange_non_staff(self,cr,uid,ids,staff,non_staff):
        val={}
        if non_staff:
            if staff:
                val['is_staff']=False
        return {'value':val}

hr_employee()
