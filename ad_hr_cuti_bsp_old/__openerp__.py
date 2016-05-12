{
    "name" : "Modul cuti untuk BSP",
    "version" : "1.0",
    "depends" : ["base","hr","ad_hr_bsp","hr_holidays","report_webkit"],
    "author" : "Adsoft",
    "description": """Modul ini digunakan untuk menyimpan data cuti karyawan BSP selain cuti bersama dan cuti tahunan seperti:
1. Cuti melahirkan
2. Cuti sakit
3. Cuti khitanan anak
4. Cuti babtisan anak 
    """,
    "website" : "http://www.adsoft.co.id",
    "category" : "Custom/Human Resources",
    "init_xml" : [],
    "demo_xml" : [],
    'test': [],
    "update_xml" : [
       "outstanding_leave_view.xml",
       "wizard/wizard_report.xml",
    ],
    "active": False,
    "installable": True,
}