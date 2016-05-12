{
    "name" : "PPh 21",
    "version" : "1.0",
    "depends" : ["hr","base","hr_payroll","ad_hr_holiday_year","ad_hr_overtime","hr_payroll_account"],
    "author" : "Adsoft",
    "description": """This module is aimed to handle PPh 21 (Indonesian income tax) calculation for each employees.
    """,
    "website" : "http://www.adsoft.co.id",
    "category" : "Custom/Human Resources",
    "init_xml" : [],
    "demo_xml" : [],
    'test': [],
    "update_xml" : [
       "ptkp_view.xml",
       "pph21_view.xml",
       "res_company_view.xml",
       "data/ptkp.xml",
    ],
    "active": False,
    "installable": True,
}