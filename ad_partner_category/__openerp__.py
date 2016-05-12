{
    "name" : "Create Company Wizard",
    "version" : "2.0",
    "depends" : ["base","document"],
    "author" : "ADSOFT",
    "category": 'Company/Custom',
    "description": "Modul ini dibuat untuk menyajikan pembuatan sebuah perusahaan dalam bentuk wizard.",
    'website': 'http://www.adsoft.co.id',
    'init_xml': [],
    'update_xml': [
                   "partner_category_view.xml",
                   "partner_template_view.xml",
    ],
    'demo_xml': [
                 "partner_category_demo.xml",
                 ],
    'installable': True,
    'active': False,
    'certificate' : '',
}