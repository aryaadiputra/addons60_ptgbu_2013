{
    'name': 'Payment Order',
    'version': '3.0',
    'category': 'Custom Procurement (PTGBU)/Payment Order',
    'description': """
     - Filter Supplier Invoice by Payment Date
     
       """,
    'author': 'ADSOFT',
    'depends': ['base','account', 'account_payment', 'ad_acc_inv_double_validation'],
    'update_xml': [
        
        "account_payment_view.xml",
        "account_invoice_workflow.xml"
        
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}