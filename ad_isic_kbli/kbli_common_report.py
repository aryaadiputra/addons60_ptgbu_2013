# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from lxml import etree

from osv import fields, osv
from tools.translate import _

class kbli_common_report(osv.osv_memory):
    #_inherit = "kbli.kbli"
    _name = "kbli.common.report"
    _description = "KBLI Common Report"
    _columns = {
        'filter' : fields.selection([
                                    ('filter_no', 'No Filters'), 
                                    ('filter_category', 'Category'), 
                                    ('filter_main_class', 'Main Class'),
                                    ('filter_class', 'Class'),
                                    ('filter_sub_class', 'Sub Class'),
                                    ('filter_group', 'Group'),
                                    ], "Filter by", required=True),
        'category_from': fields.many2one('kbli.kbli', 'Start category', domain=[('type','=',('category'))]),
        'category_to': fields.many2one('kbli.kbli', 'End category', domain=[('type','=',('category'))]),
        #'category_from': fields.many2one('kbli.kbli', 'Start category', domain=[('type','in',('category'))]),
        #'category_to': fields.many2one('kbli.kbli', 'End category', domain=[('type','in',('category'))]),
        }

    def onchange_filter(self, cr, uid, ids, filter='filter_no', context=None):
        res = {}
        if filter == 'filter_no':
            res['value'] = {
                            'category_from': False, 'category_to': False, 
                            'main_class_from': False ,'main_class_to': False,
                            'class_from': False ,'class_to': False,
                            'sub_class_from': False ,'sub_class_to': False,
                            'group_from': False ,'group_to': False,
                            }
        '''
        if filter == 'filter_category':
            start_category = end_category = False
            cr.execute(''
                SELECT * FROM kbli_kbli WHERE type='category' ORDER BY code ASC
                        '',)
            types =  [i[0] for i in cr.fetchall()]
            if types and len(types) > 1:
                start_categry = types[0]
                end_category = types[1]
            res['value'] = {'category_from': start_category, 'category_to': end_category, 
                            'main_class_from': False ,'main_class_to': False,
                            'class_from': False ,'class_to': False,
                            'sub_class_from': False ,'sub_class_to': False,
                            'group_from': False ,'group_to': False
                            }
        '''
        return res

    '''
    def _get_kbli(self, cr, uid, context=None):
        kblis = self.pool.get('kbli.kbli').search(cr, uid, [('parent_id', '=', False)], limit=1)
        return kblis and kblis[0] or False

    def _get_fiscalyear(self, cr, uid, context=None):
        now = time.strftime('%Y-%m-%d')
        fiscalyears = self.pool.get('kbli.fiscalyear').search(cr, uid, [('date_start', '<', now), ('date_stop', '>', now)], limit=1 )
        return fiscalyears and fiscalyears[0] or False

    def _get_all_journal(self, cr, uid, context=None):
        return self.pool.get('kbli.journal').search(cr, uid ,[])

    '''

    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        '''    
        if data['form']['filter'] == 'filter_category':
            result['category_from'] = data['form']['category_from']
            result['category_to'] = data['form']['category_to']

        if data['form']['filter'] == 'filter_date':
            result['date_from'] = data['form']['date_from']
            result['date_to'] = data['form']['date_to']
        elif data['form']['filter'] == 'filter_period':
            if not data['form']['period_from'] or not data['form']['period_to']:
                raise osv.except_osv(_('Error'),_('Select a starting and an ending period'))
            result['period_from'] = data['form']['period_from']
            result['period_to'] = data['form']['period_to']
        '''
        return result

    def _print_report(self, cr, uid, ids, data, context=None):
        raise (_('Error'), _('not implemented'))

        #if context is None:
        #    context = {}
        #return { 'type': 'ir.actions.report.xml', 'report_name': 'report.kbli.list.report', 'datas': data}

    def check_report1(self, cr, uid, ids, context=None):

        if context is None: 
            context = {}
        datas = {'ids': context.get('active_ids',[])}
        datas['model'] = 'kbli.kbli'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'kbli.list.report',
            'datas': datas,
        }
        
        '''            
        if context is None:
            context = {}
        
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'kbli.kbli',
             'form': data
        }

        res = self.read(cr, uid, ids, [], context)
        res = res and res[0] or {}
        datas['form'] = res
        datas['model'] = 'kbli.kbli'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'kbli.list.report',
            'datas': datas,
        }
        '''


        '''
        data = {}

        data['ids'] = context.get('active_ids', [])
        #data['model'] = context.get('active_model', 'kbli.common.report')
        data['model'] = 'kbli.common.report'

        data['form'] = self.read(cr, uid, ids, ['category_from',  'category_to'])[0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['used_context'] = used_context
        
        '''
        #return self._print_report(cr, uid, ids, data, context=context)
        #return { 'type': 'ir.actions.report.xml', 'report_name': 'kbli.list.report', 'datas': datas}
        
        '''
        raise osv.except_osv(_('Warning'), _('You tried to %s with a date anterior to another event !\nTry to contact the administrator to correct attendances.')%(data['model'],))

        datas = {'ids' : self.read(cr, uid, ids, [], context)[0]['survey_ids']}
        res = self.read(cr, uid, ids, ['survey_title', 'orientation', 'paper_size',\
                             'page_number', 'without_pagebreak'], context)
        res = res and res[0] or {}
        datas['form'] = res
        datas['model'] = 'survey.print'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'survey.form',
            'datas': datas,
        }
        '''
    def check_report(self, cr, uid, ids, context=None):
        datas = {}
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        datas = {
             'ids': context.get('active_ids',[]),
             'model': 'kbli.kbli',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'kbli.list.report',
            'datas': datas,
            }
        
kbli_common_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
