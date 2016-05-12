{
    "name" : "Supplier Invoice",
    "version" : "1.0",
    "depends" : ["base","account",],
    "author" : "Adsoft",
    "description": """Tambahan Approval pada Supplier Invoice
    """,
    "website" : "http://www.adsoft.co.id",
    "category" : "Custom/Supplier Invoice",
    "init_xml" : [],
    "demo_xml" : [],
    'test': [],
    "update_xml" : [
       "invoice_view.xml",
       "invoice_workflow.xml",
    ],
    "active": False,
    "installable": True,
}