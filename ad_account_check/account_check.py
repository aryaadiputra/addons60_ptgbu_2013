##############################################################################
#
#    Copyright (C) 2009 Almacom (Thailand) Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import time



class account_cheque(osv.osv):
    _name = "account.cheque"
    _columns = {
        "name": fields.char("Cheque No.", size=64, required=True, readonly=True, states={"hold":[("readonly", False)]}, select=2),
        "voucher": fields.char('Number Payment', size=32, required=True, readonly=True, states={"hold":[("readonly", False)]}),
        "type": fields.selection([("receipt", "Receipt"), ("payment", "Payment")], "Type", required=False, readonly=True, states={"hold":[("readonly", False)]}, select=1),
        "method": fields.selection([("paper", "Paper"), ("elec", "Electronic")], "Method", required=False, readonly=True, states={"hold":[("readonly", False)]}, select=1),
        "date": fields.date("Cheque Date", required=False, readonly=True, states={"hold":[("readonly", False)]}, select=2),
        "date_end": fields.date("Cheque End Date", required=True, readonly=True, states={"hold":[("readonly", False)]}, select=2),
        "voucher_id": fields.many2one("account.voucher", "Payment", required=True, readonly=True, states={"hold":[("readonly", False)]}, select=1),
        "partner_id": fields.many2one("res.partner", "Partner", required=True, readonly=True, states={"hold":[("readonly", False)]}, select=1),
        "amount": fields.float("Amount", required=True, readonly=True, states={"hold":[("readonly", False)]}, select=2),
        "bank_id": fields.many2one("res.bank", "Bank", required=False, readonly=True, states={"hold":[("readonly", False)]}, select=2),
        "branch": fields.char("Branch", size=64, readonly=True, states={"hold":[("readonly", False)]}, select=2),
        "state": fields.selection([("hold", "Hold"), ("released", "Released"), ("paid", "Paid"), ("end", "Canceled")], "State", readonly=True, required=True, select=1),
        #"vouch_id": fields.many2one("account.voucher", "Voucher", required=False, readonly=True, states={"hold":[("readonly", False)]}, select=2),
    }

    _defaults = {
        "type": lambda self, cr, uid, context: context.get("type", "payment"),
        "method": lambda * a: "paper",
        "partner_id": lambda self, cr, uid, context: context.get("partner_id", False),
        "state": lambda * a: "hold",
        "date": lambda * a: time.strftime("%Y-%m-%d"),
    }
    def button_released(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"released"})
        return True

    def button_cancel(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"end"})
        return True

    def button_paid(self, cr, uid, ids, context={}):
        for chk in self.browse(cr, uid, ids):
            chk.write({"state":"paid"})
        return True

    def onchange_method(self, cr, uid, ids, method):
        vals = {
            "name": method == "elec" and "1" or "",
        }
        return {"value": vals}
account_cheque()


