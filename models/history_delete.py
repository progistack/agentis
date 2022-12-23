from odoo import fields, models, api, _
from datetime import datetime


class HistoryDelete(models.Model):
    _name = 'history.delete'
    _description = ' historique de suppression'
    _order = 'create_date'

    amount = fields.Float(string='Montant')
    num_caisse = fields.Char(string='Numéro caisse')
    type_caisse = fields.Selection([('manager', 'Caisse secondaire'), ('dga', 'Caisse principale')], ' Type de caisse')
    beneficiaire_employee = fields.Many2one('hr.employee', string='Employé Bénéficiaire')
    beneficiaire_is_fournisseur = fields.Many2one('res.partner', string='Fournisseur Bénéficiaire')
    chantier_id = fields.Many2one('account.analytic.account', string="Projet")
    company_id = fields.Many2one('res.company', string='Entreprise', default=lambda self: self.env.company)
    libele = fields.Char(string='Libellé')
    check_in_out = fields.Selection([('entrer', 'Entrée'), ('sortie', 'Sortie'), ('transfert', 'Transfert de fond')], "type d'operation:")
    date_mvt = fields.Date(string='Date création mvt')


