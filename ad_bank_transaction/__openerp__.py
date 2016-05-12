{
    "name" : "Bank Transaction",
    "version" : "1.0",
    "depends" : ["base",'account'],
    "author" : "ADSOFT",
    "website" : "http://adsoft.co.id/",
    "description": """
This module add a feature for bank transaction.
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "security/ir.model.access.csv",
                    "bank_transaction_view.xml",
                    ],
    "active": False,
    "installable": True,
}
