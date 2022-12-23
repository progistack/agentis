from datetime import datetime

import pytz

from odoo import fields, models, api


class AgentisContrat(models.Model):
    _name = 'agentis.contrat'

    @api.model
    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    date = fields.Date(string='Date', default=_default_time_utc)
    name_lot = fields.Char(string='N° du Lot', require=True)
    amount = fields.Float(string='Montant', require=True)
    name = fields.Char(string=' Convention/N°Contrat')
    inherit_analytic_id = fields.Many2one('account.analytic.account', string='Id chantier')
    total = fields.Float(string="Total :")
    identify_uni = fields.Char(string='Identifiant Unique')
    amount_separe = fields.Char(string='Montant separe', compute='get_amount_separe', store=True)
    amount_float = fields.Char(string='Montant separe', compute='get_amount_float', store=True)

    @api.depends('amount')
    def get_amount_float(self):
        for contrat in self:
            amount1 = 0
            amount1 = int(amount1 + contrat.amount)
            # '{:,}'.format(1234567890.001).replace(',', ' ')
            contrat.amount_float = '{:,}'.format(amount1).replace(',', ' ')


