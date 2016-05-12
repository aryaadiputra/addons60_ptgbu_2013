{
    'name': 'Material Request GBU',
    'version': '3.0',
    'category': 'Custom Procurement/Material Request',
    'description': """
     - Material Request
     - Create Internal Move Record 
     - Approval Budget & Non Budget  
     - Approval warehouse di Remove 
     - Perbaikan Fungsi
     - Perbaikan Serching Budget
     - Many2many Historical PR
     - Tracking Status
       """,
    'author': 'ADSOFT',
    'depends': ['base','stock','purchase_requisition','ad_pr_double_validation','ad_budget'],
    'update_xml': [
        "security/access_security.xml",
        "material_req_view.xml",
        "material_sequence.xml",
        "workflow.xml",
        "stock_view.xml",
        "purchase_requisition_view.xml",
        "res_users_view.xml",
        "email_scheduler.xml",
        "hr_department_view.xml",
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}
