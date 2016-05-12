{
    "name" : "Task Scheduler",
    "version" : "1.0",
    "author" : "ADSOFT",
    "website" : "http://www.adsoft.co.id/",
    "category" : "Added Task Scheduler",
    "depends" : ['base','project','document'],
    "description": """
        This module aim to create automate task scheduler from documents expired
    """,
    "init_xml": ['task_scheduler.xml'],
    "update_xml": [
        'document_view.xml'
    ],
    "installable": True,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
