{
    'name': 'Human Resources BSP',
    'version': '3.0',
    'category': 'Human Resources',
    'description': """
     - Surat Keterangan Perjalanan Dinas
     - Surat Perintah Tugas    
       """,
    'author': 'ADSOFT',
    'depends': ['hr','hr_expense','ad_hr_indonesia','hr_payroll','hr_timesheet',],
    'update_xml': [
        "hr_contract_available_view.xml",
        "hr_memorandum_view.xml",
        "hr_association_view.xml",
        "hr_rate_view.xml",
        "hr_department_view.xml",
        "medical_history_view.xml",
        "employee_bsp_view.xml",
        "hr_section_view.xml",
        "medical_history_view.xml",
        "hr_payroll_view.xml",
        "hr_evaluation_view.xml",
        
    ],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}