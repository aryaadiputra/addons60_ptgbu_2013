# -*- coding: utf-8 -*-
from __future__ import with_statement
from osv import osv, fields
import pooler
import tools
from tools.translate import _
from report.render import render
from report.interface import report_int
import addons
import tempfile
import os

class external_pdf(render):

    def __init__(self, pdf):
        render.__init__(self)
        self.pdf = pdf
        self.output_type='pdf'

    def _render(self):
        return self.pdf


class report_custom(report_int):

    def create(self, cr, uid, ids, datas, context=None):

        pool = pooler.get_pool(cr.dbname)
        taxobj = pool.get('account.tax.code')

        if context is None:
            context = {}

        #code_ids = taxobj.search(cr, uid, [('parent_id','child_of',[datas['form']['tax_code_id']])])
        code_ids = taxobj.search(cr, uid, [("code","like","PP30_")])

        result = {}
        for t in taxobj.browse(cr, uid, code_ids, {'period_id': datas['form']['period_id']}):
            if str(t.code):
                result['case_'+str(t.code)] = '%.2f' % (t.sum_period or 0.0, )
        user = pool.get('res.users').browse(cr, uid, uid, context)

        partner = user.company_id.partner_id
        result['p1_npwp_1'] = user.company_id.npwp[:2]
        result['p1_npwp_2'] = user.company_id.npwp[3:6]
        result['p1_npwp_3'] = user.company_id.npwp[7:10]
        result['p1_npwp_4'] = user.company_id.npwp[11:12]
        result['p1_npwp_5'] = user.company_id.npwp[13:16]
        result['p1_npwp_6'] = user.company_id.npwp[17:20]
        result['p1_nama_pkp'] = user.company_id.name.upper()
        result['info_name'] = user.company_id.name
        result['info_vatnum'] = partner.vat
        result['p1_jenis_usaha'] = "PERKEBUNAN"

        if partner.address:
            phone = partner.address[0].phone
            if phone:
                
                result['p1_telp_1'] = phone
                result['p1_telp_2'] = phone
                
            result['info_address'] = partner.address[0].street
            result['info_address2'] = (partner.address[0].zip or '') + ' ' + (partner.address[0].city or '')
        try:
            tmp_file = tempfile.mkstemp(".pdf")[1]
            try:
                tools.pdf_utils.fill_pdf(addons.get_module_resource('ad_hr_indonesia','report','pdf','spt_pph2126-1721.pdf'), tmp_file, result)
                with open(tmp_file, "r") as ofile:
                    self.obj = external_pdf(ofile.read())
            finally:
                try:
                    os.remove(tmp_file)
                except:
                    pass # nothing to do
            self.obj.render()
            return (self.obj.pdf, 'pdf')
        except Exception:
            raise osv.except_osv(_('pdf not created !'), _('Please check if package pdftk is installed!'))

report_custom('report.spt.pph2126.1721.report.print')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
