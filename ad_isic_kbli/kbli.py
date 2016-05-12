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

from operator import itemgetter
from tools.translate import _
from osv import fields, osv
import netsvc
import tools
import math

#from tools import float_round, float_is_zero, float_compare
#from tools.translate import _

class kbli_kbli(osv.osv):
    _order = "parent_left"
    _parent_order = "code"
    _name = "kbli.kbli"
    _description = "ISIC (Indonesian Standard Industrial Classification)"
    _parent_store = True
    logger = netsvc.Logger()

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        if context is None:
            context = {}
        pos = 0

        while pos < len(args):

            if args[pos][0] == 'code' and args[pos][1] in ('like', 'ilike') and args[pos][2]:
                args[pos] = ('code', '=like', str(args[pos][2].replace('%', ''))+'%')
            pos += 1

        if context and context.has_key('consolidate_children'): #add consolidated children of accounts
            ids = super(kbli_kbli, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)
            for consolidate_child in self.browse(cr, uid, context['kbli_id'], context=context).child_consol_ids:
                ids.append(consolidate_child.id)
            return ids

        return super(kbli_kbli, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)

    def _get_children_and_consol(self, cr, uid, ids, context=None):
        #this function search for all the children and all consolidated children (recursively) of the given kbli ids
        ids2 = self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        for rec in self.browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
        return ids2 + ids3

    def _get_child_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.child_parent_ids:
                result[record.id] = [x.id for x in record.child_parent_ids]
            else:
                result[record.id] = []

            if record.child_consol_ids:
                for acc in record.child_consol_ids:
                    if acc.id not in result[record.id]:
                        result[record.id].append(acc.id)

        return result

    def _get_level(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        kblis = self.browse(cr, uid, ids, context=context)
        for kbli in kblis:
            level = 0
            if kbli.parent_id:
                obj = self.browse(cr, uid, kbli.parent_id.id)
                level = obj.level + 1
            res[kbli.id] = level
        return res

    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'code': fields.char('Code', size=64, required=True, select=1),
        'type': fields.selection([
            ('category', 'Category'),
            ('main_class', 'Main Class'),
            ('class', 'Class'),
            ('sub_class', 'Sub Class'),
            ('group','Group'),
        ], 'Internal Type', required=True, help="This type is used to differentiate types with "\
            "special effects in OpenERP: view can not have entries, consolidation are kblis that "\
            "can have children kblis for multi-company consolidations, payable/receivable are for "\
            "partners kblis (for debit/credit computations), closed for depreciated kblis."),
        'parent_id': fields.many2one('kbli.kbli', 'Parent', ondelete='cascade', domain=[('type','<>','group')]),
        'child_parent_ids': fields.one2many('kbli.kbli','parent_id','Children'),
        'child_consol_ids': fields.many2many('kbli.kbli', 'kbli_kbli_consol_rel', 'child_id', 'parent_id', 'Consolidated Children'),
        'child_id': fields.function(_get_child_ids, method=True, type='many2many', relation="kbli.kbli", string="Child Accounts"),
        'shortcut': fields.char('Shortcut', size=12),
        'note': fields.text('Note'),
        'active': fields.boolean('Active', select=2, help="If the active field is set to False, it will allow you to hide the kbli without removing it."),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
        'level': fields.function(_get_level, string='Level', method=True, store=True, type='integer'),
    }

    _defaults = {
        'active': True,
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        obj_self = self.browse(cr, uid, ids[0], context=context)
        p_id = obj_self.parent_id and obj_self.parent_id.id
        if (obj_self in obj_self.child_consol_ids) or (p_id and (p_id is obj_self.id)):
            return False
        while(ids):
            cr.execute('SELECT DISTINCT child_id '\
                       'FROM kbli_kbli_consol_rel '\
                       'WHERE parent_id IN %s', (tuple(ids),))
            child_ids = map(itemgetter(0), cr.fetchall())
            c_ids = child_ids
            if (p_id and (p_id in c_ids)) or (obj_self.id in c_ids):
                return False
            while len(c_ids):
                s_ids = self.search(cr, uid, [('parent_id', 'in', c_ids)])
                if p_id and (p_id in s_ids):
                    return False
                c_ids = s_ids
            ids = child_ids
        return True

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive kblis.', ['parent_id'])
    ]
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        try:
            if name and str(name).startswith('type:'):
                type = name.split(':')[1]
                args += [('type', '=', type)]
                name = False
        except:
            pass
        if name:
            ids = self.search(cr, user, [('code', '=like', name+"%")]+args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('shortcut', '=', name)]+ args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit)
            if not ids and len(name.split()) >= 2:
                #Separating code and name of kbli for searching
                operand1,operand2 = name.split(' ',1) #name can contain spaces e.g. OpenERP S.A.
                ids = self.search(cr, user, [('code', operator, operand1), ('name', operator, operand2)]+ args, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' '+name
            res.append((record['id'], name))
        return res

    def copy(self, cr, uid, id, default={}, context=None, done_list=[], local=False):
        kbli = self.browse(cr, uid, id, context=context)
        new_child_ids = []
        if not default:
            default = {}
        default = default.copy()
        default['code'] = (kbli['code'] or '') + '(copy)'
        if not local:
            done_list = []
        if kbli.id in done_list:
            return False
        done_list.append(kbli.id)
        if kbli:
            for child in kbli.child_id:
                child_ids = self.copy(cr, uid, child.id, default, context=context, done_list=done_list, local=True)
                if child_ids:
                    new_child_ids.append(child_ids)
            default['child_parent_ids'] = [(6, 0, new_child_ids)]
        else:
            default['child_parent_ids'] = False
        return super(kbli_kbli, self).copy(cr, uid, id, default, context=context)

    def _check_moves(self, cr, uid, ids, method, context=None):
        account_ids = self.search(cr, uid, [('id', 'child_of', ids)])

        #if self.search(cr, uid, [('id', 'in', account_ids)]):
        #    if method == 'write':
        #        raise osv.except_osv(_('Error !'), _('You cannot deactivate an account that contains account moves.'))
        #    elif method == 'unlink':
        #        raise osv.except_osv(_('Error !'), _('You cannot remove an account which has account entries!. '))
        #Checking whether the account is set as a property to any Partner or not
        #value = 'account.account,' + str(ids[0])
        #partner_prop_acc = self.pool.get('ir.property').search(cr, uid, [('value_reference','=',value)], context=context)
        #if partner_prop_acc:
        #    raise osv.except_osv(_('Warning !'), _('You cannot remove/deactivate an account which is set as a property to any Partner.'))
        
        return True

    def _check_allow_type_change(self, cr, uid, ids, new_type, context=None):
        group1 = ['category']
        group2 = ['main_class']
        group3 = ['class']
        group4 = ['sub_class']
        group5 = ['group']
        for account in self.browse(cr, uid, ids, context=context):
            old_type = account.type
            account_ids = self.search(cr, uid, [('id', 'child_of', [account.id])])
            if (old_type <> new_type):
                raise osv.except_osv(_('Warning !'), _("You cannot change the type of account from '%s' to '%s' type as it contains account entries!") % (old_type,new_type,))
        return True    
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        if 'active' in vals and not vals['active']:
            self._check_moves(cr, uid, ids, "write", context=context)
        if 'type' in vals.keys():
            self._check_allow_type_change(cr, uid, ids, vals['type'], context=context)
        return super(kbli_kbli, self).write(cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None):
        self._check_moves(cr, uid, ids, "unlink", context=context)
        return super(kbli_kbli, self).unlink(cr, uid, ids, context=context)

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

kbli_kbli()

class res_currency(osv.osv):
    _inherit = 'res.currency'
    
    _columns = {
        'rounding': fields.float('Rounding Factor', digits=(12,12)),
    }

#    def round(self, cr, uid, currency, amount):
#        return float_round(amount, precision_rounding=currency.rounding)

#    def compare_amounts(self, cr, uid, currency, amount1, amount2):
#        return float_compare(amount1, amount2, precision_rounding=currency.rounding)

#    def is_zero(self, cr, uid, currency, amount):
#        return False#self.float_is_zero(amount, precision_rounding=currency.rounding)

res_currency()
