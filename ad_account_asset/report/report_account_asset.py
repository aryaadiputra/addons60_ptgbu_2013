import time
from report import report_sxw
from osv import osv
import pooler

class account_asset(report_sxw.rml_parse):

   def __init__(self, cr, uid, name, context):
        super(account_asset, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time
        }) 

#report_sxw.report_sxw('report.report.all.asset', 'account.asset.asset', 'ad_report_asset_bsp/report/report_all_asset.rml', parser=account_asset, header=False)
report_sxw.report_sxw('report.report.per.asset', 'account.asset.asset', 'ad_account_asset/report/report_per_asset.rml', parser=account_asset, header=False)
report_sxw.report_sxw('report.report.label.asset', 'account.asset.asset', 'ad_account_asset/report/report_label_asset.rml', parser=account_asset, header=False)