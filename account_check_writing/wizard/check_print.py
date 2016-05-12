# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from osv import osv,fields
from tools.translate import _
import netsvc
LOGGER = netsvc.Logger()



class print_check(osv.osv_memory):
    _name = "print.check"
    _description = "Print Check"
    _columns = {
                'name': fields.char('Next Check Number',size=32, help='Next check number'),
                'nxt_seq': fields.char('Next Check Number',size=32, help='Next check number'),
                'new_no': fields.integer('Update Check Number', help= 'Enter new check number here if you wish to update'),
                'preprint_msg': fields.text('Message'),
                'status': fields.selection([    ('voided', 'Voided'),
                                                ('stop_pay', 'Stop Pay Placed'),
                                                ('lost', 'Lost'),
                                                ('unk', 'Unknown')], 'Status'),
                'pre_printed': fields.boolean('Pre Printed'),
                'state':fields.selection([      ('print', 'print'),
                                                ('printed_reprint', 'printed_reprint'),
                                                ('printed', 'printed'),
                                                ('reprint_new', 'reprint_new'),
                                                ('reprint', 'reprint'),
                                                ('update_check_no', 'update_check_no'),
                                                ('do_update', 'do_update'),
                                                ('do_action', 'do_action'),
                                                ('top', 'top'),
                                                ('middle', 'middle'),
                                                ('bottom', 'bottom'),], 'State'),
                'print_new': fields.boolean('Print a New Check'),
                'reprint': fields.boolean('Reprint existing check'),
                'update_check_no': fields.boolean('Update Supplier Payment’s Check No'),
                
                }
    def get_id(self, cr, uid, sequence_id, test='id', context=None):
        '''
        Function to find next sequence number
        '''
        seq_pool = self.pool.get('ir.sequence')
        assert test in ('code','id')
        company_id = self.pool.get('res.users').read(cr, uid, uid, ['company_id'], context=context)['company_id'][0] or None
        cr.execute('''SELECT id, number_next, prefix, suffix, padding
                      FROM ir_sequence
                      WHERE %s=%%s
                       AND active=true
                       AND (company_id = %%s or company_id is NULL)
                      ORDER BY company_id, id
                      FOR UPDATE NOWAIT''' % test,
                      (sequence_id, company_id))
        res = cr.dictfetchone()
        if res:
            if res['number_next']:
                return (seq_pool._process(res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + seq_pool._process(res['suffix']),res['number_next'])
            else:
                return (seq_pool._process(res['prefix']) + seq_pool._process(res['suffix']),0)
        return False
    def _get_nxt_no(self, cr, uid, context=None):
        '''
        Function to find next sequence number and update sequence
        '''
        pool = self.pool
        if context.get('active_ids'):
            voucher_id = pool.get('account.voucher').browse(cr, uid, context.get('active_ids'), context=context)[0]
            if not voucher_id.journal_id.check_sequence:
                raise osv.except_osv(_('Warning!'), _('Please add "Check Sequence" for journal %s.'%str(voucher_id.journal_id.name)))
            res = self.get_id(cr, uid,voucher_id.journal_id.check_sequence.id , test='id')
            return res and res[0]
        else:
            return False
    def _get_new_no(self, cr, uid, context=None):
        '''
        Function to get the next number used to generate sequence
        '''
        pool = self.pool
        voucher_id = pool.get('account.voucher').browse(cr, uid, context.get('active_ids')[0], context=context)
        res = self.get_id(cr, uid,voucher_id.journal_id.check_sequence.id , test='id')
        return res and res[1]
    
    def _get_state(self, cr, uid, context=None):
        '''
        Function to initialise state
        '''
        pool = self.pool
        state = 'print'
        if not (context.get('active_model') == 'account.voucher' and context.get('active_ids')):
            raise osv.except_osv(_('Warning!'), _('Wrong model or unable to find active ids'))
        
        for voucher_id in pool.get('account.voucher').browse(cr, uid, context.get('active_ids'), context=context):
            if voucher_id.chk_seq and voucher_id.journal_id.use_preprint_check:
                state = 'printed'
            elif voucher_id.chk_seq and state != 'printed':
                state = 'printed_reprint'
            if voucher_id.state != 'posted':
                raise osv.except_osv(_('Warning!'), _('Payment is not posted. Please Validate Payment First!'))
            if not voucher_id.journal_id.check_sequence:
                raise osv.except_osv(_('Warning!'), _('Please add "Check Sequence" for journal %s.'%str(voucher_id.journal_id.name)))  
        return state
    def _get_pre_printed(self, cr, uid, context=None):
        '''
        Function to check whether the check is pre printed or not
        '''
        pool = self.pool
        if not (context.get('active_model') == 'account.voucher' and context.get('active_ids')):
            raise osv.except_osv(_('Warning!'), _('Wrong model or unable to find active ids'))
        for voucher_id in pool.get('account.voucher').browse(cr, uid, context.get('active_ids'), context=context):
            if voucher_id.journal_id.use_preprint_check:
                return True
        return False
    def _get_msg(self, cr, uid, context=None):
        '''
        Functiont to initialize preprint_msg
        '''
        pool = self.pool
        msg1='This Payment has already been paid with check:\n'
        msg2='These Payments have already been paid with checks:\n'
        msg3='Some of these Payments have already been paid with checks:\n'
        chk_nos=[]
        voucher_ids = pool.get('account.voucher').browse(cr, uid, context.get('active_ids'), context=context)
        for voucher in voucher_ids:
            if voucher.chk_seq:
                chk_nos.append(str(voucher.chk_seq))
        if len(chk_nos)==1:
            msg = msg1+str(chk_nos[0])
        elif len(chk_nos) == len(context.get('active_ids')):
            msg = msg2+'\n'.join(chk_nos)
        else:
            msg = msg3+'\n'.join(chk_nos)
        if chk_nos:
            return msg
        else:
            return ''
    
    _defaults = {
                'name':'Check sequence',
                'nxt_seq':_get_nxt_no,
                'new_no':_get_new_no,
                'preprint_msg': _get_msg,
                'pre_printed': _get_pre_printed,
                'state':_get_state
                }
    def check_option(self, cr, uid, ids, context={}):
        '''
        Function to check the option if check is already printed 
        '''
        data = self.browse(cr,uid,ids[0],context=context)
        
        if data.print_new:
            msg =  'What happened to the existing check no '+str( data.preprint_msg.split(':\n')[1]).replace('\n',', ')+'?'
            self.write(cr,uid,ids,{'preprint_msg':msg,'state':'reprint_new'})
        
        elif data.reprint:
            company_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
            if company_obj.check_layout == 'top':
                report_name = 'account.print.check.top'
            if company_obj.check_layout == 'middle':
                report_name = 'account.print.check.middle'
            if company_obj.check_layout == 'bottom':
                report_name = 'account.print.check.bottom'
            
            return {
            'type': 'ir.actions.report.xml',
            'report_name':report_name,
            'datas': {
                    'model':'account.voucher',
                    'id': context.get('active_ids') and context.get('active_ids')[0] or False,
                    'ids': context.get('active_ids') and context.get('active_ids') or [],
                    'report_type': 'pdf'
                },
            'nodestroy': False
            }
        elif data.update_check_no:
            print 'updating check no'
            msg =  'What happened to the existing check no '+str( data.preprint_msg.split(':\n')[1]).replace('\n',', ')+'?'
            self.write(cr,uid,ids,{'preprint_msg':msg,'state':'update_check_no'})
            
            
        return {'nodestroy':True}
    
    
    
    def get_nxt_seq(self, cr, uid, check_sequence_id, test='id', context={}):
        '''
        Function to find the next check number without conflict
        '''
        next_seq = pool.get('ir.sequence').get_id(cr, uid, voucher.journal_id.check_sequence.id, test='id', context=context)
        while(pool.get('check.log').search(cr,uid,[('check_no','=',next_seq)])):
            next_seq = pool.get('ir.sequence').get_id(cr, uid, voucher.journal_id.check_sequence.id, test='id', context=context)
        return next_seq
    
    def print_check(self, cr, uid, ids, context={}):
        '''
        Function to print check
        '''
        if not context.get('active_ids'): return []
        pool = self.pool
        seq = {}
        voucher_ids = pool.get('account.voucher').browse(cr, uid, context.get('active_ids'), context=context)
        data = self.browse(cr,uid,ids[0],context=context)
        for voucher in voucher_ids:
            if voucher.journal_id.check_sequence:
                seq[voucher.journal_id.check_sequence.id] = True
            else:
                raise wizard.except_wizard(_('Warning'), _('Please add "Check Sequence" for journal %s.'%str(voucher.journal_id.name)))
        for seq_id in seq.keys():
            nxt_no = pool.get('ir.sequence').read(cr, uid, seq_id,['number_next'],context=context)['number_next']
            #if nxt_no < data.new_no:
            pool.get('ir.sequence').write(cr, uid, [seq_id],{'number_next':data.new_no}, context=context)
        
        for voucher in voucher_ids:
            next_seq = pool.get('ir.sequence').get_id(cr, uid, voucher.journal_id.check_sequence.id, test='id', context=context)
#            next_seq = get_nxt_seq(cr, uid, voucher.journal_id.check_sequence.id, test='id', context=context)                        #Automatically find next possible check number if conflict occures
            pool.get('account.voucher').write(cr, uid,[voucher.id],{'chk_seq':next_seq,'chk_status':True})
            pool.get('check.log').create(cr, uid,{'name':voucher.id,'status':'active','check_no':next_seq})
        if data.state == 'print':
            
            company_obj = pool.get('res.users').browse(cr, uid, uid, context=context).company_id
            if company_obj.check_layout == 'top':
                report_name = 'account.print.check.top'
            if company_obj.check_layout == 'middle':
                report_name = 'account.print.check.middle'
            if company_obj.check_layout == 'bottom':
                report_name = 'account.print.check.bottom'
            return {
                'type': 'ir.actions.report.xml',
                'report_name':report_name,
                'datas': {
                        'model':'account.voucher',
                        'id': context.get('active_ids') and context.get('active_ids')[0] or False,
                        'ids': context.get('active_ids') and context.get('active_ids') or [],
                        'report_type': 'pdf'
                    },
                'nodestroy': False
                }
        else:
            return {}
        
    def onchange_chkbx(self, cr, uid, ids, value, field, context=None):
        '''
        Function to update check box print_new, reprint and update_check_no
        '''
        ret={
             'print_new':False,
             'reprint':False,
             'update_check_no':False,
             }
        if value:
            ret[field] = True
        return {'value':ret}
    
    def update_no(self, cr, uid, ids, context={}):
        '''
        Function to update check log status
        '''
        data = self.browse(cr,uid,ids[0],context=context)
        pool = self.pool
        voucher_ids = pool.get('account.voucher').browse(cr, uid, context.get('active_ids'), context=context)
        if data.status:
            for voucher in voucher_ids:
                if voucher.chk_seq:
                    chk_log_ids = pool.get('check.log').search(cr,uid,[('check_no','=',voucher.chk_seq),('status','=','active')])
                    pool.get('check.log').write(cr,uid,chk_log_ids, {'status':data.status or 'unk'})        
        
        self.write(cr,uid,ids,{'preprint_msg':'','state':'do_update'})
        
        
    def print_new(self, cr, uid, ids, context={}):
        '''
        Function to update check log status
        '''
        data = self.browse(cr,uid,ids[0],context=context)
        pool = self.pool
        voucher_ids = pool.get('account.voucher').browse(cr, uid, context.get('active_ids'), context=context)
        if data.status:
            for voucher in voucher_ids:
                if voucher.chk_seq:
                    chk_log_ids = pool.get('check.log').search(cr,uid,[('check_no','=',voucher.chk_seq),('status','=','active')])
                    pool.get('check.log').write(cr,uid,chk_log_ids, {'status':data.status or 'unk'})        
        
        self.write(cr,uid,ids,{'preprint_msg':'','state':'print'})
print_check()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
