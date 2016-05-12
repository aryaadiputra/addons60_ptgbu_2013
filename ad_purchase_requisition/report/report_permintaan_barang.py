##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import time
from report import report_sxw
from osv import osv
import pooler
import datetime

class requisition(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(requisition, self).__init__(cr, uid, name, context=context)
        self.line_no = 1
        self.localcontext.update({
            'time': time,
            'nourut': self.no_urut,
            'line_no':self._line_no,
            'blank_line':self._blank_line,
        }) 
    
    def no_urut(self, list, value):
        return list.index(value) + 1
    
    def _blank_line(self, nlines):
        res = ""
        for i in range(nlines - self.line_no):
            res = res + '\n'
        return res

    # generat line number   
    def _line_no(self):
        self.line_no = self.line_no + 1
        return self.line_no
    
report_sxw.report_sxw('report.permintaan.barang', 'purchase.requisition', 'addons/ad_purchase_requisition/report/report_permintaan_barang.rml', parser=requisition, header=False)
report_sxw.report_sxw('report.permintaan.barang2', 'purchase.requisition', 'addons/ad_purchase_requisition/report/report_permintaan_barang2.rml', parser=requisition, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
