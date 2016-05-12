{
    "name" : "Contract Coloring",
    "version" : "1.0",
    "depends" : ["hr_contract", "resource"],
    "author" : "Adsoft",
    "description": """Get this very simple module installed to color your contract tree view.
    Red for exipred contract.
    Black for courrent contract.
    
    Get this module installed also let you warned when you input overlapping date of contract.
    """,
    "website" : "http://www.adsoft.co.id",
    "category" : "Custom/Human Resources",
    'depends': ['hr_contract', 'ad_hr_bsp'],
    "init_xml" : [],
    "demo_xml" : [],
    'test': [],
    "update_xml" : [
       "contract_coloring_view.xml",
#       "resource_view.xml",
       "contract_bsp_view.xml"
    ],
    "active": False,
    "installable": True,
}