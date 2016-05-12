{
    'name': 'Module Purchase Order',
    'version': '1.0',
    'category': 'Custom/PT.Gunung Bara Utama',
    'description': """
    Modul ini dibuat agar Quantity tidak boleh lebih dari Quantity PR.    
       """,
    'author': 'ADSOFT',
    'depends': ['base', 'purchase','hr','purchase_requisition'],
    'update_xml': [
        'purchase_view.xml',
        'purchase_requisition_view.xml',
        
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}