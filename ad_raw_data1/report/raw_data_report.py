import time
from report import report_sxw
from osv import osv
import reportlab.lib.units
import urllib
import base64
import pooler
import datetime, dateutil.parser
from dateutil.relativedelta import relativedelta
from datetime import datetime
import calendar

class raw_data_report(report_sxw.rml_parse):
    print "qqqqqqqqqqqqqqq"
    def __init__(self, cr, uid, name, context):
        #print "xxxxxxxxxxxxxxxx1234"
        super(raw_data_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                        'get_data' : self._get_data,
                        'get_move_line': self._get_move_line,
                        'get_budget_line': self._get_budget_line,
                        'get_create_date_move_line' : self._get_create_date_move_line,
                        'get_current_date_start' : self._get_current_date_start,
                        #'start_day_of_month' : self._start_day_of_month,
                        'last_day_of_month' : self._last_day_of_month,
                        'get_periods' : self._get_periods,
                                   })
    
    def _get_periods(self, data):
        cr, uid = self.cr, self.uid
        periods = ""
        cr.execute("select name from account_period where id = %s" % data['form']['period_start'])
        period_start = cr.fetchone()[0]
        
        cr.execute("select name from account_period where id = %s" % data['form']['period_end'])
        period_end = cr.fetchone()[0]
        
        periods     = period_start +" s/d "+ period_end
        print "periods>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.", periods
        
        return periods
    
    def _start_day_of_month(self, data, date):
        print "date", date
        """return the date (as a string) of the last day of the month"""
        cr, uid = self.cr, self.uid
        cr.execute("select date_start from account_period where id = %s" % data['form']['period_end'])
        year = '2013'
        
        today = year + date
        today = datetime.strptime(today, '%Y-%m-%d')
        
        print "today????????????????????????", today
        
        return today
    
    def _last_day_of_month(self, data, date):
        print "date", date
        """return the date (as a string) of the last day of the month"""
        cr, uid = self.cr, self.uid
        cr.execute("select date_start from account_period where id = %s" % data['form']['period_end'])
        val = {}
        year = '2013'
        
        
        # where are we now? 
        #today = datetime.date.today()
        today = year + date
        today = datetime.strptime(today, '%Y-%m-%d')
        print "xxxxxxxxxxxxxxxxxxxxx", today.date()
        
        
        # get next month. 
        # force us into the middle of the month 
        # so we don't need to deal with edge cases. 
        x,y = calendar.monthrange(today.year,today.month)
        
        # now force us to the beginning of next month minus one day
#        eom = datetime.date(nm.year, nm.month, 1) - datetime.timedelta(days=1)
        print "HHHHHHHHHHHHHHHHHHHHH"
        start_month = today.date().strftime('%Y-%m-%d')
        print "start_month>>>>>>>>>>>>>>>>", start_month
        end_month   = '%s-%s-%s' % (today.year, today.month, y)
        
        print type(start_month), type(end_month)
        
        
        val = {
            'start_month'   : start_month,
            'end_month'     : end_month
               }
        
        return val
    
    def _get_current_date_start(self, data):
        cr, uid = self.cr, self.uid
        cr.execute("select date_start from account_period where id = %s" % data['form']['period_end'])
        current_date_start = cr.fetchone()[0]
        return current_date_start
    
    def _get_current_date_end(self, data):
        cr, uid = self.cr, self.uid
        cr.execute("select date_stop from account_period where id = %s" % data['form']['period_end'])
        current_date_end = cr.fetchone()[0]
        return current_date_end
        
    def _get_data(self,data):
        date_start  = dateutil.parser.parse(data['form']['date_start'])
        date_stop   = dateutil.parser.parse(data['form']['date_stop'])
        
        result_date_start   = date_start.strftime('%d-%b-%y')
        result_date_end     = date_stop.strftime('%d-%b-%y')
        
        result_date = {
                  'result_date_start'   : result_date_start,
                  'result_date_end'     : result_date_end,
                  }
        return result_date
 
    def _get_move_line(self,data):
        #print "+++++++++++++++++++++++++++++=", data['form']['date_start'], data['form']['date_stop']
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        res = []
        results = []
        cr.execute("select date_start from account_period where id = %s" % data['form']['period_start'])
        date_start = cr.fetchone()[0]
        
        cr.execute("select date_stop from account_period where id = %s" % data['form']['period_end'])
        date_end = cr.fetchone()[0]
        
        cr.execute("""
            select * from account_move_line where date >= %s and date <= %s
    
        """, (
              date_start, date_end
              ))

        res = map(lambda x: x[0], cr.fetchall())
        
        #print "RES_________________>>", res
        
        results = db_pool.get('account.move.line').browse(cr, uid, res)
        
        return results
    
    
    def _get_budget_line(self,data):
        #print "+++++++++++++++++++++++++++++=", data['form']['date_start'], data['form']['date_stop']
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        res = []
        results = []

        cr.execute("""
            select id from ad_budget_line where amount != 0.0
    
                    """)

        res = map(lambda x: x[0], cr.fetchall())
        
        results = db_pool.get('ad_budget.line').browse(cr, uid, res)
        #print "results++++++++++++++++++++++++++++++++++++", results
        return results
    
    def _get_create_date_move_line(self, id):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        res = []
        results = []
        
        cr.execute('select create_date from account_move_line where id = %s', (id,))
        
        res = map(lambda x: x[0], cr.fetchall())
        
        #print "RES---------------->>", res[0]
        return res[0]
        
    
    def _get_create_date_budget(self, id):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        res = []
        results = []
        
        cr.execute('select create_date from ad_budget_line where id = %s', (id,))
        
        res = map(lambda x: x[0], cr.fetchall())
        
        return res[0]
        
    
report_sxw.report_sxw('report.raw.data.report', 'account.move.line', 'ad_raw_data/report/raw_data_report.mako', parser=raw_data_report, header=False)
