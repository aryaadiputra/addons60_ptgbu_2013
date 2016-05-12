{
    'name': 'Supplier Invoice i',
    'version': '3.0',
    'category': 'Supplier Invoice',
    'description': """
     Supplier Invoice Double Validation, Added Create Record Date 
       """,
    'author': 'ADSOFT',
    'depends': ['base','account'],
    'update_xml': [
        "security/access_security.xml",
        "supplier_invoice_double_validation_installer.xml",
        "account_voucher_pay_invoice.xml",
        "account_invoice_view.xml",
        "account_invoice_workflow.xml",
        
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}