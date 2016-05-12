{
    "name" : "Task Scheduler",
    "version" : "1.0",
    "author" : "ADSOFT",
    "website" : "http://www.adsoft.co.id/",
    "category" : "Added Task Scheduler",
    "depends" : ['hr','ad_hr_bsp','smtpclient','organization_structure'],
    "description": """
        This module aim to create automate task scheduler for several purpose, such as:
        1. Birthday
    """,
    "init_xml": ['employee_birthday.xml',
                 'employee_pensiun.xml',
                 ],
    "update_xml": [
                   # 'employee_mutation.xml',
                   'employee_resign.xml',
                   'data/resign_sequence.xml',
                   'employee_resign_type.xml'],
    "installable": True,
    "active": False,
}