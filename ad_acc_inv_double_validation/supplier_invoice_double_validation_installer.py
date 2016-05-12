from osv import fields, osv

class supplier_invoice_double_validation_installer(osv.osv_memory):
    """CFO Cost Control"""
    _name = 'supplier.invoice.double.validation.installer'
    _inherit = 'res.config'
    _columns = {
        'limit_amount': fields.integer('Maximum Supplier Invoice Amount', required=True, help="Maximum amount after which validation of supplier is required."),
    }

    _defaults = {
        'limit_amount': 1000000,
    }

    def execute(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)
        if not data:
            return {}
        amt = data[0]['limit_amount']
        data_pool = self.pool.get('ir.model.data')
        transition_obj = self.pool.get('workflow.transition')
        waiting = data_pool._get_id(cr, uid, 'ad_acc_inv_double_validation', 'tlv2')
        waiting_id = data_pool.browse(cr, uid, waiting, context=context).res_id
        confirm = data_pool._get_id(cr, uid, 'ad_acc_inv_double_validation', 'tlv2i')
        confirm_id = data_pool.browse(cr, uid, confirm, context=context).res_id
        transition_obj.write(cr, uid, waiting_id, {'condition': 'amount_total>=%s' % (amt)})
        transition_obj.write(cr, uid, confirm_id, {'condition': 'amount_total<%s' % (amt)})
        return {}

supplier_invoice_double_validation_installer()

class supplier_invoice_double_validation_installer3(osv.osv_memory):
    """CEO Cost Control"""
    _name = 'supplier.invoice.double.validation.installer3'
    _inherit = 'res.config'
    _columns = {
        'limit_amount': fields.integer('Maximum Supplier Invoice Amount', required=True, help="Maximum amount after which validation of supplier is required."),
    }

    _defaults = {
        'limit_amount': 100000000,
    }

    def execute(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)
        if not data:
            return {}
        amt = data[0]['limit_amount']
        data_pool = self.pool.get('ir.model.data')
        transition_obj = self.pool.get('workflow.transition')
        waiting = data_pool._get_id(cr, uid, 'ad_acc_inv_double_validation', 'tlv2-1')
        waiting_id = data_pool.browse(cr, uid, waiting, context=context).res_id
        confirm = data_pool._get_id(cr, uid, 'ad_acc_inv_double_validation', 'tlv2-1i')
        confirm_id = data_pool.browse(cr, uid, confirm, context=context).res_id
        transition_obj.write(cr, uid, waiting_id, {'condition': 'amount_total>=%s' % (amt)})
        transition_obj.write(cr, uid, confirm_id, {'condition': 'amount_total<%s' % (amt)})
        return {}

supplier_invoice_double_validation_installer3()

class supplier_invoice_double_validation_installer4(osv.osv_memory):
    """CFO Treasury"""
    _name = 'supplier.invoice.double.validation.installer4'
    _inherit = 'res.config'
    _columns = {
        'limit_amount': fields.integer('Maximum Supplier Invoice Amount', required=True, help="Maximum amount after which validation of supplier is required."),
    }

    _defaults = {
        'limit_amount': 1000000,
    }

    def execute(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)
        if not data:
            return {}
        amt = data[0]['limit_amount']
        data_pool = self.pool.get('ir.model.data')
        transition_obj = self.pool.get('workflow.transition')
        waiting = data_pool._get_id(cr, uid, 'ad_acc_inv_double_validation', 'tlv2')
        waiting_id = data_pool.browse(cr, uid, waiting, context=context).res_id
        confirm = data_pool._get_id(cr, uid, 'ad_acc_inv_double_validation', 'tlv2i')
        confirm_id = data_pool.browse(cr, uid, confirm, context=context).res_id
        transition_obj.write(cr, uid, waiting_id, {'condition': 'amount_total>=%s' % (amt)})
        transition_obj.write(cr, uid, confirm_id, {'condition': 'amount_total<%s' % (amt)})
        return {}

supplier_invoice_double_validation_installer4()

class supplier_invoice_double_validation_installer2(osv.osv_memory):
    """CEO Treasury"""
    _name = 'supplier.invoice.double.validation.installer2'
    _inherit = 'res.config'
    _columns = {
        'limit_amount': fields.integer('Maximum Supplier Invoice Amount', required=True, help="Maximum amount after which validation of supplier is required."),
    }

    _defaults = {
        'limit_amount': 100000000,
    }

    def execute(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)
        if not data:
            return {}
        amt = data[0]['limit_amount']
        data_pool = self.pool.get('ir.model.data')
        transition_obj = self.pool.get('workflow.transition')
        waiting = data_pool._get_id(cr, uid, 'ad_acc_inv_double_validation', 'tlv5')
        waiting_id = data_pool.browse(cr, uid, waiting, context=context).res_id
        confirm = data_pool._get_id(cr, uid, 'ad_acc_inv_double_validation', 'tlv5i')
        confirm_id = data_pool.browse(cr, uid, confirm, context=context).res_id
        transition_obj.write(cr, uid, waiting_id, {'condition': 'amount_total>=%s' % (amt)})
        transition_obj.write(cr, uid, confirm_id, {'condition': 'amount_total<%s' % (amt)})
        return {}

supplier_invoice_double_validation_installer2()