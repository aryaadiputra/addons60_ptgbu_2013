{
    "name" : "Budget Reporting Custom",
    "version" : "0.1",
    "author" : "ADSOFT",
    "category" : "Generic Modules/Accounting-Budget",
    "website" : "http://www.openerp.co.id",
    "description": """ Reporting for budget.
    """,
    "depends" : ["account","ad_budget"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["budget_utilization_view.xml",
                    "budget_utilization_report.xml"],
    "active": False,
    "installable": True,
}
