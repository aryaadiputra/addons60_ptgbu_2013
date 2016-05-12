from osv import osv,fields

class jamsostek_form(osv.osv_memory):
    _name    = "jamsostek.form"
    _columns = {
                'form'      : fields.selection([('f1','Form F1'),
                                                ('f1a','Form F1A'),
                                                ('f1b','Form F1B'),
                                                ('f2a','Form F2A'),
                                                ('f3','Form F3'),
                                                ('f3b','Form F3B'),
                                                ('f3c','Form F3C'),
                                                ('f4','Form F4'),
                                                ('f5','Form F5'),
                                                ('f61a','Form F61A'),
                                                ('f6c2','Form F6C2'),
                                                ('fjakons','Form FJakons')],'Form',required=True),
                }
    def open_form(self,cr,uid,ids,context=None):
        jform=self.pool.get('jamsostek.form').browse(cr,uid,ids[0])
        obj     = "form."+jform.form
        title   = "Form "+jform.form.upper()
        res = {
            'domain': str([]),
            'name': title,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': obj,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': context
        }
        return res
jamsostek_form()