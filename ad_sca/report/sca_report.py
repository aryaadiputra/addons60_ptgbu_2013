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
import datetime
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
from dateutil import parser

class sca_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sca_report, self).__init__(cr, uid, name, context=context)

        self.line_no = 0
        self.localcontext.update({
            'get_purchase_order':self._get_purchase_order,
            'get_purchase_order2':self._get_purchase_order2,
            'get_purchase_order3':self._get_purchase_order3,
            'get_purchase':self._get_purchase,
            'get_purchase2':self._get_purchase2,
            'get_purchase3':self._get_purchase3,
            'get_po':self._get_po,
            'get_po_approve':self._get_po_approve,
            'get_object':self._get_object,
            'time': time,
            'convert':self.convert,
            'get_company_address': self._get_company_address,

        }) 
        
  
    def _get_purchase_order(self, data):
        print "11111111111111111111111111111111111111111"
        po = self.pool.get('purchase.order').browse(self.cr, self.uid, data)
        print "po-------------->>", po
        return po
    
    def _get_purchase_order2(self, data):
        
        po = self.pool.get('purchase.order').browse(self.cr, self.uid, data)
        
        return po
    
    def _get_purchase_order3(self, data):
        
        po = self.pool.get('purchase.order').browse(self.cr, self.uid, data)
        
        return po

    def get_six_monthes(self):
        now = time.strftime('%Y-%m-%d')
        now = now.split('-')
        year = int(now[0])
        month = int(now[1])-6
        if month==0:
            month=1
        elif month==-1:
            month=12
            year-=1
        elif month==-2:
            month=11
            year-=1
        elif month==-3:
            month=10
            year-=1
        elif month==-4:
            month=9
            year-=1
        elif month==-5:
            month=8
            year-=1
        date = int(now[2])
        
        six_month = datetime.date(year,month,date)
        self.cr.execute("SELECT DATE(CURRENT_DATE - INTERVAL '6 months') as dateorder")
        six_month = self.cr.fetchone()[0]
        six_month = parser.parse(six_month).date()
        return six_month
    
    def _get_purchase(self, data):
#        hasil = []
#        unit_price_search = self.pool.get('purchase.order.line').search(self.cr, self.uid, [('product_id','=',data),('order_id.state','=','draft')])
#        unit_price_browse = self.pool.get('purchase.order.line').browse(self.cr, self.uid, unit_price_search)
#        for x in unit_price_browse:
#            print "wwwwwwwwww", x.id 
#            hasil.append(x.id)
#            
        #query = "select min(price_unit) from purchase_order_line where product_id =" +str(data)+ "and state='confirmed'"
        query = "select min(price_unit) from purchase_order_line pol, purchase_order po where pol.order_id = po.id and po.state='done' and pol.product_id =" +str(data)+ ""
        print "Purchase ---------------123>>", self.cr.execute(query)
        
        unit_price = self.cr.fetchone()[0]
        print "unit_price:", unit_price
        line_search = self.pool.get('purchase.order.line').search(self.cr, self.uid, [('price_unit','=',unit_price),('product_id','=',data),('order_id.state','=',"done")])
        line_browse = self.pool.get('purchase.order.line').browse(self.cr, self.uid, line_search)
        
        for a in line_browse:
            print "========================",a.product_qty
        a = "arya"
        print "line_browse=================>>", line_browse
        print 'data1=======================',data
        if len(line_browse)<>0:
            return line_browse[0]
            #return False
        else:
            return False
    
    def _get_purchase2(self, data):
        result = []
        print 'dataxx',data
        
        product_line_search = self.pool.get('purchase.order.line').search(self.cr, self.uid, [('product_id','=', data)] )
        product_line_browse = self.pool.get('purchase.order.line').browse(self.cr, self.uid, product_line_search )
        
        for x in product_line_browse:
            print "ddd::", x.order_id.id
            #print "Price :", x.price_unit
            order_search = self.pool.get('purchase.order').search(self.cr, self.uid, [('id','=', x.order_id.id), ('state','=',"done")])
            order_browse = self.pool.get('purchase.order').browse(self.cr, self.uid, order_search )
            
            for y in order_browse:
                result.append(y.date_order)
            print 'result==============>>>>>>>>>.',result
            #result.append(x.price_unit)
        print "Result 1:", result
        last_date = max(result)
        print "Result 2:", last_date
        
        #po_id = self.pool.get('purchase.order').search(self.cr, self.uid, [('date_order','=',last_date)])
        po_id = self.pool.get('purchase.order').search(self.cr, self.uid, [('date_order','=',last_date), ('state','=',"done")])
        ###############DIganti Temp tapi haru di cek kembali################
        #po_id = self.pool.get('purchase.order').search(self.cr, self.uid, [('date_order','=',last_date), ('state','!=',"done")])
        
        po_line_search = self.pool.get('purchase.order.line').search(self.cr, self.uid, [('order_id','in',po_id),('product_id','=',data)])[-1]
        po_line_browse = self.pool.get('purchase.order.line').browse(self.cr, self.uid, po_line_search)
        print 'po_line_browse',po_line_browse
        
        return po_line_browse
    
    def convert_to_date(self,tanggal):
        t=tanggal.split('-')
        tanggal=datetime.date(int(t[0]),int(t[1]),int(t[2]))
        return tanggal
    
    def _get_purchase3(self, data):
        print "tttt"
        result = []
        product_line_search = self.pool.get('purchase.order.line').search(self.cr, self.uid, [('product_id','=', data),('order_id.state','=','done')] )
        product_line_browse = self.pool.get('purchase.order.line').browse(self.cr, self.uid, product_line_search )
        for x in product_line_browse:
            order_search = self.pool.get('purchase.order').search(self.cr, self.uid, [('id','=', x.order_id.id),('state','=','done')])
            order_browse = self.pool.get('purchase.order').browse(self.cr, self.uid, order_search )
            for y in order_browse:
                if self.convert_to_date(y.date_order)>self.get_six_monthes():
                    print "qqqqqqqqqqqqqqqqqq"
                    result.append(y.date_order)
                ########Temporer#########
                else:
                    result.append(y.date_order)
        print "Result :", result
        ids=[]
        for res in result:
            po_id2 = self.pool.get('purchase.order').search(self.cr, self.uid, [('date_order','=',res),('state','=','done')])
            po_line_search2 = self.pool.get('purchase.order.line').search(self.cr, self.uid, [('order_id','in',po_id2),('product_id','=',data), ('order_id.state','=','done')])
            ids.append(po_line_search2[0])
            #print "IDS:****************************", ids 
        po_line_browse2 = self.pool.get('purchase.order.line').browse(self.cr, self.uid, ids)
        print "po_line_browse2:::", po_line_browse2
        cheapest=9999999999999999999
        line_browse = False
        for line in po_line_browse2:
            if line.price_unit<cheapest:
                print "line.price_unit :", line.price_unit,"VS",cheapest
                cheapest=line.price_unit
                line_browse=line
        return line_browse
    
#    def _get_purchase3(self, data):
#        print "tttt"
#        result = []
#        product_line_search = self.pool.get('purchase.order.line').search(self.cr, self.uid, [('product_id','=', data)] )
#        product_line_browse = self.pool.get('purchase.order.line').browse(self.cr, self.uid, product_line_search )
#        for x in product_line_browse:
#            order_search = self.pool.get('purchase.order').search(self.cr, self.uid, [('id','=', x.order_id.id)])
#            order_browse = self.pool.get('purchase.order').browse(self.cr, self.uid, order_search )
#            for y in order_browse:
#                if self.convert_to_date(y.date_order)>self.get_six_monthes():
#                    result.append(y.date_order)
#        print "Result :", result
#        ids=[]
#        for res in result:
#            po_id2 = self.pool.get('purchase.order').search(self.cr, self.uid, [('date_order','=',res)])
#            po_line_search2 = self.pool.get('purchase.order.line').search(self.cr, self.uid, [('order_id','in',po_id2),('product_id','=',data)])
#            ids.append(po_line_search2[0])
#            #print "IDS:****************************", ids 
#        po_line_browse2 = self.pool.get('purchase.order.line').browse(self.cr, self.uid, ids)
#        print "po_line_browse2:::", po_line_browse2
#        cheapest=9999999999999999999
#        for line in po_line_browse2:
#            if line.price_unit<cheapest:
#                print "line.price_unit :", line.price_unit,"VS",cheapest
#                cheapest=line.price_unit
#                line_browse=line
#        return line_browse

    def _get_po(self,data):
        print "xxxxxxxxxx", data
        a = self.pool.get('purchase.order').search(self.cr,self.uid,[('origin','like',data),('state','!=',"cancel")])
        b = self.pool.get('purchase.order').browse(self.cr,self.uid,a)
        print "ccccxxxxxxxxx",b
        return b
    
    def _get_po_approve(self,data):
        print "xxxxxxxxxx", data
        a = self.pool.get('purchase.order').search(self.cr,self.uid,[('origin','like',data),('state','!=',"cancel"),('state','!=',"draft")])
        b = self.pool.get('purchase.order').browse(self.cr,self.uid,a)
        print "cccc",b
        return b
    
    def _get_object(self,data):
        #print "Data:", data
        obj_data=self.pool.get(data['model']).browse(self.cr,self.uid,[data['id']])
        return obj_data
    
#    def angka(self):
#        amount = 1000
        
    def _get_company_address(self, company):
        print "COMPANY::", company
        partner = company.partner_id.id
        address_id = self.pool.get('res.partner.address').search(self.cr,self.uid,[('partner_id','=',partner)])
        print address_id
        address = self.pool.get('res.partner.address').browse(self.cr,self.uid,address_id[0])
        
        return address
        
    def convert(self, amount, cur):
        
        amt_id = amount_to_text_id.amount_to_text(amount, 'id', cur)
        print "==================>>>", amt_id
        return amt_id
        """amt_id = num2word.num2word_id(amount,"id",cur).decode('utf-8')
        return amt_id"""
    
    
           
report_sxw.report_sxw('report.sca.report.form', 'purchase.requisition', 'ad_sca/report/sca_report.mako', parser=sca_report,header=False)


#data = [(tanggal,harga),(tanggal,harga)]
