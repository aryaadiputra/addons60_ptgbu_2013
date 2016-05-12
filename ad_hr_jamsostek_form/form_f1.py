from osv import osv,fields

class form_f1(osv.osv):
    _name   = "form.f1"
    _columns= {
               'name'               : fields.many2one('res.partner','Nama Perusahaan', required=True),
               'address'            : fields.many2one('res.partner.address','Alamat', required=True),
               'city'               : fields.char('Kota',size=32, required=True),
               'zip'                : fields.char('Kode Pos',size=16, required=True),
               'regency'            : fields.char('Kabupaten',size=32, required=True),
               'com_phone1'         : fields.char('No. Telepon',size=16, required=True,help="Sertakan kode area daerah perusahaan, kemudian pisahkan dengan tanda'-'."),
               'com_phone2'         : fields.char('No. Telepon 2',size=16,help="Sertakan kode area daerah perusahaan, kemudian pisahkan dengan tanda'-'."),
               'com_fax'            : fields.char('No. Fax',size=16, required=True),
               'com_status'         : fields.selection([('pusat','Pusat'),
                                                        ('cabang','Cabang'),
                                                        ('anak','Anak Perusahaan'),
                                                        ('cabang_anak','Cabang Anak Perusahaan')],
                                                       'Status Perusahaan', required=True),
               'com_corporation'    : fields.many2one('res.partner.title','Bentuk Badan Hukum', required=True),
               'business_license'   : fields.char('Nomor Ijin Usaha',size=64, required=True),
               'business_type'      : fields.many2one('kbli.kbli','Jenis Usaha Utama', required=True),
               'npwp'               : fields.char('NPWP',size=16, required=True),
               'ownership'          : fields.selection([('sn','Swasta Nasional'),
                                                        ('sa','Swasta Asing'),
                                                        ('bumn','BUMN'),
                                                        ('bumd','BUMD'),
                                                        ('koperasi','Koperasi'),
                                                        ('jv','Joint Venture'),
                                                        ('yayasan','Yayasan')],
                                                       'Kepemilikan', required=True),
               
               'com_contact'        : fields.many2one('res.partner.contact','Nama Lengkap', required=True),
               'position'           : fields.char('Jabatan',size=16, required=True),
               'com_contact_phone'  : fields.char('No. Telepon',size=16, required=True,help="Sertakan kode area daerah perusahaan, kemudian pisahkan dengan tanda'-'."),
               'com_contact_ext'    : fields.char('Ext',size=8),
               'com_contact_mobile' : fields.char('No. HP',size=16),
               'com_contact_fax'    : fields.char('No. Fax',size=16),
               'com_contact_email'  : fields.char('Email address',size=32),
               
               'ho_npp'             : fields.char('NPP Kantor Pusat',size=16),
               'ho_name'            : fields.many2one('res.partner','Nama Perusahaan'),
               'ho_address'         : fields.many2one('res.partner.address','Alamat Perusahaan'),
               'ho_city'            : fields.char('Kota',size=32),
               'ho_zip'             : fields.char('Kode Pos',size=8),
               'ho_regency'         : fields.char('Kabupaten',size=32),
               'ho_phone1'          : fields.char('No. Telepon',size=16,help="Sertakan kode area daerah perusahaan, kemudian pisahkan dengan tanda'-'."),
               'ho_phone2'          : fields.char('No. Telepon 2',size=16,help="Sertakan kode area daerah perusahaan, kemudian pisahkan dengan tanda'-'."),
               
               'program'            : fields.selection([('paket1','Jaminan Kecelakaan Kerja\nJaminan Hari Tua\nJaminan Kematian\nJaminan Pemeliharaan Kesehatan'),
                                                        ('paket2','Jaminan Kecelakaan Kerja\nJaminan Hari Tua\nJaminan Kematian'),
                                                        ('paket3','Jaminan Kecelakaan Kerja\nJaminan Kematian')],
                                                       'Program yang diikuti', required=True),
               'member_since'       : fields.date('Menjadi peserta sejak',required=True),
               'total_employee'     : fields.integer('Jumlah Tenaga Kerja',required=True),
               'salary_amount'      : fields.integer('Jumlah upah sebulan', required=True), 
               }
    def onchange_company(self, cr, uid, ids, data):
        if data:
            print data
            partner = self.pool.get('res.partner').browse(cr,uid,data)
            print partner
            addr    =  partner.address[0]
            val = {
                   'address'        : addr.id,
                   'city'           : addr.city,
                   'zip'            : addr.zip,
                   'com_phone1'     : addr.phone,
                   'com_fax'        : addr.fax,
                   'com_corporation': partner.title.id,
                   'business_type'  : partner.isic.id,
                   }
            print val
        return {'value':val}
    
    def onchange_contact(self, cr, uid, ids, data):
        if data:
            contact = self.pool.get('res.partner').browse(cr,uid,data)
            addr    =  partner.address[0]
            val = {
                   'address'        : addr.id,
                   'city'           : addr.city,
                   'zip'            : addr.zip,
                   'com_phone1'     : addr.phone,
                   'com_fax'        : addr.fax,
                   'com_corporation': partner.title.id
                   }
        return {'value':val}
form_f1()