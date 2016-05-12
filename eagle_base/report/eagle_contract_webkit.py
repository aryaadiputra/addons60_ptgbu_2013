import time
from report import report_sxw
from osv import osv

class eagle_contract_webkit(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(eagle_contract_webkit, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
        
report_sxw.report_sxw('report.webkiteagle.contract',
                       'eagle.contract', 
                       'addons/eagle_base/report/eagle_contract_webkit.mako',
                       parser=eagle_contract_webkit)
