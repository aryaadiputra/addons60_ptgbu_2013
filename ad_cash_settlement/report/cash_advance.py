import time
from report import report_sxw
from osv import osv
import reportlab.lib.units
import urllib
import base64
import pooler
from datetime import datetime 

class cash_advance(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(cash_advance, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                        'get_object': self._get_object,
                        'change_format_date':self._change_format_date,
                                   })

    def _get_object(self,data,context=None):
        # print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",data['model']
        # print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",data['id_cash']
        # if context is None:
        #     context = {}
        # advance_ids=self.pool.get(data['model']).search(self.cr,self.uid,[('state','!=','posted')])
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,data['id_cash'])
        # print "obj_dataaaaaaaaa",obj_data
        return obj_data

    def _change_format_date(self,date):
        if date == False:
            new_date = ""
        else:
            date_format = datetime.strptime(date, '%Y-%m-%d')
            # print "dateeeeeee2", date_format
            date_format = date_format.strftime('%d/%m/%Y')
            # print "dateeeeeee1", date_format
            new_date = date_format
        return new_date

report_sxw.report_sxw('report.print.cash.advance', 'cash.advance', 'ad_cash_settlement/report/cash_advance.mako', parser=cash_advance, header=False)
