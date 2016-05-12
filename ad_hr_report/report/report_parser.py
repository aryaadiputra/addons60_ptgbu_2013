from report import report_sxw
from osv import osv
import pooler
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tools.translate import _

class report_hr_parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_hr_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_dept':self._get_department,
            'get_section':self._get_section,
            'get_employee':self._get_employee,
            'get_job_level':self._get_job_level,
            'get_work_location':self._get_work_location,
            'get_gender':self._get_gender,
            'get_contract':self._get_contract,
            'get_bagian':self._get_bagian,
            'get_age':self._get_age,
            'get_work_age':self._get_work_experiences,
        })
    def _get_age(self):
        return [
                {'value':[('age','>=',20),('age','<',30)],'name':'20 - 29 years old'},
                {'value':[('age','>=',30),('age','<',40)],'name':'30 - 39 years old'},
                {'value':[('age','>=',40),('age','<',50)],'name':'40 - 49 years old'},
                {'value':[('age','>=',50)],'name':'>= 50 years old'},
                ]
    
        
    
    def _get_work_experiences(self):
        return [
                {'value':[('doj','>',(datetime.today()-relativedelta(years= 1)).strftime('%Y-%m-%d'))],'name':'< 1 tahun'},
                {'value':[('doj','<=',(datetime.today()-relativedelta(years= 1)).strftime('%Y-%m-%d')),('doj','>',(datetime.today()-relativedelta(years= 5)).strftime('%Y-%m-%d'))],'name':'1-5 tahun'},
                {'value':[('doj','<=',(datetime.today()-relativedelta(years= 5)).strftime('%Y-%m-%d')),('doj','>',(datetime.today()-relativedelta(years= 10)).strftime('%Y-%m-%d'))],'name':'5-10 tahun'},
                {'value':[('doj','<=',(datetime.today()-relativedelta(years= 10)).strftime('%Y-%m-%d')),('doj','>',(datetime.today()-relativedelta(years= 15)).strftime('%Y-%m-%d'))],'name':'10-15 tahun'},
                {'value':[('doj','<=',(datetime.today()-relativedelta(years= 15)).strftime('%Y-%m-%d')),('doj','>',(datetime.today()-relativedelta(years= 20)).strftime('%Y-%m-%d'))],'name':'15-20 tahun'},
                {'value':[('doj','<=',(datetime.today()-relativedelta(years= 20)).strftime('%Y-%m-%d')),('doj','>',(datetime.today()-relativedelta(years= 25)).strftime('%Y-%m-%d'))],'name':'20-25 tahun'},
                {'value':[('doj','<=',(datetime.today()-relativedelta(years= 25)).strftime('%Y-%m-%d')),('doj','>',(datetime.today()-relativedelta(years= 30)).strftime('%Y-%m-%d'))],'name':'25-30 tahun'},
                {'value':[('doj','<=',(datetime.today()-relativedelta(years= 30)).strftime('%Y-%m-%d'))],'name':'>30 tahun'},
                ]

        
    def _get_bagian(self):
        return ['core','subcore','support']
    
    def _get_contract(self,contract_ids=None):
        value=False
        if contract_ids:
            value =self.pool.get('hr.contract').browse(self.cr,self.uid,contract_ids)
            if not value:
                value =self.pool.get('hr.contract').browse(self.cr,self.uid,[contract_ids])
        return value    
        
    def _get_gender(self):
        return ['male','female']
    
    def _get_work_location(self):
        return ['pekanbaru','jakarta','pedada','west','zamrud']
    
    def _get_job_level(self):
        value=False
        job_level_ids=self.pool.get('hr.job.level').search(self.cr,self.uid,[])
        if job_level_ids:
            value =self.pool.get('hr.job.level').browse(self.cr,self.uid,job_level_ids)
        return value
    
    def _get_department(self,dep_ids=None,section_ids=None,bagian=None):
        value=False
        if dep_ids:
            value =self.pool.get('hr.department').browse(self.cr,self.uid,dep_ids)
            if not value:
                value =self.pool.get('hr.department').browse(self.cr,self.uid,[dep_ids])
        if bagian:
            department_ids =self.pool.get('hr.department').search(self.cr,self.uid,[('id','in',dep_ids),('bagian','=',bagian)])
            value = self.pool.get('hr.department').browse(self.cr,self.uid,department_ids) 
        return value
    
    def _get_section(self,dep_id=None,section_id=None):
        value=False
        if dep_id and section_id:
            section_ids=self.pool.get('hr.section').search(self.cr,self.uid,[('department','in',[dep_id]),('id','in',section_id)])
            if not section_ids:
                section_ids=self.pool.get('hr.section').search(self.cr,self.uid,[('department','=',dep_id),('id','in',section_id)])
            value =self.pool.get('hr.section').browse(self.cr,self.uid,section_ids)
        elif section_id and not dep_id:
            section_ids=self.pool.get('hr.section').search(self.cr,self.uid,[('id','in',section_id)])
            value =self.pool.get('hr.section').browse(self.cr,self.uid,section_ids)
        return value
    
    def _get_employee(self,active,dep_id=None,section_id=None,job_level=None,work_location=None,gender=None,age=None,we=None,sort=None):
        #print "================================",gender
        
        value=False
        ctx = []
        temp=False
        if dep_id:
            if dep_id != "kosong":
                if len(dep_id)>1:
                    temp=('department_id','in',dep_id)
                else:
                    temp=('department_id','=',dep_id)
            else:
                temp=('department_id','is',False)
            ctx.append(temp)
        if section_id:
            if section_id != "kosong":
                if len(section_id)>1:
                    temp=('section','in',section_id)
                else:
                    temp=('section','=',section_id)
            else:
                temp=('section','=',False)
            ctx.append(temp)
        if job_level:
            if len(job_level)>1:
                temp=('current_job_level','in',job_level)
            else:
                temp=('current_job_level','=',job_level)
            ctx.append(temp)
        if work_location:
            if len(work_location)>1:
                temp=('work_location','in',work_location)
            else:
                temp=('work_location','=',work_location[0])
            ctx.append(temp)
        if gender:
            if len(gender)>1:
                temp=('gender','in',gender)
            else:
                temp=('gender','=',gender[0])
            ctx.append(temp)
        if age:
            for a in age:
                ctx.append(a)
        if we:
            for w in we:
                ctx.append(w)
        if active=='active':
            temp=('active','=',True)
            ctx.append(temp)
        elif active=='inactive':
            temp=('active','=',False)
            ctx.append(temp)
            
        #print "CTX ++++++++++++++++>>>>>",ctx
            
        if sort:
            emp_ids=self.pool.get('hr.employee').search(self.cr,self.uid,ctx,order=sort)
        else:
            emp_ids=self.pool.get('hr.employee').search(self.cr,self.uid,ctx,order='section,current_job_level DESC',)
        if emp_ids:
            value=self.pool.get('hr.employee').browse(self.cr,self.uid,emp_ids)
        return value
    
    
        
    
report_sxw.report_sxw('report.report.hr.custom.department.list', 'hr.report.wizard', 'addons/ad_hr_report/report/employee_department_list.mako', parser = report_hr_parser, header = True)
report_sxw.report_sxw('report.report.hr.custom.section.list', 'hr.report.wizard', 'addons/ad_hr_report/report/employee_section_list.mako', parser = report_hr_parser, header = True)
report_sxw.report_sxw('report.report.hr.custom.joblevel.list', 'hr.report.wizard', 'addons/ad_hr_report/report/employee_joblevel_list.mako', parser = report_hr_parser, header = True)
report_sxw.report_sxw('report.report.hr.custom.location.list', 'hr.report.wizard', 'addons/ad_hr_report/report/employee_location_list.mako', parser = report_hr_parser, header = True)
report_sxw.report_sxw('report.report.hr.custom.gender.list', 'hr.report.wizard', 'addons/ad_hr_report/report/employee_gender_list.mako', parser = report_hr_parser, header = True)
report_sxw.report_sxw('report.report.hr.custom.bagian.list', 'hr.report.wizard', 'addons/ad_hr_report/report/employee_bagian_list.mako', parser = report_hr_parser, header = True)
report_sxw.report_sxw('report.report.hr.custom.age.list', 'hr.report.wizard', 'addons/ad_hr_report/report/employee_age_list.mako', parser = report_hr_parser, header = True)
report_sxw.report_sxw('report.report.hr.custom.workexperience.list', 'hr.report.wizard', 'addons/ad_hr_report/report/employee_workexperience_list.mako', parser = report_hr_parser, header = True)
report_sxw.report_sxw('report.report.hr.custom.contract.list', 'hr.report.wizard', 'addons/ad_hr_report/report/employee_contract_list.mako', parser = report_hr_parser, header = True)

