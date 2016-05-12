# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "ISIC (Indonesian Standard Industrial Classification)",
    "version": "1.0",
    "author": "ADSOFT",
    "category": "Localisation/Indonesian Standard Industrial Classification",
    "website": "http://www.adsoft.co.id",
    "description": """
    This module aims to manage:
    KBLI (Klasifikasi Baku Lapangan Usaha Indonesia)
    or
    ISIC (Indonesian Standard Industrial Classification)
    """,
    'depends': ['base'],
    'init_xml': [],
    'update_xml': [
        'kbli_common_report.xml',
        'kbli_view.xml',
        'kbli_report.xml',
        ],
    'demo_xml': ['demo/kbli_demo.xml'
        ],
    'test': ['test/test_hr.yml'],
    'installable': True,
    'active': False,
    'certificate': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
