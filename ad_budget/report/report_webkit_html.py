import time
import locale
from report import report_sxw
from osv import osv

class report_webkit_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_webkit_html, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'locale': locale,
        })

report_sxw.report_sxw('report.ad_budget.tree_webkit',
                       'ad_budget.item',
                       'addons/ad_budget/report/report_ad_budget_item.mako',
                       parser=report_webkit_html)

