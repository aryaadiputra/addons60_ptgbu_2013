{
    'name': 'Human Resources for Indonesia',
    'version': '1.0',
    "category": "Localisation/Human Resources",
    "website": "http://www.adsoft.co.id",
    "description": """
    This module aim to adopt hr modules for use in Indonesia
      adding field : 
           - KTP
           - NPWP
           - Insurance
           - Religion
           - Family
           - address
           - education
       adding report :
           - CV
     
    """,
    'author': 'ADSOFT',
    'depends': ['base','hr','hr_payroll','hr_expense'],
    'update_xml': [
        'hr_ktp_view.xml',
        'hr_npwp_view.xml',
        'hr_jamsostek_view.xml',
        'hr_religion_view.xml',
        'data/hr_religion_data.xml',
        'hr_family_job_view.xml',
        'hr_family_view.xml',
        'hr_experience_view.xml',
        'hr_cv_report.xml',
        'employee_job_view.xml',
        'hr_education_view.xml',
        'hr_address_view.xml',
        'hr_payroll_declare_view.xml',
        'hr_extension_view.xml',
        'hr_view.xml',
        'wizards_view.xml',
        'expenses_structure_view.xml',
        'hr_family_relation.xml',
        'hr_expense_view.xml',
#<<<<<<< TREE
#        'hr_pensiun_view.xml',
#        'hr_family_job_view.xml',
        'partner_view.xml',
        'wizard/hr_expense_generate_invoice_view.xml'
#=======
#        'hr_pensiun_view.xml',
#>>>>>>> MERGE-SOURCE
    ],
    'demo_xml': [
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}