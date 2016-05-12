{
    "name": "costum",
    "version": "1.0",
    "depends": ['account','account_voucher','ad_account_check','base'],
    "author": "ADSOFT",
    "category": "Account Voucher",
    "description": """
        This module aim to add New Payment by Transfer & Cheque
    """,
    "init_xml": [],
    'update_xml': [
        'account_voucher.xml',
        'base_update.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
