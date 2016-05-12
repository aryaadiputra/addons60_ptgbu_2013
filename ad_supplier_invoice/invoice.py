import time
from osv import fields, osv

class add_wf_invoice(osv.osv):
   
    ''' inherited account.invoice '''
    _inherit = "account.invoice"
    
    def button_confirm(self, cr, uid, ids, *args):
        print "================="
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"confirm"})
        return True
    
    def confirm_cancel(self, cr, uid, ids, *args):
        print "================="
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"draft"})
        return True
    
    
    _columns = {
        'state': fields.selection([
                ('draft','Draft'),
                ('proforma','Pro-forma'),
                ('proforma2','Pro-forma'),
                ('confirm','Confirm'),
                ('open','Open'),
                ('paid','Paid'),
                ('cancel','Cancelled')
                ],'State', select=True, readonly=True,
                help=' * The \'Draftxx\' state is used when a user is encoding a new and unconfirmed Invoice. \
                \n* The \'Pro-forma\' when invoice is in Pro-forma state,invoice does not have an invoice number. \
                \n* The \'Open\' state is used when user create invoice,a invoice number is generated.Its in open state till user does not pay invoice. \
                \n* The \'Paid\' state is set automatically when invoice is paid.\
                \n* The \'Cancelled\' state is used when user cancel invoice.'),
                
                }
                
add_wf_invoice()