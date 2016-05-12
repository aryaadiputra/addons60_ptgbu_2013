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
import netsvc
from pdf_ext import fill_pdf
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
import locale

class external_pdf(render):

    def __init__(self, pdf):
        render.__init__(self)
        self.pdf = pdf
        self.output_type='pdf'

    def _render(self):
        return self.pdf


class report_custom(report_int):
    
    def create(self, cr, uid, ids, datas, context=None):
        pool    = pooler.get_pool(cr.dbname)
        form    = pool.get('form.f2a').browse(cr,uid,ids[0])
                
        result = {}
        jsostek = form.jamsostek
        print jsostek, form
        
        result['npp']                           = form.npp
        result['com_name']                      = form.name.name
        result['unit_kerja_nama']               = form.nuk
        result['period_id']                     = form.period_id
        
        i=1
        for member in jsostek:
            if i<10:
                seq     = '0'+str(i)
            else:
                seq     = str(i)
            kpj     = 'emp_no_kpj_'+seq
            nik     = 'emp_nik_'+seq
            nama    = 'emp_nama_'+seq
            ttl     = 'emp_ttl_'+seq
            upah    = 'emp_upah_'+seq
            jkk     = 'emp_iuran_jkk_'+seq
            jkm     = 'emp_iuran_jkm_'+seq
            jpk     = 'emp_iuran_jpk_'+seq
            jht_tk  = 'emp_iuran_jhttk_'+seq
            jht     = 'emp_iuran_jht_'+seq
            total   = 'emp_total_iuran_'+seq
            
            result[kpj]     = member.jnumber
            result[nik]     = member.name.nik
            result[nama]    = member.name.name
            
            birthday        = datetime.fromtimestamp(time.mktime(time.strptime(member.name.birthday,"%Y-%m-%d")))
            birthday        = tools.ustr(birthday.strftime('%d/%m/%Y'))
            result[ttl]     = birthday
            
            contract_ids    = pool.get('hr.contract').search(cr,uid,[('employee_id','=',member.name.id)])
            if len(contract_ids)==0:
                raise osv.except_osv(_('No Contract Found!'), _('No contract found for one of this employee!\nPlease create contract for the employee first.'))
            else:
                contract        =pool.get('hr.contract').browse(cr,uid,contract_ids[0])
                
            locale.setlocale(locale.LC_ALL, 'en_AU.utf8')    
            result[upah]    = locale.format('%.2f', contract.wage, 1)
            result[jkk]     = locale.format('%.2f',member.jkk_amount, 1) or "-"
            result[jkm]     = locale.format('%.2f',member.jk_amount, 1) or "-"
            result[jpk]     = locale.format('%.2f',member.jpk_amount, 1) or "-"
            result[jht_tk]  = locale.format('%.2f',member.jht_amount, 1) or "-"
            result[jht]     = locale.format('%.2f',member.jht_amount, 1) or "-"
            result[total]   = locale.format('%.2f',member.total, 1) or "-"
            
            i=i+1
        
        try:
            tmp_file = tempfile.mkstemp(".pdf")[1]
            try:
                fill_pdf(addons.get_module_resource('ad_hr_jamsostek_form','report','pdf','f2a.pdf'), tmp_file, result)
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

report_custom('report.jamsostek.f2a.print')

class form_f2a(osv.osv):
    _inherit    = "form.f2a"
    
    def print_form_f2a(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids',[])
        data = {}
        data['form'] = {}
        data['ids'] = active_ids
        data['form']['name'] = self.browse(cr, uid, ids)[0].name
        return { 'type': 'ir.actions.report.xml', 'report_name': 'jamsostek.f2a.print', 'datas': data, 'parser':form_f2a}
    
form_f2a()
