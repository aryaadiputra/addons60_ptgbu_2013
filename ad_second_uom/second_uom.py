import netsvc, time
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser

#class historical_transaction(osv.osv):
#    _name = 'historical.transaction'
#    
#    _columns = {
#            'order_id'                      : fields.many2one('purchase.order'),
#            'name'                          : fields.many2one('material.requisition','name'),
#            'material_req_created_date'     : fields.datetime('Material Request Created Date'),
#            'material_req_release_date'     : fields.datetime('Material Request Release Date'),
#            'internal_move_date'            : fields.datetime('Internal Move Date'),
#            'purchase_requisition_date'     : fields.datetime('Purchase Requisition Created Date'),
#            'request_for_quotation'         : fields.datetime('Request for Quotation Created Date'),
#            'purchase_order_release_date'   : fields.datetime('Purchase Order Released Date'),
#            'manager_proc_app_date'         : fields.datetime('Manager Procurement Approve Date'),
#            'head_of_div_proc_app_date'     : fields.datetime('Head of Division Procurement Approve Date'),
#            'head_of_div_req_app_date'      : fields.datetime('Head of Division Approve Date'),
#            'ceo'                           : fields.datetime('CEO Approve Date'),
#            'inv_receive_date'              : fields.datetime('Invoice Receive Date'),
#            'payment_inv_date'              : fields.datetime('Payment Invoice Date'),
#                }
#historical_transaction()

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'factor': fields.float('Convertion', digits=(16, 5)),
        'factor_price': fields.float('Price @UoM PO', digits=(16, 5)),
        'tolerances_uom': fields.selection([
            ('persen', ' % (Percentage)'),
            ('qty', 'Fixed Qty'),
            ], 'UoM Tolerances', readonly=False, select=True),
        'tolerances_qty': fields.float('Qty Tolerances', digits=(16, 2), required=False, readonly=False), 
    }
    _defaults = {'factor': 1.0}
    
    def create(self, cr, uid, data, context=None):
        res = self.search(cr, uid, [('default_code', '=', data['default_code']), ('name_template', '=', data['name'])])
        if res:
            raise osv.except_osv(('Perhatian !'), ('There is duplicate product : %s') % [data['default_code'], data['name']])
        return super(product_product, self).create(cr, uid, data, context)
    
   
    def write(self, cr, uid, ids, vals, context=None):
        res = []
        product = self.browse(cr, uid, ids)[0]
        if vals.get('default_code', False) and vals.get('name', False):
            res = self.search(cr, uid, [('default_code', '=', vals['default_code']), ('name_template', '=', vals['name'])])
        elif vals.get('default_code', False):
            res = self.search(cr, uid, [('default_code', '=', vals['default_code']), ('name_template', '=', product.name_template)])
        elif vals.get('name', False):
            res = self.search(cr, uid, [('default_code', '=', product.default_code), ('name_template', '=', vals['name'])])
        
        if res:
            raise osv.except_osv(('Perhatian !'), ('There is duplicate product'))
        return super(product_product, self).write(cr, uid, ids, vals, context=context)

product_product()

class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    _columns = {
        'factor': fields.float('Convertion', digits=(16, 5)),
        'uom_warehouse' : fields.many2one('product.uom', 'UoM WH'),
        'uom_warehouse_qty' : fields.float('Qty UoM WH', digits=(16, 2), required=False, readonly=False),
        'tolerances_uom': fields.selection([
            ('persen', ' % (Percentage)'),
            ('qty', 'Fixed Qty'),
            ], 'UoM Tolerances', readonly=False, select=True),
        'tolerances_qty': fields.float('Qty Tolerances', digits=(16, 2), required=False, readonly=False),
        'use_incoming_plan': fields.boolean('Use Incoming Shipment Plan ?'),
        'incoming_plan': fields.one2many('incoming.plan', 'incoming_id', 'Incoming Shipment Plan', readonly=True, states={'draft': [('readonly', False)]}),
        'pr_line_id' : fields.many2one('purchase.requisition.line', 'PR Line ID'),
    }

    def uom_warehouse_qty_change(self, cr, uid, ids, pid, qty):
        if pid :
            val = qty
            product = self.pool.get('product.product').browse(cr, uid, [pid])[0]
            if product.uom_id.id != product.uom_po_id.id :
                val = qty / product.factor
            return {'value':{'uom_warehouse_qty':val}}
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty, uom,
            partner_id, date_order=False, fiscal_position=False, date_planned=False,
            name=False, price_unit=False, notes=False):
        if not pricelist:
            raise osv.except_osv(_('No Pricelist !'), _('You have to select a pricelist or a supplier in the purchase form !\nPlease set one before choosing a product.'))
        if not  partner_id:
            raise osv.except_osv(_('No Partner!'), _('You have to select a partner in the purchase form !\nPlease set one partner before choosing a product.'))
        if not product:
            return {'value': {'price_unit': price_unit or 0.0, 'name': name or '',
                'notes': notes or'', 'product_uom' : uom or False}, 'domain':{'product_uom':[]}}
        res = {}
        prod= self.pool.get('product.product').browse(cr, uid, product)

        product_uom_pool = self.pool.get('product.uom')
        lang=False
        if partner_id:
            lang=self.pool.get('res.partner').read(cr, uid, partner_id, ['lang'])['lang']
        context={'lang':lang}
        context['partner_id'] = partner_id

        prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
        prod_uom_po = prod.uom_po_id.id
        if not uom:
            uom = prod_uom_po
        if not date_order:
            date_order = time.strftime('%Y-%m-%d')
        qty = qty or 1.0
        seller_delay = 0

        prod_name = self.pool.get('product.product').name_get(cr, uid, [prod.id], context=context)[0][1]
        res = {}
        for s in prod.seller_ids:
            if s.name.id == partner_id:
                seller_delay = s.delay
                if s.product_uom:
                    temp_qty = product_uom_pool._compute_qty(cr, uid, s.product_uom.id, s.min_qty, to_uom_id=prod.uom_id.id)
                    uom = s.product_uom.id #prod_uom_po
                temp_qty = s.min_qty # supplier _qty assigned to temp
                if qty < temp_qty: # If the supplier quantity is greater than entered from user, set minimal.
                    qty = temp_qty
                    res.update({'warning': {'title': _('Warning'), 'message': _('The selected supplier has a minimal quantity set to %s, you cannot purchase less.') % qty}})
        qty_in_product_uom = product_uom_pool._compute_qty(cr, uid, uom, qty, to_uom_id=prod.uom_id.id)
        price = self.pool.get('product.pricelist').price_get(cr,uid,[pricelist],
                    product, qty_in_product_uom or 1.0, partner_id, {
                        'uom': uom,
                        'date': date_order,
                        })[pricelist]
        dt = (datetime.now() + relativedelta(days=int(seller_delay) or 0.0)).strftime('%Y-%m-%d %H:%M:%S')

        if prod.factor_price > 0.0 :
            price = prod.factor_price
            
        res.update({'value': {'price_unit': price, 'name': prod_name,
            'taxes_id':map(lambda x: x.id, prod.supplier_taxes_id),
            'date_planned': date_planned or dt,'notes': notes or prod.description_purchase,
            'product_qty': qty,
            'product_uom': uom}})
        domain = {}

        taxes = self.pool.get('account.tax').browse(cr, uid,map(lambda x: x.id, prod.supplier_taxes_id))
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        res['value']['taxes_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)

        res2 = self.pool.get('product.uom').read(cr, uid, [uom], ['category_id'])
        res3 = prod.uom_id.category_id.id
        domain = {'product_uom':[('category_id','=',res2[0]['category_id'][0])]}
        if res2[0]['category_id'][0] != res3:
            raise osv.except_osv(_('Wrong Product UOM !'), _('You have to select a product UOM in the same category than the purchase UOM of the product'))
        
        if prod.uom_id.id != prod.uom_po_id.id :
                qty = qty / prod.factor
        res['value']['uom_warehouse_qty'] = qty 
        res['domain'] = domain
        return res

purchase_order_line()

class IncomingPlan(osv.osv):
    _name = "incoming.plan"
    _columns = {
                'incoming_id': fields.integer('Id', readonly=False),
                'name': fields.char('Release Code', size=64, required=True, select=True),
                'qty': fields.float('Quantity', digits=(16, 2), required=True),
                'date': fields.date('Release Date', required=True),
    }
    
    _defaults = {
                 'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'release.plan'),
                 'date': lambda *a: time.strftime('%Y-%m-%d'),
                 }
        
IncomingPlan()


class purchase_requisition_partner(osv.osv_memory):
    _inherit = "purchase.requisition.partner"
    
    def create_order(self, cr, uid, ids, context=None):
        print "BBB"
        print "create_order::"
        """
             To Create a purchase orders .

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary
             @return: {}

        """
        if context is None:
            context = {}
        record_ids = context and context.get('active_ids', False)
        if record_ids:
            data =  self.read(cr, uid, ids)
            company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
            order_obj = self.pool.get('purchase.order')
            order_line_obj = self.pool.get('purchase.order.line')
            partner_obj = self.pool.get('res.partner')
            tender_line_obj = self.pool.get('purchase.requisition.line')
            pricelist_obj = self.pool.get('product.pricelist')
            prod_obj = self.pool.get('product.product')
            tender_obj = self.pool.get('purchase.requisition')
            acc_pos_obj = self.pool.get('account.fiscal.position')
            partner_id = data[0]['partner_id']
            h = self.pool.get('purchase.compare')

            supplier_data = partner_obj.browse(cr, uid, partner_id, context=context)

            address_id = partner_obj.address_get(cr, uid, [partner_id], ['delivery'])['delivery']
            list_line=[]
            purchase_order_line={}
            for tender in tender_obj.browse(cr, uid, record_ids, context=context):
                pd = None
                for line in tender.line_ids:
                    partner_list = sorted([(partner.sequence, partner) for partner in  line.product_id.seller_ids if partner])
                    partner_rec = partner_list and partner_list[0] and partner_list[0][1] or False
                    uom_id = line.product_id.uom_po_id and line.product_id.uom_po_id.id or False

                    if tender.date_start:
                        newdate = datetime.strptime(tender.date_start, '%Y-%m-%d %H:%M:%S') - relativedelta(days=company.po_lead)
                    else:
                        newdate = datetime.today() - relativedelta(days=company.po_lead)
                    delay = partner_rec and partner_rec.delay or 0.0
                    if delay:
                        newdate -= relativedelta(days=delay)

                    partner = partner_rec and partner_rec.name or supplier_data
                    pricelist_id = partner.property_product_pricelist_purchase and partner.property_product_pricelist_purchase.id or False
                    price = pricelist_obj.price_get(cr, uid, [pricelist_id], line.product_id.id, line.product_qty, False, {'uom': uom_id})[pricelist_id]
                    product = prod_obj.browse(cr, uid, line.product_id.id, context=context)
                    location_id = self.pool.get('stock.warehouse').read(cr, uid, [tender.warehouse_id.id], ['lot_input_id'])[0]['lot_input_id'][0]
                    
                    convertion = 1.0
                    if line.product_id.factor > 0.00000 and line.product_id.factor_price > 1.0 :
                        convertion = line.product_id.factor
                        price = line.product_id.factor_price
                    
                    
                    purchase_order_line= {
                            'name': product.partner_ref,
                            'product_qty': (line.product_qty-line.qty_order) * convertion, #line.product_qty * line.product_id.uom_po_id.factor,
                            'product_id': line.product_id.id,
                            'product_uom': uom_id,
                            #'price_unit': price,
                            'price_unit': line.price,
                            'factor': line.product_id.factor,
                            'uom_warehouse_qty': (line.product_qty-line.qty_order) * line.product_id.uom_po_id.factor,
                            'uom_warehouse': line.product_id.uom_id.id,
                            'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                            'notes': line.detail or "",
                            'account_analytic_id': line.account_analytic_id.id,
                            'ket': line.ket,
                            'pr_line_id':line.id,
                    }
                    
                    pd = line.product_id                         
                    if pd.tolerances_uom and pd.tolerances_qty :
                        purchase_order_line.update({
                            'tolerances_uom': pd.tolerances_uom,
                            'tolerances_qty': pd.tolerances_qty,
                        })                   
                    
                    taxes_ids = line.product_id.product_tmpl_id.supplier_taxes_id
                    taxes = acc_pos_obj.map_tax(cr, uid, partner.property_account_position, taxes_ids)
                    purchase_order_line.update({
                            'taxes_id': [(6,0,taxes)]
                        })
                    list_line.append(purchase_order_line)
                #################################Di Rrmove karena tidak memkai Seq ini lagi, dipisah antara PO & RFQ############################################
                #name_purchase = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order')
                #print "name_purchase::", name_purchase
                #print "tender.origin::", tender.origin
                #new_name = name_purchase[:6] + '/' + (tender.origin).upper()
                #print "new_name::", new_name        
                #############################################################################
                ################################Tambahan Cek Historical######################################
                for tender in tender_obj.browse(cr, uid, record_ids, context=context):
                    name = False
                    material_req_date = False
                    internal_move_date = False
                    if tender.int_move_id:
                        internal_move_date = tender.int_move_id.min_date
                        material_req_created_date = tender.int_move_id.material_req_id.date_start
                        material_req_release_date = tender.int_move_id.material_req_id.kadiv_app
                        #print "material_req_release_date ::::", material_req_release_date
                        name = tender.int_move_id.material_req_id.id
                    else:
                        internal_move_date = False
                        material_req_created_date = False
                        material_req_release_date = False
                        name = False
                    purchase_req_date = tender.date_start or False
                ######################################################################
                
                purchase_id = order_obj.create(cr, uid, {
                            #'name': name_purchase,
                            'name': "/",
                            'origin': tender.purchase_ids and tender.purchase_ids[0].origin or tender.name,
                            'partner_id': partner_id,
                            'partner_address_id': address_id,
                            'pricelist_id': pricelist_id,
                            'location_id': tender.purchase_ids and tender.purchase_ids[0].location_id.id or line.product_id.product_tmpl_id.property_stock_production.id,
                            'company_id': tender.company_id.id,
                            'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
                            'requisition_id':tender.id,
                            'notes':tender.description,
                            'warehouse_id':tender.warehouse_id.id and tender.warehouse_id.id ,
                            'location_id':location_id,
                            'company_id':tender.company_id.id,
                            'delegate': tender.delegate.id,
                            'mr_description' : tender. mr_description,
                            ######################################################################
                            'mr_number'                     : name or False,
                            'material_req_created_date'     : material_req_created_date or False,
                            'material_req_release_date'     : material_req_release_date or False,
                            'purchase_requisition_date'     : purchase_req_date or False,
                            'request_for_quotation'         : time.strftime('%Y-%m-%d'),
                            ######################################################################
                            
                })
                order_ids=[]
                for order_line in list_line:
                    order_line.update({
                            'order_id': purchase_id
                        })
                    order_line_obj.create(cr,uid,order_line)
                    
                ########################Historical Approval#######
                
#                for tender in tender_obj.browse(cr, uid, record_ids, context=context):
#                    name = False
#                    material_req_date = False
#                    internal_move_date = False
#                    if tender.int_move_id:
#                        internal_move_date = tender.int_move_id.min_date
#                        material_req_date = tender.int_move_id.material_req_id.user_app
#                        name = tender.int_move_id.material_req_id.id
#                    purchase_req_date = tender.manager_approve_date or False
                        
#                    order_obj.write(cr, uid, ids, {
#                                        'mr_number'                     : name,
##                                        'material_req_created_date'
##                                        'material_req_release_date'
##                                        'internal_move_date'
##                                        'purchase_requisition_date'
##                                        'request_for_quotation'
##                                        'purchase_order_release_date'
##                                        'manager_proc_app_date'
##                                        'head_of_div_proc_app_date'
##                                        'head_of_div_req_app_date'
##                                        'ceo'
##                                        'inv_receive_date'
##                                        'payment_inv_date'
#                                                   })
                    
#                    print "name :", tender.int_move_id.material_req_id.name
#                    
#                    print "internal_move_date **********************************************:", internal_move_date
#                    print "material_req_date **********************************************:", material_req_date
#                    print "pr_date", 
                    #################################Remove Not use Historical Object anymore####################################
#                    historical = {
#                        'order_id' : purchase_id or False,
#                        'name' : name,
#                        'material_req_date': material_req_date,
#                        'internal_move_date': internal_move_date,
#                        'purchase_requisition_date': purchase_req_date or False,
#                        
#                         }
#                    x = self.pool.get('historical.transaction').create(cr, uid, historical)

                    #####################################################################
                #################################################    
                
                ##################Comparation#####################
                
                a = order_line_obj.search(cr, uid, [('order_id','=',purchase_id)])
                b = order_line_obj.browse(cr, uid, a)
                
                
                #print "Hasil :", cr.fetchone()[0]
                
                print "bbbbb", b
                for c in b:
                    #print "nnnnnnnnnn", c.name
                    #print "nnnnnnnnnn", c.product_id.id
                    product_id = c.product_id.id
                    
                    id_line = order_line_obj.search(cr,uid,[('product_id','=',product_id),('state','=',"confirmed")])
                    
                    if id_line:
                        #print "ID LINE",id_line
                        price=[]
                        last_date=[]
                        for lines in id_line:
                            order_line = order_line_obj.browse(cr,uid,lines)
                            price.append(order_line.price_unit)
                            last_date.append(order_line.date_planned)
                        
                        cheapest_price = min(price)
                        
                        print "cheapest_price : ", cheapest_price
                        
                        cheapest_price_partner_search = order_line_obj.search(cr,uid,[('price_unit','=',cheapest_price),('product_id','=',product_id),('state','=',"confirmed")])
                        cheapest_price_partner_browse = order_line_obj.browse(cr,uid,cheapest_price_partner_search)
                        #print "lllllllllllllllllll", cheapest_price_partner_browse
                        for cheapest_price_partner in cheapest_price_partner_browse:
                            cheapest_price_partner = cheapest_price_partner.partner_id.name
                            #last_price_partner = 1
                        
                            print "cheapest_price_partner :1", cheapest_price_partner
                        
                        date_cheapest_search = order_line_obj.search(cr, uid, [('price_unit','=',cheapest_price),('product_id','=',product_id),('partner_id','=',cheapest_price_partner),('state','=',"confirmed")])
                        date_cheapest_browse = order_line_obj.browse(cr, uid,date_cheapest_search)
                        
                        print "date_cheapest_browse :", date_cheapest_browse
                        
                        for id_date in date_cheapest_browse:
                            id_date.id
                            id_date.date_planned
                            id_date.product_qty
                        date_cheapest_price = id_date.date_planned
                        qty_cheapest_price = id_date.product_qty
                        print "ID :", id_date.id
                        
                        cheapest_price = min(price)
                        
                        max_date = max(last_date)
                        print "max_date :>>>>>>>>>>>>>>>>>>>>>>>>", max_date
                        
                        #Last Transaction#
                        
                        order_line_last_search = order_line_obj.search(cr,uid,[('date_planned','=',max_date),('product_id','=',product_id),('state','=',"confirmed")])
                        order_line_last_browse = order_line_obj.browse(cr,uid,order_line_last_search)
                        #print "order_line_last_browse", order_line_last_browse
                        
                        if order_line_last_browse:
                            for y in order_line_last_browse:
                                #print "Nama Product:", y.name
                                print "Partner :", y.partner_id
                                print "Price Unit", y.price_unit
                                print "Date :", y.date_planned
                                print "Qty :", y.product_qty
                            date_last_price = y.date_planned
                            qty_last_price = y.product_qty
                            last_price_partner = y.partner_id.name
                            print "last_price_partner :", last_price_partner
                            last_price = y.price_unit
                        else:
                            last_price_partner = ''
                            last_price = 0.0
                    else:
                        #last_price_partner = ''
                        cheapest_price_partner = "/"
                        cheapest_price = 0.0
                        qty_cheapest_price = 0.0
                        date_cheapest_price = False
                        
                        last_price_partner =  "/"
                        last_price = 0.0
                        qty_last_price = 0.0
                        date_last_price = False
            
                    z = {
                        'order_id' : purchase_id,
                        'name' : c.name,
                        'cheapest_price_partner': cheapest_price_partner or "/",
                        'cheapest_price': cheapest_price,
                        'qty_cheapest_price': qty_cheapest_price,
                        'date_cheapest_price': date_cheapest_price,
                        'last_price_partner':  last_price_partner or "/",
                        'last_price': last_price,
                        'qty_last_price': qty_last_price,
                        'date_last_price': date_last_price,
                         }
                    print "zzzz:::", z
                    
                    print "HHH:::", h
                    
                    t = self.pool.get('purchase.compare')
                    print "TTTTTTTTTTTT:::", order_obj
                    
                    x = self.pool.get('purchase.compare').create(cr, uid, z)
                #######################################
                
        return {'type': 'ir.actions.act_window_close'}

purchase_requisition_partner()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    ###########################Ubah WKF untuk brg Service#################################
    def has_stockable_product(self,cr, uid, ids, *args):
        for order in self.browse(cr, uid, ids):
            for order_line in order.order_line:
                if order_line.product_id and order_line.product_id.product_tmpl_id.type in ('product', 'consu', 'service'):
                    return True
        return False
    ############################################################
    
    def _check_incoming_plan(self, cr, uid, ids):
        purchase = self.browse(cr, uid, ids)[0]
        for line in purchase.order_line:
            if line.use_incoming_plan:
                plan_qty = sum([x.qty for x in line.incoming_plan])
                if line.product_qty != plan_qty:
                    raise osv.except_osv(('Perhatian !'), ('Jumlah incoming plan qty tidak sama dengan jumlah produk qty pada produk %s') % line.name)
        return True

    _constraints = [
        (_check_incoming_plan, 'Quantity not equal', ['product_id']),
    ]

    def set_data_picking(self, purchase):
        tgl = []
        data = []
        for line in purchase.order_line:
            if line.use_incoming_plan:
                for x in line.incoming_plan:
                    tgl.append(x.date)
                    data.append({'line':line, 'release':x.name, 'date':x.date, 'qty':x.qty} )
            else:
                tgl.append(line.date_planned)
                data.append({'line':line, 'date':line.date_planned, 'qty':line.product_qty, 'release':''})
        
        tanggal = []
        result = []
        for d in data:    
            if d['date'] not in tanggal:
                result.append({'date':d['date'], 'schedule':[{'line':d['line'], 'qty':d['qty'], 'release':d['release']}]})
                tanggal.append(d['date'])
            else:
                for r in result:
                    if r['date'] == d['date']:
                        r['schedule'].append({'line':d['line'], 'qty':d['qty'], 'release':d['release']})         
        
        return result
    
    def action_picking_create(self,cr, uid, ids, *args):
        print "action_picking_create"
        #################Tambahan Informasi di Incoming########################
        req_employee    = False
        mr_description  = False
        ###########################################
        partial = False
        picking_id = False
        for order in self.browse(cr, uid, ids):
            loc_id = order.partner_id.property_stock_supplier.id
            istate = 'none'                    
                    
            schedule = self.set_data_picking(order)
            if len(schedule) > 1:
                partial = True 
            
            if order.invoice_method=='picking':
                istate = '2binvoiced'
            ##################Tambahan Informasi di Incoming#########################    
            if  order.mr_number:
                req_employee    = order.mr_number.req_employee.id
                mr_description  = order.mr_number.origin
            ################################################################
            if partial:
                picking_id = []
                for s in schedule:
                    
                    pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in')
                    pick_part_id = self.pool.get('stock.picking').create(cr, uid, {
                        'name': pick_name,
                        'origin': order.name+((order.origin and (':'+order.origin)) or ''),
                        'type': 'in',
                        'address_id': order.dest_address_id.id or order.partner_address_id.id,
                        'invoice_state': istate,
                        'purchase_id': order.id,
                        'company_id': order.company_id.id,
                        'min_date': s['date'],
                        'move_lines' : [],
                        ##################Tambahan Informasi di Incoming#########################
                        'req_employee'      : req_employee,
                        'mr_description'    : req_employee,
                        #########################################################################
                        })
                    picking_id = pick_part_id
                    todo = []
                    for line in s['schedule']:
                        convertion = 1.0
                        if line['line'].product_id.factor > 0.00000 :
                            convertion = line['line'].product_id.factor
                            
                        if not line['line'].product_id:
                            continue
                        if line['line'].product_id.product_tmpl_id.type in ('product', 'consu','service'):
                            dest = order.location_id.id
                            move = self.pool.get('stock.move').create(cr, uid, {
                                'name': order.name + ': ' +(line['line'].name or ''),
                                'product_id': line['line'].product_id.id,
                                'product_qty': line['qty'] / convertion, # order_line.product_qty
                                'product_uos_qty': line['qty'] / convertion, # order_line.product_qty
                                'product_uom': line['line'].product_id.uom_id.id, # order_line.product_uom.id,
                                'product_uos': line['line'].product_id.uom_id.id, # order_line.product_uom.id,
                                'uom_po_id': line['line'].product_uom.id,
                                'uom_po_qty': line['qty'],
                                'date': s['date'],
                                'date_expected': s['date'],
                                'location_id': loc_id,
                                'location_dest_id': dest,
                                'picking_id': pick_part_id,
                                'move_dest_id': line['line'].move_dest_id.id,
                                'state': 'draft',
                                'purchase_line_id': line['line'].id,
                                'company_id': order.company_id.id,
                                'release': line['release'],
                                'price_unit': line['line'].price_unit
                            })
                            if line['line'].move_dest_id:
                                self.pool.get('stock.move').write(cr, uid, [line['line'].move_dest_id.id], {'location_id':order.location_id.id})
                            todo.append(move)
                    self.pool.get('stock.move').action_confirm(cr, uid, todo)
                    self.pool.get('stock.move').force_assign(cr, uid, todo)
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'stock.picking', pick_part_id, 'button_confirm', cr)    
            else:
                pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in')
                picking_id = self.pool.get('stock.picking').create(cr, uid, {
                    'name': pick_name,
                    'origin': order.name+((order.origin and (':'+order.origin)) or ''),
                    'type': 'in',
                    'address_id': order.dest_address_id.id or order.partner_address_id.id,
                    'invoice_state': istate,
                    'purchase_id': order.id,
                    'min_date': order.minimum_planned_date,
                    'company_id': order.company_id.id,
                    'move_lines' : [],
                    ##################Tambahan Informasi di Incoming#########################
                    'req_employee'      : req_employee,
                    'mr_description'    : mr_description,
                    #########################################################################
                })
            
                todo_moves = []
                for order_line in order.order_line:
                    convertion = 1.0
                    if order_line.product_id.factor > 0.00000 :
                        convertion = order_line.product_id.factor
                        
                    if not order_line.product_id:
                        continue
                    if order_line.product_id.product_tmpl_id.type in ('product', 'consu','service'):
                        dest = order.location_id.id
                        move = self.pool.get('stock.move').create(cr, uid, {
                            'name': order.name + ': ' +(order_line.name or ''),
                            'product_id': order_line.product_id.id,
                            'product_qty': order_line.product_qty / convertion, # order_line.product_qty
                            'product_uos_qty': order_line.product_qty / convertion, # order_line.product_qty
                            'product_uom': order_line.product_id.uom_id.id, # order_line.product_uom.id,
                            'product_uos': order_line.product_id.uom_id.id, # order_line.product_uom.id,
                            'uom_po_id': order_line.product_uom.id,
                            'uom_po_qty': order_line.product_qty,
                            'date': order_line.date_planned,
                            'date_expected': order_line.date_planned,
                            'location_id': loc_id,
                            'location_dest_id': dest,
                            'picking_id': picking_id,
                            'move_dest_id': order_line.move_dest_id.id,
                            'state': 'draft',
                            'purchase_line_id': order_line.id,
                            'company_id': order.company_id.id,
                            'price_unit': order_line.price_unit
                        })
                        if order_line.move_dest_id:
                            self.pool.get('stock.move').write(cr, uid, [order_line.move_dest_id.id], {'location_id':order.location_id.id})
                        todo_moves.append(move)
                self.pool.get('stock.move').action_confirm(cr, uid, todo_moves)
                self.pool.get('stock.move').force_assign(cr, uid, todo_moves)
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return picking_id
    
    _columns = {
            'delegate'                      : fields.many2one('res.users', 'Delegate to'),
            #'historical_transaction_line'   : fields.one2many('historical.transaction','order_id'),
            'mr_description'                : fields.char("Description", size=64),
            ################################Historical#######################################
            'mr_number'                     : fields.many2one('material.requisition','Material Requisition'),
            'material_req_created_date'     : fields.date('Material Request Created Date'),
            'material_req_release_date'     : fields.date('Material Request Release Date'),
            'internal_move_date'            : fields.date('Internal Move Date'),
            'purchase_requisition_date'     : fields.date('Purchase Requisition Created Date'),
            'request_for_quotation'         : fields.date('Request for Quotation Created Date'),
            'purchase_order_release_date'   : fields.date('Purchase Order Released Date'),
            'manager_proc_app_date'         : fields.date('Manager Procurement Approve Date'),
            'head_of_div_proc_app_date'     : fields.date('Head of Division Procurement Approve Date'),
            'head_of_div_req_app_date'      : fields.date('Head of Division Approve Date'),
            'ceo'                           : fields.date('CEO Approve Date'),
            'inv_receive_date'              : fields.date('Invoice Receive Date'),
            'payment_inv_date'              : fields.date('Payment Invoice Date'),
            ####################################################################################
                }
    
purchase_order()

############Tambahan Informasi di Incoming Shipment##############
class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    _columns = {
            'req_employee'      : fields.many2one('hr.employee', 'Request By',),
            'mr_description'    : fields.char('Description', size=64),
                }
stock_picking()
#################################################################

class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
                'release': fields.char('Release Code', size=64, select=True),
                'uom_po_id': fields.many2one('product.uom', 'UoM PO'),
                'uom_po_qty': fields.float('Qty PO', digits=(16, 5)),
    }
        
stock_move()

class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
        
    def do_partial(self, cr, uid, ids, context=None):
        """ Makes partial moves and pickings done.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        toleran = False
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        
        picking_ids = context.get('active_ids', False)
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_datas = {
            'delivery_date' : partial.date
        }

        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            picking_type = self.get_picking_type(cr, uid, pick, context=context)
            moves_list = picking_type == 'in' and partial.product_moves_in or partial.product_moves_out
            if not [move for move in moves_list]:
                    raise osv.except_osv(_('Perhatian'), _('Daftar product tidak boleh kosong !'))
            for move in moves_list:

                #Adding a check whether any line has been added with new qty
                if not move.move_id:
                    raise osv.except_osv(_('Processing Error'),\
                    _('You cannot add any new move while validating the picking, rather you can split the lines prior to validation!'))

                calc_qty = uom_obj._compute_qty(cr, uid, move.product_uom.id, \
                                    move.quantity, move.move_id.product_uom.id)

                #Adding a check whether any move line contains exceeding qty to original moveline
                if calc_qty > move.move_id.product_qty:
                    tol_uom = move.move_id.purchase_line_id.tolerances_uom
                    tol_qty = move.move_id.purchase_line_id.tolerances_qty
                    if tol_uom and tol_qty > 0.0 :
                        tol_max = move.move_id.product_qty + tol_qty
                        if tol_uom == 'persen' :
                            tol_max = move.move_id.product_qty + ((move.move_id.purchase_line_id.uom_warehouse_qty * tol_qty) / 100) 
                         
                        if move.quantity > tol_max :
                            raise osv.except_osv(_('Error Toleransi'), 
                            _('Quantity sebanyak %d %s melebihi batas toleransi yang ditentukan sebanyak %d %s !')\
                            % (move.quantity, move.product_uom.name, tol_max, move.product_uom.name))
                        
                        toleran = True
                        
                    else:        
                        raise osv.except_osv(_('Processing Error'),
                        _('Processing quantity %d %s for %s is larger than the available quantity %d %s !')\
                        %(move.quantity, move.product_uom.name, move.product_id.name,\
                          move.move_id.product_qty, move.move_id.product_uom.name))

                #Adding a check whether any move line contains qty less than zero
                if calc_qty <= 0:
                    raise osv.except_osv(_('Processing Error'), \
                            _('Can not process quantity %d for Product %s !') \
                            %(move.quantity, move.product_id.name))

                partial_datas['move%s' % (move.move_id.id)] = {
                    'product_id': move.product_id.id,
                    'product_qty': calc_qty,
                    'product_uom': move.move_id.product_uom.id,
                    'prodlot_id': move.prodlot_id.id,
                }
                if (picking_type == 'in') and (move.product_id.cost_method == 'average'):
                    partial_datas['move%s' % (move.move_id.id)].update({
                                                    'product_price' : move.cost,
                                                    'product_currency': move.currency.id,
                                                    })
        
        id_do = pick_obj.do_partial(cr, uid, picking_ids, partial_datas, context=context)
        id_done = id_do.items()
        contract = self.pool.get('stock.picking').browse(cr,uid, picking_ids[0])
        
        # PARSIAL DELIVERY ORDER WHEN DONE
        pool_data = self.pool.get('ir.model.data')
        action_model_out, action_id_out = pool_data.get_object_reference(cr, uid, 'stock', "view_picking_out_form")
        action_pool_out = self.pool.get(action_model_out)
        res_id_out = action_model_out and action_id_out or False
        action_out = action_pool_out.read(cr, uid, action_id_out, context=context) 
        action_out['name'] = 'Partial Delivery Done'
        action_out['view_type'] = 'form'
        action_out['view_mode'] = 'form'
        action_out['view_id'] = [res_id_out]
        action_out['res_model'] = 'stock.picking'
        action_out['context'] = "{'type':'out','state':'done','invoice_state':'2binvoiced'}"
        action_out['type'] = 'ir.actions.act_window'
        action_out['target'] = 'current'
        action_out['res_id'] = id_done[0][1]['delivered_picking']
                
        # PARSIAL INCOMING SHIPMENT WHEN DONE
        action_model_in,action_id_in = pool_data.get_object_reference(cr, uid, 'stock', "view_picking_in_form")
        action_pool_in = self.pool.get(action_model_in)
        res_id_in = action_model_in and action_id_in or False
        action_in = action_pool_in.read(cr, uid, action_id_in, context=context) 
        action_in['name'] = 'Partial Incoming Done'
        action_in['view_type'] = 'form'
        action_in['view_mode'] = 'form'
        action_in['view_id'] = [res_id_in]
        action_in['res_model'] = 'stock.picking'
        action_in['context'] = "{'type':'in','state':'done'}"
        action_in['type'] = 'ir.actions.act_window'
        action_in['target'] = 'current'
        action_in['res_id'] = id_done[0][1]['delivered_picking']
        
        picking_done = self.pool.get('stock.picking').browse(cr,uid, [id_done[0][1]['delivered_picking']])[0]
        action_close = {'type': 'ir.actions.act_window_close'} 
        if contract.state == 'done':
            if contract.type == 'out':
                name = self.pool.get('ir.sequence').get(cr, uid, contract.partner_id.sequence_do.code)
                m = '/' + name.split('/')[-2] + '/'
                n = '/' + str(contract.delivery_datetime)[5:7] + '/'
                name = name.replace(m, n)
                self.pool.get('stock.picking').write(cr, uid, [contract.id], {'name': name})
                for move in picking_done.move_lines:
                    self.pool.get('sale.order.line').write(cr, uid, [move.sale_line_id.id], {'terkirim': move.sale_line_id.terkirim + move.product_qty})

            action_close = {'type': 'ir.actions.act_window_close'} 
            if contract.purchase_id.id :
                #self.pool.get('purchase.order').write(cr, uid, [contract.purchase_id.id], {'close':True})
                idp = self.pool.get('stock.picking').search(cr, uid, [('purchase_id','=',contract.purchase_id.id)])
                #self.pool.get('stock.picking').write(cr, uid, idp, {'close_purchase':True})
                if toleran :
                    product = []
                    data = self.pool.get('stock.picking').browse(cr, uid, idp)                    
                    for d in data:
                        for m in d.move_lines:
                            product.append({
                                            'product_id': m.product_id.id,
                                            'product_qty': m.product_qty,
                                            })
                    prod = []
                    invoice = []
                    for y in product :    
                        if y['product_id'] not in prod:
                            invoice.append({'id': y['product_id'], 'qty':[y['product_qty']]})
                            prod.append(y['product_id'])
                        else:
                            for i in invoice:
                                if i['id'] == y['product_id']:
                                    i['qty'].append(y['product_qty'])
                                
                    inv_id = self.pool.get('account.invoice').search(cr, uid, [('name','=', contract.purchase_id.name)])
                    inv_line_id = self.pool.get('account.invoice.line').search(cr, uid, [('invoice_id','=', inv_id[0])])
                    inv_line_data = self.pool.get('account.invoice.line').browse(cr, uid, inv_line_id)

                    for x in inv_line_data :
                        for z in invoice:
                            if z['id'] == x.product_id.id: 
                                self.pool.get('account.invoice.line').write(cr, uid, [x.id], {'quantity': sum(z['qty'])})
                                if x.product_id.uom_id.id != x.product_id.uom_po_id.id : 
                                    self.pool.get('account.invoice.line').write(cr, uid, [x.id], {'quantity': sum(z['qty']) * x.product_id.factor})
                                           
                    self.pool.get('account.invoice').button_compute(cr, uid, inv_id, {'type':'in_invoice'}, set_total=True)
                    da = self.pool.get('account.invoice').read(cr, uid, inv_id)[0]
                    self.pool.get('account.invoice').write(cr, uid, inv_id, {'check_total': da['amount_total']})
              
        else:
            if contract.type == 'out':
                action_close = action_out
                picking = self.pool.get('stock.picking').browse(cr, uid, [action_out['res_id']])[0]              
                name = self.pool.get('ir.sequence').get(cr, uid, picking.partner_id.sequence_do.code)
                m = '/' + name.split('/')[-2] + '/'
                n = '/' + str(picking.delivery_datetime)[5:7] + '/'
                name = name.replace(m, n)
                self.pool.get('stock.picking').write(cr, uid, [picking.id], {'name': name})
                for move in picking_done.move_lines:
                    self.pool.get('sale.order.line').write(cr, uid, [move.sale_line_id.id], {'terkirim': move.sale_line_id.terkirim + move.product_qty})

            elif contract.type == 'in':
                action_close = action_in
        return action_close

stock_partial_picking()


