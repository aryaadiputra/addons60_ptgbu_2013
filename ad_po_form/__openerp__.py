{
    "name": "ADSOFT",
    "version": "1.0",
    "depends": ["purchase","ad_amount2text_idr","ad_purchase_compare","ad_second_uom"],
    "author": "Adsoft",
    "category": "Custom GBU/ Purchase Order Form",
    "description": """
    This module provide :
    Create Purchase Order Form
    
    Added :
        - Blank Line
    
    Wekit Setting:
        - /usr/local/bin/wkhtmltopdf
    """,
    "init_xml": [],
    'update_xml': [
                   "purchase_view_report.xml",
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}