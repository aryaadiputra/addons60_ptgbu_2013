import time
from report import report_sxw
from osv import osv
import reportlab.lib.units
import urllib
import base64
import pooler

class cash_flow_report(report_sxw.rml_parse):
    print "qqqqqqqqqqqqqqq"
    def __init__(self, cr, uid, name, context):
        print "xxxxxxxxxxxxxxxx1234"
        super(cash_flow_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                        'get_move_line': self._get_move_line,
                        'get_cashflow_category': self._get_cashflow_category,
                                   })
    
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
        print "+++++++++++++++++++++++++++++=", data['form']['date_start'], data['form']['date_stop']
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        res = []
        results = []
#        cr.execute("""
#                select id from account_move_line 
#                where move_id in (select move_id from account_move_line 
#                    where account_id in (select id from account_account where type = 'liquidity')) AND
#                account_id not in (select id from account_account where type = 'liquidity') AND
#                (date >= %s AND date <= %s) AND
#                account_id in (select id from account_account WHERE cash_flow_categ = 'payable')
#                """, (data['form']['date_start'], data['form']['date_stop']))

        cr.execute("""
                select a.id, b.cash_flow_categ from account_move_line a, account_account b 
                 WHERE move_id in ( select move_id from account_move_line  where reconcile_id in (select reconcile_id from account_move_line 
                                where move_id in (select move_id from account_move_line 
                                    where account_id in (select id from account_account where type = 'liquidity')) AND
                        
                                account_id in (select id from account_account WHERE reconcile = True) AND
                                reconcile_id is not null
                                AND (date >= %s AND date <= %s)) AND id not in (select id from account_move_line 
                                where move_id in (select move_id from account_move_line 
                                    where account_id in (select id from account_account where type = 'liquidity')) AND
                        
                                account_id in (select id from account_account WHERE reconcile = True) AND
                                reconcile_id is not null
                                AND (date >= %s AND date <= %s)))
                 AND account_id not in (select id from account_account where reconcile = True)
                 AND a.account_id = b.id
                 
                 AND b.sub_cashflow_category_id = %s
                 
                 group by b.cash_flow_categ, a.id
                order by b.cash_flow_categ asc
                 """, (data['form']['date_start'], data['form']['date_stop'], data['form']['date_start'], data['form']['date_stop'], subcateg_id) )
        
        res_ap_ar = map(lambda x: x[0], cr.fetchall())
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>", res_ap_ar
        
        cr.execute("""
                select * from account_move_line a, account_account b 
                    where a.account_id = b.id AND
                    a.move_id in ( 
                        select move_id from account_move_line 
                            where account_id in (select id from account_account where type = 'liquidity') AND
                            account_id not in (select id from account_account where reconcile = True) AND
                            (date >= %s AND date <= %s)
                     ) AND b.reconcile <> True AND
                    b.id not in (select id from account_account where type = 'liquidity')
                    
                    AND b.sub_cashflow_category_id = %s
            """, (data['form']['date_start'], data['form']['date_stop'], subcateg_id))
        res_exp = map(lambda x: x[0], cr.fetchall())
        print '++++++++++++++++++++++++++++++++++', res_exp
        
        res = res_ap_ar + res_exp
        print "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", res
        
        results = db_pool.get('account.move.line').browse(cr, uid, res)
        print "results--------------------------------->>", results
        
        return results
        

report_sxw.report_sxw('report.cash.flow.report', 'account.move.line', 'ad_cash_flow/report/cash_flow_report.mako', parser=cash_flow_report, header=False)
