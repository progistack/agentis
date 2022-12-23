from datetime import datetime

import pytz

from odoo import models, fields, api


class InheritAccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    @api.model
    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    num_transaction = fields.Char(string='N° trasaction')
    bank_reception = fields.Many2one('agentis.bank', string='Banque Réceptrice')
    methode_payment = fields.Selection(
        [('virement', 'Virement'), ('versement', 'Versement'), ('misedispo', 'Mise à Disposition'),
         ('chequebarre', 'Chèque Barré'), ('chequenonbarre', 'Chèque Non Barré'), ('espece', 'Espèce'),
         ('prele', 'Prélèvement'), ('traite', 'Traite'), ('finance', 'Financement')],
        "Méthode de paiément", default='virement')
    type_operation = fields.Selection([('local', 'Local'), ('inter', 'International')], "Type d'operation",
                                      default='local')
    date_escompte = fields.Date(string="Date d'escompte")
    origin_fond = fields.Many2many('origin.fond', store=True, string='origine des fonds', readonly=False)
    partner_id = fields.Many2one('res.partner', string='Partenaire:')
    libele = fields.Text(string='Libelé:', default='aucun')
    chantier_id = fields.Many2one('account.analytic.account', string="Projet")

    def _create_payment_vals_from_wizard(self):
        res = super(InheritAccountPaymentRegister, self)._create_payment_vals_from_wizard()
        move = self.env['account.move'].search([('id', '=', self._context['active_id'])])
        for line in move.invoice_line_ids:
            self.chantier_id = line.analytic_account_id
        res.update({
                'methode_payment': self.methode_payment,
                'type_operation': self.type_operation,
                'origin_fond': self.origin_fond,
                'ref': self.num_transaction,
                'bank_reception': self.bank_reception.id,
                'libele': self.libele,
                'chantier_id': self.chantier_id.id,
                'from_popup': True,
            })
        return res

    def action_create_payments(self):
        res = super(InheritAccountPaymentRegister, self).action_create_payments()

        return res

