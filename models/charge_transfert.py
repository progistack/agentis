from datetime import datetime

import pytz

from odoo import fields, api, models


class ChargeTransfert(models.Model):
    _name = 'charge.transfer'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']

    @api.model
    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    partner_id_init = fields.Many2one('res.partner', string='Client Initial')
    partner_id_final = fields.Many2one('res.partner', string='Client Final')
    name = fields.Char(string='Description')
    chantier_id_init = fields.Many2one('account.analytic.account', string='Chantier Initial')
    chantier_id_final = fields.Many2one('account.analytic.account', string='Chantier Final')
    date = fields.Date(string='Date', default=_default_time_utc)

    def charge_transfer(self):
        pass
