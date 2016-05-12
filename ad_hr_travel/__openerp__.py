{
    "name" : "Travel - Official Journey",
    "version" : "1.0",
    "depends" : ["hr","base","ad_hr_indonesia","hr_attendance"],
    "author" : "Ardhi - Adsoft",
    "description": 
    """This module is created to make Official Journey and generate Official Journey to Invoice.""",
    "website" : "http://www.adsoft.co.id",
    "category" : "Custom/Human Resources",
    "init_xml" : [],
    "demo_xml" : [],
    'test': [],
    "update_xml" : [
       "hr_travel_view.xml",
       "hr_travel_line_view.xml",
       "wizard/hr_travel_order_group.xml"
       
    ],
    "active": False,
    "installable": True,
}