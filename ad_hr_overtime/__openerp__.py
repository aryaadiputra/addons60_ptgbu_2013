{
    "name" : "Overtime Submission",
    "version" : "1.0",
    "depends" : ["hr","hr_attendance"],
    "author" : "Adsoft",
    "description": """This module is aimed to handle overtime submission.
    """,
    "website" : "http://www.adsoft.co.id",
    "category" : "Custom/Human Resources",
    "init_xml" : [],
    "demo_xml" : [],
    'test': [],
    "update_xml" : [
       "hr_overtime_view.xml",
       "report/print_overtime_recapitulation_view.xml",
    ],
    "active": False,
    "installable": True,
}