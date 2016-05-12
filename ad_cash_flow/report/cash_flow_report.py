import time
from report import report_sxw
from osv import osv
import reportlab.lib.units
import urllib
import base64
import pooler
import datetime, dateutil.parser

class cash_flow_report(report_sxw.rml_parse):
    print "qqqqqqqqqqqqqqq"
    def __init__(self, cr, uid, name, context):
        print "xxxxxxxxxxxxxxxx1234"
        super(cash_flow_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                        'get_data' : self._get_data,
                        'get_move_line': self._get_move_line,
                        'get_move_line_partial': self._get_move_line_partial,
                        'get_cashflow_category': self._get_cashflow_category,
                        'get_cash_beginning' : self._get_cash_beginning,
                                   })
        
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
    
    def _get_cashflow_category(self, data):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        
        search = db_pool.get('cash.flow.category').search(cr, uid, [])
        browse = db_pool.get('cash.flow.category').browse(cr, uid, search)
        return browse
    
    def _get_cashflow_subcategory(self, parent_id):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        
        search = db_pool.get('sub.category.line').search(cr, uid, [('category_id','=',parent_id)])
        browse = db_pool.get('sub.category.line').browse(cr, uid, search)
        return browse
    
    def _get_move_line(self,data, subcateg_id):
        #print "+++++++++++++++++++++++++++++=", data['form']['date_start'], data['form']['date_stop']
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        res = []
        results = []

        cr.execute("""
        select a.id, b.sub_cashflow_category_id, a.move_id from account_move_line a, account_account b 
                 WHERE move_id in ( select move_id from account_move_line  where reconcile_id in (select reconcile_id from account_move_line 
                                where move_id in (select move_id from account_move_line 
                                    where account_id in (select id from account_account where type = 'liquidity')) AND
                        
                                account_id in (select id from account_account WHERE reconcile = True and ar_ap = True) AND
                                reconcile_id is not null
                                AND (date >= %s AND date <= %s)) AND id not in (select id from account_move_line 
                                where move_id in (select move_id from account_move_line 
                                    where account_id in (select id from account_account where type = 'liquidity')) AND
                        
                                account_id in (select id from account_account WHERE reconcile = True and ar_ap = True) AND
                                reconcile_id is not null
                                AND (date >= %s AND date <= %s)))
                 AND a.account_id not in (select id from account_account where type = 'liquidity' or ar_ap = True)
                 AND a.account_id = b.id
                 
                 AND b.sub_cashflow_category_id = %s

UNION

select a.id, b.sub_cashflow_category_id, a.move_id from account_move_line a, account_account b where a.move_id in 
    (
    select move_id from account_move_line 
    where account_id in (select id from account_account where type = 'liquidity')
    
    AND move_id in (select move_id from account_move_line 
        where account_id in (select id from account_account WHERE ar_ap = True)
        )
    
    AND date >= %s AND date <= %s
    )
    AND a.account_id = b.id
    AND a.account_id not in (select id from account_account where type = 'liquidity')
    AND a.account_id not in (select id from account_account WHERE ar_ap = True)
    AND b.sub_cashflow_category_id = %s
    
    
UNION

select a.id, b.sub_cashflow_category_id, a.move_id from account_move_line a, account_account b 
                    where a.account_id = b.id AND
                    a.move_id in ( 
                        select move_id from account_move_line 
                            where account_id in (select id from account_account where type = 'liquidity') AND
                            account_id not in (select id from account_account WHERE ar_ap = True) AND
                            (date >= %s AND date <=  %s)
                     ) AND b.id not in (select id from account_account where type = 'liquidity')
                    AND a.account_id not in (select id from account_account WHERE ar_ap = True)
                    AND b.sub_cashflow_category_id = %s

UNION

select z.id, b.sub_cashflow_category_id, z.move_id from account_move_line z, account_account b
    where z.account_id in (select acc.id from account_account acc where acc.type='liquidity')
    and z.move_id not in (select move_id from account_move_line where account_id 
    not in ((select acc.id from account_account acc where acc.type='liquidity')))
    AND z.account_id = b.id
    AND z.date >= %s AND z.date <= %s
    AND b.sub_cashflow_category_id = %s
    AND z.account_id not in (select id from account_account WHERE ar_ap = True)
    
        """
        , (
              data['form']['date_start'], data['form']['date_stop'], data['form']['date_start'], data['form']['date_stop'], subcateg_id, 
              data['form']['date_start'], data['form']['date_stop'], subcateg_id,
              data['form']['date_start'], data['form']['date_stop'], subcateg_id, 
              data['form']['date_start'], data['form']['date_stop'], subcateg_id
              ))

        res = map(lambda x: x[0], cr.fetchall())
        res = list(set(res))
        results = db_pool.get('account.move.line').browse(cr, uid, res)
        #print "results--------------------------------->>", results
        
        return results
    
    def _get_cash_beginning(self, data):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        res = []
        results = []
        
        print "data['form']['date_start']", data['form']['date_start']
        
        cr.execute(""" 
                    select sum(a.debit-a.credit) as amount from account_move_line a, account_account b 
                        where a.date < '%s'
                        AND a.account_id in (select id from account_account where type = 'liquidity')
                        AND a.account_id = b.id
                    """% (data['form']['date_start']))
        
        results = cr.fetchone()[0]
        
        return results
    
    def _get_move_line_partial(self,data):
        print "+++++++++++++++++++++++++++++=", data['form']['date_start'], data['form']['date_stop']
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        res = []
        results = []
        dict = {}
        
        cr.execute("""
        
        select move_id, reconcile_partial_id from account_move_line a, account_account b 
            WHERE move_id in 
            (
            select move_id from account_move_line a, account_account b 
            WHERE a.account_id in (select id from account_account where type = 'liquidity')
            AND a.account_id = b.id
            AND date >= %s AND date <= %s
            )
            AND a.account_id in (select id from account_account where reconcile = True) 
            AND a.account_id = b.id
            AND reconcile_partial_id is not null
    
        """, (data['form']['date_start'], data['form']['date_stop']))

        #res = map(lambda x: x[0], cr.fetchall())
        fetch = cr.fetchall()
        
        for m in fetch:
            print "11111111111111", m[0]
            print "22222222222222", m[1]
            dict = {
                'move_line_id'          : m[0],
                'reconcile_partial_id'  : m[1]
                    }
            
        res.append(dict)
        print "yyyyyyyyyyyyyyyyyyyy", res
        #results = db_pool.get('account.move.line').browse(cr, uid, res)
        #print "results--------------------------------->>123", results
        
        return results
        


report_sxw.report_sxw('report.cash.flow.report', 'account.move.line', 'ad_cash_flow/report/cash_flow_report.mako', parser=cash_flow_report, header=False)
