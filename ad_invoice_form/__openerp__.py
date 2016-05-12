{
    "name": "ADSOFT",
    "version": "1.0",
    "depends": ["base","account","ad_amount2text_idr"],
    "author": "Adsoft",
    "category": "Custom GBU/ Invoice Form",
    "description": """
    This module provide :
    Create Purchase Order Form
    
    Wekit Setting:
        - /usr/local/bin/wkhtmltopdf
    """,
    "init_xml": [],
    'update_xml': [
                   "invoice_form_view.xml",
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}