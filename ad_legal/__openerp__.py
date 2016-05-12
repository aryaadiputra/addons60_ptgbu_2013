{
    "name" : "Legal",
    "version" : "1.0",
    "depends" : ["base","document","email_template","hr","base_contact","ad_task_scheduler","ad_partner_category","account"],
    "author" : "ADSOFT",
    "category": 'Generic Modules/Legal Document',
    "description": "Modul ini dibuat untuk mengelola dokumen legal perusahaan. Modul ini akan membuat struktur direktori dokumen legal sebuah perusahaan.",
    'website': 'http://www.adsoft.co.id',
    'init_xml': [],
    'update_xml': [
        'security/legal_security.xml',
        'security/ir.model.access.csv',
        'res_partner_view.xml',
        'legal_view.xml',
        'menu_manager_view.xml',
        'res_partner_contact_view.xml'
    ],
    'demo_xml': ['legal_demo.xml'],
    'installable': True,
    'active': False,
    'certificate' : '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
