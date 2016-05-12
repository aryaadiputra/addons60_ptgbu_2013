{
    'name': 'Account Payment Extention Unreconciled Default',
    'version': '3.0',
    'category': 'Account Payment',
    'description': """
     Membuat Filter Unreconciled Aktif sebagai Default     
       """,
    'author': 'ADSOFT',
    'depends': ['base',"account","account_payment","account_payment_extension"],
    'update_xml': [
        "payment_view.xml",
        
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}