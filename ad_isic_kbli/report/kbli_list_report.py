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

class kbli_catelog(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(kbli_catelog, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,

        })
report_sxw.report_sxw('report.kbli.list.report', 'kbli.kbli', 'addons/l10n_id_kbli/report/kbli_list_report.rml', parser=kbli_catelog, header=False)

#report_sxw.report_sxw('report.kbli.list.report', 'kbli.kbli', 'addons/l10n_id_kbli/report/kbli_list_report.rml', header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


