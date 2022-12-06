from datetime import datetime

import pytz
from num2words import num2words

from odoo import fields, models, api, _, tools
from odoo.exceptions import ValidationError


class AgentisConsolide(models.Model):
    _name = 'consolidated.box'
    _auto = False
    _order = 'create_date desc'

    create_date = fields.Date(string='Date de création:')
    date = fields.Date(string='Date ')
    libele = fields.Text(string='Libellé:', default='aucun')
    num_facture = fields.Char(string="Numéro facture:")
    nature_payment = fields.Selection([('espece', 'Espèce'), ('autre', 'Autre')], default='espece')
    payment_with = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('autre', 'Autre')],
        "Par l’intermédiaire de:", default='employee')

    payment_with_other = fields.Many2one('res.partner', string="Par l’intermédiaire de:")
    beneficiaire_is = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('dga', 'Caisse Principale'),
         ('autre', 'Autre')],
        "Partenaire:", default='employee')
    beneficiaire_employee = fields.Many2one('hr.employee', string='Employé Bénéficiaire:')
    beneficiaire_is_fournisseur = fields.Many2one('res.partner', string='Fournisseur Bénéficiaire:')
    check_in_out = fields.Selection([('entrer', 'Entrée'), ('sortie', 'Sortie')], "type d'operation:", default='sortie')
    somme = fields.Float(string='Montant payé:', help="Montant de l'opération")
    update = fields.Datetime(string='Mise à jour le:')
    update_by = fields.Many2one('res.users', string='Mise à jour par:')
    visibility = fields.Selection([('0', 'Oui'), ('1', 'Non')],
                                  "à ne pas déclarer ?", default='1')
    name = fields.Char(string="N° de bon")
    chantier_id = fields.Many2one('account.analytic.account', string="Projet:")  # , 'agentis_office_id'
    etat = fields.Boolean(string='etat')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  default=lambda self: self.env.company.currency_id)
    solde = fields.Monetary(string='Solde', compute='get_solde', store=True, currency_field='currency_id')
    somme_in = fields.Float(string=' Somme', compute='get_somme_in')
    somme_out = fields.Float(string='Somme', compute='get_somme_out')
    is_create = fields.Boolean(string='est crée')
    insible_somme = fields.Boolean(string='somme visble ou non')

    donne_a_client = fields.Many2one('res.partner', string='Donné à :')
    donne_a_employe = fields.Many2one('hr.employee', string='Donné à :')
    status = fields.Selection([('brouillon', 'BROUILLONS'), ('attente', 'EN ATTENTE'), ('valide', 'VALIDE')],
                              default='brouillon')
    company_id = fields.Many2one('res.company', string='Société:', required=True, default=lambda self: self.env.company)
    product_id = fields.Many2one(
        'product.product', 'Product', required=False, default=0)
    journal_id = fields.Many2one('account.journal', string='Méthode de paiément:')
    tax_id = fields.Many2one('account.tax', string='Taxe:')
    facture_id = fields.Integer(string='id facture')
    payment_id = fields.Integer(string='id payment')
    date_prevue = fields.Date(string='Date Effective:')
    file = fields.Binary(string="Fichier")
    file_name = fields.Char(string='nom fichier')
    type_caisse = fields.Selection([('dga', 'DGA'), ('manager', 'Office manager'), ('comptable', 'Comptable')],
                                   'Type de caisse')
    total_somme = fields.Float(string='somme total', compute='get_total_somme')
    somme_lettre = fields.Char(string='Somme lettre')
    fideca = fields.Boolean(string='FIDECA')
    origin_fond = fields.Selection([('banque', 'Banque'), ('client', 'Client')], 'Orogine des fonds', default='client')
    total_facture_with_tax = fields.Float(string='Montant avec taxe', compute='get_total_with_tax')
    borderau = fields.Boolean(string='Borderau de livraison')
    num_borderau = fields.Char(string='N° Borderau')
    nature = fields.Char(string="Nature de l'operation")
    note = fields.Text(string='Note')
    somme_char = fields.Char(string='somme en caractere', compute='get_somme_char')
    facture = fields.Boolean(string='Crée une Facture ?')
    amount_facture = fields.Integer(string='somme facture')
    exist_facture_select = fields.Many2one('account.move', string='Selectionner la facture')
    exist_facture = fields.Boolean(string='Facture existante ?')
    hide_boolean = fields.Boolean(string='Cacher fact et pay', default=False)

    """def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        query = '''CREATE OR REPLACE VIEW consolidated_box AS (select min(z.id) AS id,
        z.partner_id AS beneficiaire_is_fournisseur,z.payment_ref AS num_facture,z.num_transaction AS name,z.amount AS somme 
        FROM account_bank_statement_line z GROUP BY z.num_transaction,z.partner_id,z.payment_ref,z.amount) '''
        self._cr.execute(query)"""


