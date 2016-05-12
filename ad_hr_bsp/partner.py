from osv import osv,fields

class res_partner_address(osv.osv):
    _inherit    = "res.partner.address"
    def name_get(self, cr, user, ids, context={}):
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, user, ids, ['name','zip','country_id', 'city','partner_id', 'street']):
            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
                res.append((r['id'], r['partner_id'][1]))
            else:
                addr = r['street'] or ''
                if r['city'] or r['country_id']:
                    addr += ', '
                addr += (r['city'] or '') + ' '  + (r['country_id'] and r['country_id'][1] or '')
                if (context.get('contact_display', 'contact')=='partner_address') and r['partner_id']:
                    res.append((r['id'], "%s: %s" % (r['partner_id'][1], addr.strip() or '/')))
                else:
                    res.append((r['id'], addr.strip() or '/'))
        return res
res_partner_address()