{
    "name": "Email Invoice",
    "version": "1.0",
    "depends": ['base','account','zb_task_emails'],
    "author": "ADSOFT",
    "category": "Email Invoice Scheduler",
    "description": """
        This module aim to send invoice automatic scheduler via email
    """,
    "init_xml": [],
    'update_xml': [
        'state_users.xml',
        'email_scheduler.xml'
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
