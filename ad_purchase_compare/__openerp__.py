{
    "name" : "Purchase Compare",
    "version" : "1.0",
    "depends" : ["base","purchase","purchase_requisition"],
    "author" : "Adsoft",
    "description": """Membandingan harga suatu Product antar Supplier, dan menambahkan Payment Terms di Request for Quotation
    Added:
        - Payment Terms
        - Do Merge PO
        - def action_invoice_create di Remove & digantikan dengan yang ada di Module ad_down_payment
        - Required Dest Address
        - Field Payment Method
        - Pindah Field Notes ke Tree
        
    """,
    "website" : "http://www.adsoft.co.id",
    "category" : "Generic/Purchase Compare",
    "init_xml" : [],
    "demo_xml" : [],
    'test': [],
    "update_xml" : [
       "purchase_view.xml",
       "purchase_requisitions_view.xml",
      
    ],
    "active": False,
    "installable": True,
}