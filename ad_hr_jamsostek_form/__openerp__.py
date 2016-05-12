{
    "name" : "Jamsostek Form",
    "version" : "1.0",
    "depends" : ["hr","base","base_contact","ad_hr_jamsostek","ad_isic_kbli","ad_partner_legal"],
    "author" : "Adsoft",
    "description": """This module is aimed to handle overtime submission.
    """,
    "website" : "http://www.adsoft.co.id",
    "category" : "Generic Jamsostek Module",
    "init_xml" : [],
    "demo_xml" : [],
    'test': [],
    "update_xml" : [
       "hr_jamsostek_form_view.xml",
       "form_f1_view.xml",
       "form_f1a_view.xml",
       "form_f2a_view.xml",
       "report/print_form_f1_view.xml",
       "report/print_form_f2a_view.xml",
    ],
    "active": False,
    "installable": True,
}