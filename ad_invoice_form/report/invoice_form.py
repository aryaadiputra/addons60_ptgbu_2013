import time
from report import report_sxw
from osv import osv,fields
from report.render import render
#from ad_num2word_id import num2word
import pooler
#from report_tools import pdf_fill,pdf_merge
from tools.translate import _
import tools
from tools.translate import _
import decimal_precision as dp
from ad_amount2text_idr import amount_to_text_id
from tools import amount_to_text_en
import datetime

class invoice_form(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(invoice_form, self).__init__(cr, uid, name, context=context)
        if self.pool.get('account.invoice').browse(cr, uid, context['active_ids'])[0].state == 'draft':
            raise osv.except_osv(_('Can not Invoice Form !'), _('You can not Print Invoice Form If State not Approved'))
        
        self.line_no = 0
        self.localcontext.update({
            'get_object':self._get_object,
            'time': time,
            'get_process_date' : self.get_process_date,
            'amount_remain' : self._amount_remain,
            'compute_lines' : self.compute_lines,
            #'convert':self.convert,
            #'get_company_address': self._get_company_address,
            #'convert':self.convert,
            #'charge':self.charge,
            #'line_no':self._line_no,
            #'blank_line':self.blank_line,
            #'blank_line_rfq':self.blank_line_rfq,
            #'get_grand_total':self.get_grand_total,
        }) 
    
#    def get_budget(self, invoice_id, account_analytic_id):
#        obj_budget_inv = self.pool.get('budget.info.inv')
#        obj_budget_inv._amount_remain(self.cr, self, uid, )
##        search = obj_budget_inv.search(self.cr, self.uid, [('invoice_id','=',invoice_id), ('account_analytic_id','=',account_analytic_id)])
##        if search:
##            obj_budget_inv.browse(self.cr, self.uid, search)[0].
##                
#        
#        return res

    def get_process_date(self,):
        process_date        = datetime.datetime.today().strftime('%d-%b-%y')
        return process_date
    
    def compute_lines(self, id, method, context=None):
        print "DDDDDDDDDDDDDDDDDDDDDDDD", method
        result = {}
        
        cr  = self.cr
        uid = self.uid
        ids = [id]
        for invoice in self.pool.get('account.invoice').browse(cr, uid, ids, context=context):
            src = []
            lines = []
            if invoice.move_id:
                for m in invoice.move_id.line_id:
                    temp_lines = []
                    if m.reconcile_id:
                        temp_lines = map(lambda x: x.id, m.reconcile_id.line_id)
                    elif m.reconcile_partial_id:
                        temp_lines = map(lambda x: x.id, m.reconcile_partial_id.line_partial_ids)
                    lines += [x for x in temp_lines if x not in lines]
                    src.append(m.id)
                    
            
            lines = filter(lambda x: x not in src, lines)
            result[invoice.id] = lines
        print "result------------------------->>", lines
        print "yyyyyyyyyyyyy", id
        cr.execute("SELECT voucher_id FROM account_voucher_line WHERE invoice_id in (%s)" %(id))
        
        voucher_id = map(lambda x:x[0],cr.fetchall())
        
        for i in self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=context):
            if i.payment_adm == method:
                return 'checked = "checked"'
            
            else:
                return ""
        #print "xxxxxxxxxxxxxx", voucher_id, a
        
        #return result
    
    def _amount_remain(self, account_analytic_id, invoice_id, date_end):
            res={}
            budget_remain = 0.0
            if not account_analytic_id or not date_end:
                return budget_remain
        #for line in self.browse(cr, uid, ids, context=None):
            #account_analytic_id = line.account_analytic_id.id
            #invoice_id = line.invoice_id.id
            #date_end = line.invoice_id.date_invoice[:4]
            #acc_ids = line.budget_item_id.
            print "account_analytic_id, invoice_id, date_end", account_analytic_id, invoice_id, date_end
            cr = self.cr
            cr.execute("SELECT SUM(amount) as balance_real FROM account_analytic_line "
                   "WHERE account_id=%s AND to_char(date,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_real = cr.fetchone()
            amount_real = amount_real[0] or 0.00
            
            cr.execute("select sum(a.amount) as amount_budget from ad_budget_line a, account_period b "
                       " where a.analytic_account_id = %s and a.period_id = b.id and to_char(b.date_start,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            amount_budget = cr.fetchone()
            amount_budget = amount_budget[0] or 0.00
            
            #===================================================================
            # cr.execute("SELECT SUM(x.product_qty*x.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y "
            #        " WHERE x.state in ('approved','confirmed','done') and x.order_id = y.id and "
            #        " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
            #            " where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('confirmed','approved','done') and b.state not in ('open','paid','cancel')) and a.id=y.id) and "
            #           " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            # amount_spent = cr.fetchone()
            # amount_spent = amount_spent[0] or 0.00
            #===================================================================
            cr.execute("select SUM(x.product_qty*x.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y "
                        " where y.state in ('approved') and x.order_id = y.id "
                        "  and x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ", (str(account_analytic_id),str(date_end),))
            amount_virtual1 = cr.fetchone()
            amount_virtual1 = amount_virtual1[0] or 0.00
            
            cr.execute("SELECT SUM(a.product_qty*a.price_unit) as balance_virtual FROM purchase_order_line x, purchase_order y, stock_move a "
                     " WHERE x.order_id = y.id and a.purchase_line_id = x.id and a.state in ('cancel','done') and "
                     " x.order_id in (select a.id from purchase_order a, account_invoice b, purchase_invoice_rel c "
                       "  where a.id=c.purchase_id and b.id= c.invoice_id and (a.state in ('approved') and b.state in ('open','paid','cancel')) and a.id=y.id) and "
                       " x.account_analytic_id = %s and to_char(x.date_planned,'yyyy') = %s ",(str(account_analytic_id),str(date_end),))
            amount_virtual2 = cr.fetchone()
            amount_virtual2 = amount_virtual2[0] or 0.00
            amount_spent = amount_virtual1 - amount_virtual2
            #res[line['id']] = amount_spent
            #===================================================================
            cr.execute("select sum((a.quantity * a.price_unit) - (a.quantity * a.price_unit) * a.discount / 100) from account_invoice c, account_invoice_line a, budget_info_inv b "
                       " where c.id=a.invoice_id and a.invoice_id = %s and a.account_analytic_id=b.account_analytic_id and b.account_analytic_id = %s and c.id = b.invoice_id and to_char(c.date_invoice,'yyyy') = %s and c.state = 'draft'",(invoice_id,str(account_analytic_id),str(date_end),))
            
            amount1 = cr.fetchone()
            amount1 = amount1[0] or 0.00
            
#            cr.execute(" select sum(e.subtotal) from purchase_order a, purchase_requisition b, stock_picking c, material_requisition d, material_requisition_line e, budget_info f "
#                       " where a.requisition_id = b.id and b.int_move_id = c.id and c.material_req_id = d.id and a.state in ('done','approved') "
#                       " and d.id = f.material_req_id  and e.account_analytic_id = f.account_analytic_id and d.id = e.requisition_id "
#                       " and e.requisition_id = %s and f.account_analytic_id = %s and to_char(d.date_end,'yyyy') = %s ",(material_req_id,str(account_analytic_id),str(date_end),))
#            amount2 = cr.fetchone()
#            amount2 = amount2[0] or 0.00    
            amount2 = 0.00
            amount_current = amount1 - amount2
            #print amount1,amount2,amount_current,amount_budget - (amount_spent + amount_current + abs(amount_real))
            #===================================================================
            #res[line['id']] = amount_budget - (amount_spent + amount_current + abs(amount_real))
            budget_remain = amount_budget - (amount_spent + amount_current + abs(amount_real))
            return budget_remain
    
    def get_grand_total(self,total,chargeline):
        gt=0
        charge=0
        for line in chargeline:
            charge=+line.amount
        gt=charge+total
        return gt
    
    def charge(self,line):
        cost=0
        for line in line:
            cost=+line.amount
        return cost
    
    def convert(self, amount, cur):
        amt_en = amount_to_text_en.amount_to_text(amount, 'en', cur)
        return amt_en
    
    def _get_object(self,data):
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['id']])
        #seq=obj_data[0].print_seq
        #seq+=1
        #obj_data[0].write({'print_seq':seq})
        return obj_data
        
    def blank_line(self, nlines):
        row = len(nlines)
        
        res = ""
        
        if row < 15:
            for i in range(15 - row):
                res = res + ('<tr> <td class="row_line_left">&nbsp;</td> <td class="row_line" colspan="2">&nbsp;</td><td class="row_line">&nbsp;</td><td class="row_line">&nbsp;</td><td class="row_line">&nbsp;</td><td class="row_line_right">&nbsp;</td></tr>')

        return res
    
    def blank_line_rfq(self, nlines):
        row = len(nlines)
        
        res = ""
        
        if row < 15:
            for i in range(15 - row):
                res = res + ('<tr> <td class="row_line_left">&nbsp;</td> <td class="row_line" colspan="2">&nbsp;</td> <td class="row_line">&nbsp;</td> <td class="row_line">&nbsp;</td> </tr>')

        return res
        
    def _get_company_address(self, company):
        partner = company.partner_id.id
        address_id = self.pool.get('res.partner.address').search(self.cr,self.uid,[('partner_id','=',partner)])
        address = self.pool.get('res.partner.address').browse(self.cr,self.uid,address_id[0])
        
        return address
        
    def _line_no(self):
        self.line_no = self.line_no + 1
        return self.line_no
    
    def _blank_line(self, nlines, row, type):
        res = ""
        if type=="IDR":
            if row > 1:
                for i in range(nlines+1):
                    res = res + ('<tr class="sub_line"><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>')
            else:
                for i in range(nlines - row):
                    res = res + ('<tr class="sub_line"><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>')
        else:
            if row > 1:
                for i in range(nlines+1):
                    res = res + ('<tr class="sub_line"><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>')
            else:
                for i in range(nlines - row):
                    res = res + ('<tr class="sub_line"><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>')

        return res

    
    def no_urut(self, list, value):
        return list.index(value) + 1
        


                   
report_sxw.report_sxw('report.invoice.form', 'account.invoice', 'ad_invoice_form/report/invoice_form.mako', parser=invoice_form,header=False)


