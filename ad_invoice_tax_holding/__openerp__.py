{
    'name': 'Supplier Invoice Taxes',
    'version': '3.0',
    'category': 'Supplier Invoice Taxes',
    'description': """
     Supplier Invoice Taxes apart
         Added :
         - DP Sbg Pengurang AP
       """,
    'author': 'ADSOFT',
    'depends': ['base','account'],
    'update_xml': [
        "account_view.xml",
        "account_invoice_view.xml",
        
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}