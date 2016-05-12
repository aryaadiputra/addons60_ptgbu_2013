{
    "name": "ADSOFT",
    "version": "1.0",
    "depends": [
                "base", 
                "account", 
                "account_voucher",
                "ad_payment_adm",
                "ad_down_payment",
                ],
    "author": "Adsoft",
    "category": "Invoice",
    "description": """ Modul ini digunakan untuk menambah field pajak rate pada form currency""",
    "init_xml": [],
    'update_xml': [
                   "pajak_rate_view.xml",
                   "account_invoice_view.xml",
                   "account_voucher_view.xml",
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
