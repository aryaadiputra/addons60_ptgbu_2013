from osv import osv, fields
import pooler
import time

#===============================================================================
# Structure History [START]
#===============================================================================

class structure_history_line(osv.osv):
    _name = "structure.history.line"
    _columns = {
                'name'         : fields.char('Contact Name', size=128),
                'job_id'       : fields.integer('Job ID'),
                'partner'      : fields.many2one('res.partner', 'Partner'),
                'contact_id'   : fields.integer('Contact ID'),
                'date_start'   : fields.date('Start Date'),
                'date_stop'    : fields.date('Stop Date'),
                'function'     : fields.char('Function', size=64),
#                'history_id'   : fields.many2one('structure.history', 'History'),
                }
structure_history_line()

class res_partner_job(osv.osv):
    _inherit = 'res.partner.job'
    _columns = {
              'history_id':fields.integer("History ID"),
              }    
    def create(self, cr, uid, values, context=None):
        ids = super(res_partner_job, self).create(cr, uid, values, context)
        job_id = self.pool.get('res.partner.job').search(cr, uid, [('function_id', '=', values['function_id']), ('contact_id', '=', values['contact_id'])])[0]
        contact = self.pool.get('res.partner.contact').browse(cr, uid, values['contact_id'])
        if contact['first_name']:
            contact_name = '%s' % contact['first_name'] + " " + contact['name'],
        else:
            contact_name = contact['name']
        contact_name = str(contact_name)
        name = contact_name[3:-3]
        history = {
                   'name'       : name,
                   'job_id'     : job_id,
                   'partner'    : values['function_id'],
                   'contact_id' : values['contact_id'],
                   'date_start' : values['date_start'],
                   'date_stop'  : values['date_stop'],
                   'function'   : values['function'],
                   }
        id_history = self.pool.get('structure.history.line').create(cr, uid, history)
        return ids
    
    def write(self, cr, uid, ids, vals, context=None):
        contact = self.pool.get('res.partner.contact').browse(cr, uid, vals['contact_id'])
        if contact['first_name']:
            contact_name = '%s' % contact['first_name'] + " " + contact['name'],
        else:
            contact_name = contact['name']

        history_id = self.pool.get('structure.history.line').search(cr, uid, [('job_id', '=', ids[0])])[0]
        values = {
               'name'       : contact_name,
               'job_id'     : ids[0],
               'contact_id' : vals['contact_id'],
               'date_start' : vals['date_start'],
               'date_stop'  : vals['date_stop'],
               'function'   : vals['function'],
                }
        self.pool.get('structure.history.line').write(cr, uid, history_id, values, context)
        return super(res_partner_job, self).write(cr, uid, ids, vals, context)
    
res_partner_job()

#===============================================================================
# Structure History [END]
#===============================================================================

#===============================================================================
# Document History [START]
#===============================================================================

class document_history_line(osv.osv):
    _name = "document.history.line"
    _columns = {
                'name'          : fields.char('Document Name', size=128),
                'doc_id'        : fields.integer('Doc ID'),
                'partner'       : fields.many2one('res.partner', 'Partner'),
                'date_start'    : fields.date('Date Issued'),
                'date_stop'     : fields.date('Date Expired'),
                'date_created'  : fields.datetime('Date Created'),
                'date_renew'    : fields.datetime('Last Edited'),
                'date_deleted'  : fields.datetime('Date Deleted'),
                } 
document_history_line()

class ir_attachment(osv.osv):
    _inherit = "ir.attachment"
    
    def create(self, cr, uid, values, context=None):
        ids = super(ir_attachment, self).create(cr, uid, values, context)
        history = {
                   'name'           : values['name'],
                   'doc_id'         : ids,
                   'partner'        : values['partner_id'],
                   'date_start'     : values['date_issued'],
                   'date_stop'      : values['date_expired'],
                   'date_created'   : time.strftime('%Y-%m-%d %H:%M:%S'),
                   }
        id_history = self.pool.get('document.history.line').create(cr, uid, history)
        return ids
    
    def write(self, cr, uid, ids, vals, context=None):
        write = super(ir_attachment, self).write(cr, uid, ids, vals, context)
        doc = self.pool.get("ir.attachment").browse(cr, uid, ids)[0]
        history_id = self.pool.get("document.history.line").search(cr, uid, [('doc_id', '=', ids[0])])[0]
        history = {
                 'name'         : doc['name'],
                 'partner'      : doc['partner_id']['id'],
                 'date_start'   : doc['date_issued'],
                 'date_stop'    : doc['date_expired'],
                 'date_renew'   : time.strftime('%Y-%m-%d %H:%M:%S'),
                 }
        self.pool.get("document.history.line").write(cr, uid, history_id, history, context)
        return write
    
    def unlink(self, cr, uid, ids, context=None):
        history_id = self.pool.get("document.history.line").search(cr, uid, [('doc_id', '=', ids[0])])
        unlink = super(ir_attachment, self).unlink(cr, uid, ids, context=context)
        history = {
                 'date_deleted' : time.strftime('%Y-%m-%d %H:%M:%S'),
                 }
        self.pool.get("document.history.line").write(cr, uid, history_id, history)
        return unlink
    
ir_attachment()

#===============================================================================
# Document History [END]
#===============================================================================



#===============================================================================
# Shareholder History [START]
#===============================================================================

class shareholder_history_line(osv.osv):
    _name = "shareholder.history.line"
    _columns = {
                'name'                  : fields.char('Share certificates', size=128),
                'shareholder'           : fields.char('Shareholder', size=128),
                'shareholder_id'        : fields.integer('Shareholder ID'),
                'company'               : fields.char('Company', size=128),
                'total_share'           : fields.integer('Total share'),
                'total_share_value'     : fields.integer('Total share value'),
                'total_share_percent'   : fields.float('Total share (%)', digits=(3, 2)),
                'date_start'            : fields.date('Start date'),
                'date_stop'             : fields.date('End date'),
                'date_created'          : fields.datetime('Created'),
                'date_edited'           : fields.datetime('Last edited'),
                'date_deleted'          : fields.datetime('Deleted'),
                }
shareholder_history_line()

class res_partner_shareholders(osv.osv):
    _inherit = "res.partner.shareholders"
    
    def create(self, cr, uid, values, context=None):
        ids = super(res_partner_shareholders, self).create(cr, uid, values, context)
        shareholder = self.pool.get("res.partner.shareholders").browse(cr, uid, ids)
        company = self.pool.get("res.partner").browse(cr,uid,values['name'])
        
        print "shareholder_name", shareholder
        print "values", values
        
        if values['is_person'] == 1:
            contact = self.pool.get('res.partner.contact').browse(cr, uid, values['contact'])
            if contact['first_name']:
                contact_name = '%s' % contact['first_name'] + " " + contact['name'],
            else:
                contact_name = contact['name']
            shareholder_name = str(contact_name)[3:-3]
        else:
            shareholder_name = shareholder['share_owning']['name']
            
        history = {
                   'name'               : values['share_certificates'],
                   'shareholder'        : shareholder_name,
                   'shareholder_id'     : ids,
                   'company'            : company['name'],
                   'total_share'        : shareholder['share'],
                   'total_share_value'  : shareholder['share_value'],
                   'total_share_percent': shareholder['share_percent'],
                   'date_start'         : shareholder['start_date'],
                   'date_stop'          : shareholder['stop_date'],
                   'date_created'       : time.strftime('%Y-%m-%d %H:%M:%S'),
                   }
        history_id = self.pool.get('shareholder.history.line').create(cr,uid,history,context)
        print "history", history
        return ids
    
    def unlink(self, cr, uid, ids, context=None):
        unlink = super(res_partner_shareholders, self).unlink(cr, uid, ids, context)
        history_id = self.pool.get("shareholder.history.line").search(cr, uid, [('shareholder_id', '=', ids[0])])
        history = {
                 'date_deleted' : time.strftime('%Y-%m-%d %H:%M:%S'),
                 }
        self.pool.get("shareholder.history.line").write(cr, uid, history_id, history)
        return unlink
res_partner_shareholders()

#===============================================================================
# Shareholder History [END]
#===============================================================================
