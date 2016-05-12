from osv import osv, fields

class resource_calendar(osv.osv):
    _inherit    = "resource.calendar"
    _columns    = {
                   'type'   : fields.selection([('406','40:6'),
                                                ('405','40:5')], 'Type')
                   }
resource_calendar()