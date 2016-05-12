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

from osv import osv, fields

class res_religion(osv.osv):
    
    _name = "res.religion"
    _description= 'Description of religion'

    _columns = {
        'name' : fields.char('Religion', size=20, required = True, help="Religion name"),
        }

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'Religion name must be unique !')
    ]

    def copy(self, cr, uid, id, default={}, context=None):
        previous_name = self.browse(cr, uid, id, context=context)
        if not default:
            default = {}
        default = default.copy()
        default['name'] = (previous_name['name'] or '') + '(copy)'
        print default['name']
        return super(res_religion, self).copy(cr, uid, id, default, context=context)

res_religion()

class hr_religion(osv.osv):
    """ HR Address Contact """
    _inherit = "hr.employee"
    _columns = {
        'religion_id': fields.many2one('res.religion', 'Religion', help='Employee religion'),
        }

hr_religion()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: