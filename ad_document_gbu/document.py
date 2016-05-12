from osv import fields, osv
import tools
import time
import datetime
from datetime import date

class document_report_gbu(osv.osv):
    _name = "document.report.gbu"
    _description = "Files detailed by expired"
    _auto = False
    _columns = {
        'id':fields.integer('ID',readonly=True),
        'name': fields.char('Year', size=64, readonly=True),
        'month':fields.selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'), ('06', 'June'),
                                  ('07', 'July'), ('08', 'August'), ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month', readonly=True),
        'user_id':fields.integer('Owner', readonly=True),
        'user':fields.char('User', size=64, readonly=True),
        'directory': fields.char('Directory', size=64, readonly=True),
        'doc_name': fields.char('Document Name', size=64, readonly=True),
        'partner_name':fields.char('Company',size=128, readonly=True),
        'datas_fname': fields.char('File Name', size=64, readonly=True),
        'create_date': fields.datetime('Date Created', readonly=True),
        'date_expired': fields.datetime('Date Expired', readonly=True),
        'change_date': fields.datetime('Modified Date', readonly=True),
        'file_size': fields.integer('File Size', readonly=True),
        'nbr':fields.integer('Number of Files', readonly=True),
        'type':fields.char('Directory Type', size=64, readonly=True),
        'current_date':fields.datetime('Current Date', readonly=True),
     }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'document_report_gbu')
        current_date=time.strftime('%Y-%m-%d %H:%M:%S')
        print "current date",current_date
        cr.execute("""
            CREATE OR REPLACE VIEW document_report_gbu as (
                 SELECT
                     min(f.id) as id,
                     to_char(f.date_expired, 'YYYY') as name,
                     to_char(f.date_expired, 'MM') as month,
                     f.user_id as user_id,
                     f.name as doc_name,
                     p.name as partner_name,
                     u.name as user,
                     count(*) as nbr,
                     d.name as directory,
                     f.datas_fname as datas_fname,
                     f.create_date as create_date,
                     f.date_expired as date_expired,
                     f.file_size as file_size,
                     min(d.type) as type,
                     f.write_date as change_date
                 FROM ir_attachment f
                     left join document_directory d on (f.parent_id=d.id and d.name<>'')
                     inner join res_users u on (f.user_id=u.id)
                     inner join res_partner p on (f.partner_id=p.id)
                 group by to_char(f.date_expired, 'YYYY'), to_char(f.date_expired, 'MM'),f.user_id,f.name,p.name,u.name,d.name,f.datas_fname,f.create_date,f.date_expired,f.file_size,f.write_date,d.type
             )
        """)
document_report_gbu()

class directory_report_gbu(osv.osv):
    _name = "directory.report.gbu"
    _description = "Direcotry"
    _auto = False
    _columns = {
                'name':fields.char('Directory name',size=256,readonly=True),
                'parent':fields.char('Parent Directory', size=256, readonly=True),
                'partner':fields.char('Company',size=64,readonly=True),
                }
    
    def init(self,cr):
        tools.drop_view_if_exists(cr, 'directory_report_gbu')
        cr.execute("""
            CREATE OR REPLACE VIEW directory_report_gbu AS (
                select d.id as id,
                       d.name as name,
                       dd.name as parent,
                       p.name as partner
                    from document_directory d
                    inner join res_partner p on (d.partner=p.id)
                    inner join document_directory dd on (d.parent_id=dd.id)
                    where d.id not in (
                        select parent_id from ir_attachment) and d.filled=true
            )
        """)
directory_report_gbu()