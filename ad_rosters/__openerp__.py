{
    "name" : "Rosters",
    "version" : "1.0",
    "depends" : ["base","hr","hr_attendance"],
    "author" : "Adsoft",
    "description": """Menghitung Jadwl Kerja Rosters
    """,
    "website" : "http://www.adsoft.co.id",
    "category" : "Custom/Rosters Schudule Management",
    "init_xml" : [],
    "demo_xml" : [],
    'test': [],
    "update_xml" : [
       "wizard/extends_view.xml",
       "rosters_view.xml",
       "rosters_type_view.xml",
      
    ],
    "active": False,
    "installable": True,
}