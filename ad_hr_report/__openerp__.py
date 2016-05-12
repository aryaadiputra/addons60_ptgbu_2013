{
    "name" : "HR Reporting",
    "version" : "1.0",
    "depends" : [
                 "hr",
                 "base",
                 "hr_payroll",
                 "ad_hr_holiday_year",
                 "ad_hr_bsp",
                 "hr_attendance",
                 "ad_hr_overtime",
                 "hr_payroll_account"
                 ],
    "author" : "Adsoft",
    "description": """This module is aimed to create Employees Reporting.
    """,
    "website" : "http://www.adsoft.co.id",
    "category" : "Custom/Human Resources",
    "init_xml" : [],
    "demo_xml" : [],
    'test': [],
    "update_xml" : [
            "report_view.xml",
            "wizard_view.xml",
            "attendance_report_view.xml",
    ],
    "active": False,
    "installable": True,
}