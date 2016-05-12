from osv import osv,fields

class form_f1a(osv.osv):
    _name       = "form.f1a"
    _columns    = {
                   'name'                   : fields.many2one('hr.employee','Nama Lengkap Tenaga Kerja',required=True),
                   'jamsostek_member'       : fields.boolean('Peserta Jamsostek?', help="Apakah sebelumnya Anda sudah menjadi peserta Jamsostek?"),
                   'type'                   : fields.selection([('baru','Pendaftaran Baru'),
                                                                ('edit','Perubahan Data')],
                                                               'Type ', required=True),
                   'company_name'           : fields.many2one('res.partner','Nama Perusahaan',required=True),
                   'nik'                    : fields.char('NIK', size=16, help='Nomor Induk Perusahaan'),
                   'nuk'                    : fields.char('NUK', size=16, help='Nama Unit Kerja'),
                   'kuk'                    : fields.char('KUK', size=16, help='Kode Unit Kerja'),
                   'tempat_lahir'           : fields.char('Tempat Lahir', size=32),
                   'tanggal_lahir'          : fields.date('Tanggal Lahir'),
                   'pendidikan'             : fields.selection([('sd','SD'),
                                                                ('smp','SMP'),
                                                                ('sma','SMA'),
                                                                ('d3','D3'),
                                                                ('s1','S1'),
                                                                ('s2s3','S2/S3'),],
                                                               'Pendidikan Terakhir'),
                   'gender'                 : fields.selection([('male','Laki-laki'),
                                                                ('female','Perempuan'),],
                                                               'Jenis Kelamin'),
                   'gol_darah'              : fields.selection([('o','O'),
                                                                ('a','A'),
                                                                ('b','B'),
                                                                ('ab','AB')],
                                                               'Golongan Darah'),
                   'marital'                : fields.selection([('belum','Belum Menikah'),
                                                                ('sudah','Sudah Menikah'),],
                                                               'Status Pernikahan'),
                   'identitas'              : fields.selection([('ktp','KTP'),
                                                                ('paspor','Paspor'),],
                                                               'Identitas Diri'),
                   'kewarganegaraan'        : fields.many2one('res.country','Kewarganegaraan'),
                   'id_number'              : fields.char('Nomor Identitas Diri', size=20),
                   'expiry'                 : fields.date('Berlaku s/d'),
                   'npwp'                   : fields.char('NPWP', size=16),
                   'mother'                 : fields.char('Nama Ibu Kandung',size=64),
                   'alamat'                 : fields.many2one('res.partner.address','Alamat',help='Sesuai identitas diri'),
                   'city'                   : fields.char('Kota', size=32),
                   'zip'                    : fields.char('Kode Pos', size=5),
                   'alamat_surat'           : fields.many2one('res.partner.address','Alamat Surat Menyurat'),
                   'city_surat'             : fields.char('Kota', size=32),
                   'zip_surat'              : fields.char('Kode Pos', size=5),
                   'telepon_rumah'          : fields.char('No. Telepon Rumah', size=21),
                   'telepon_kantor'         : fields.char('No. Telepon Kantor', size=21),
                   'ext'                    : fields.char('Ext.', size=5),
                   'mobile'                 : fields.char('No. HP', size=21),
                   'email'                  : fields.char('Alamat Email', size=32),
                   'surat_menyurat'         : fields.selection([('mail','Alamat Surat Menyurat'),
                                                                ('email','Alamat Email'),],
                                                               'Surat Menyurat ke'),
                   'akun_bank'              : fields.many2one('res.partner.bank','Nomor Rekening Bank'),
                   'nama_bank'              : fields.many2one('res.bank','Nama Bank'),
                   'branch'                 : fields.char('Cabang', size=32),
                   'pemilik'                : fields.char('Atas Nama', size=32),
                   'keluarga'               : fields.one2many('hr.family','res_id','Keluarga'),
                   'bpu'                    : fields.char('Balai Pengobatan Umum', size=32),
                   'bpg'                    : fields.char('Balai Pengobatan Gigi', size=32),
                   'rb'                     : fields.char('Rumah Bersalin', size=32),
                   }
    _defaults   = {
                   'type'                   : 'baru',
                   'identitas'              : 'ktp',
                   }
    def onchange_employee(self, cr, uid, ids, data):
        if data:
            employee    = self.pool.get('hr.employee').browse(cr,uid,data)
            print employee.family_id
            married =['married','sudah menikah','menikah','berkeluarga']
            
            if employee.marital:
                if employee.marital.name.lower() in married:
                    marital='sudah'
                else:
                    marital='belum'
            else:
                marital=False
                
            fam_id=[]
            if employee.family_id:
                for data in employee.family_id:
                    fam_id.append(data.id)
            
            val = {
                   'nik'            : employee.nik,
                   'npwp'           : employee.npwp,
                   'company_name'   : employee.company_id.partner_id.id,
                   'tanggal_lahir'  : employee.birthday,
                   'gender'         : employee.gender,
                   'gol_darah'      : employee.gol,
                   'kewarganegaraan': employee.country_id.id,
                   'id_number'      : employee.no_ktp,
                   'marital'        : marital,
                   'keluarga'       : fam_id
                   }
            print val
        return {'value':val}
        
form_f1a()