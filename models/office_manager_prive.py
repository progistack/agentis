# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError


class OfficeManagerPrive(models.Model):
    _name = 'office.manager.prive'

    create_date = fields.Date(string='Date')
    libele = fields.Text(string='Libellé')
    num_facture = fields.Char(string="Numéro facture")
    nature_payment = fields.Selection([('espece', 'Espèce'), ('autre', 'Autre')], default='espece')
    payment_with = fields.Selection([('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('autre','Autre')],
                                    "Par l’intermédiaire de", default='employee')
    payment_with_employee = fields.Many2one('hr.employee', string='Employé')
    payment_with_other = fields.Many2one('res.partner', string='Client/Fournisseur')
    beneficiaire = fields.Many2one('hr.employee', string='Employé Bénéficiaire')
    beneficiaire_no_client = fields.Many2one('res.partner', string='Autre Bénéficiaire')
    check_in_out = fields.Selection([('entrer', 'Entrée'), ('sortie', 'Sortie')], 'Entrée/Sortie', default='sortie')
    somme = fields.Float(string='Somme')
    update = fields.Datetime(string='Mise à jour le')
    update_by = fields.Many2one('res.users', string='Mise à jour par')
    visibility = fields.Selection([('0', 'Oui'), ('1', 'Non')],
                                  "à ne pas déclarer ?", default='1')
    name = fields.Char(string="N° de bon")
    chantier_id = fields.Many2one('agentis.chantier', string="Chantier") #, 'agentis_office_id'
    etat = fields.Boolean(string='etat')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  default=lambda self: self.env.company.currency_id)
    solde = fields.Monetary(string='Somme', compute='get_solde', store=True, currency_field='currency_id')
    list_check_in_out = []

    def generate_update(self):
        locale_time = datetime.now()
        return locale_time


class CaissesConsolide(models.Model):
    _name = 'caisse.consolide'

    create_date = fields.Date(string='Date')
    libele = fields.Text(string='Libellé')
    num_facture = fields.Char(string="Numéro facture")
    nature_payment = fields.Selection([('espece', 'Espèce'), ('autre', 'Autre')], default='espece')
    payment_with = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('autre', 'Autre')],
        "Par l’intermédiaire de", default='employee')
    payment_with_employee = fields.Many2one('hr.employee', string='Employé')
    payment_with_fourn = fields.Many2one('res.partner', string='Fournisseur')
    payment_with_client = fields.Many2one('res.partner', string='Client')
    payment_with_other = fields.Many2one('res.partner', string='Autre')
    beneficiaire_is = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('autre', 'Autre')],
        "paiement de", default='employee')
    beneficiaire_employee = fields.Many2one('hr.employee', string='Employé Bénéficiaire')
    beneficiaire_is_client = fields.Many2one('res.partner', string='Client Bénéficiaire')
    beneficiaire_is_fournisseur = fields.Many2one('res.partner', string='Fournisseur Bénéficiaire')
    beneficiaire_is_other = fields.Many2one('res.partner', string='Autre Bénéficiaire')
    check_in_out = fields.Selection([('entrer', 'Entrée'), ('sortie', 'Sortie')], 'Entrée/Sortie', default='sortie')
    somme = fields.Float(string='Somme')
    update = fields.Datetime(string='Mise à jour le')
    update_by = fields.Many2one('res.users', string='Mise à jour par')
    visibility = fields.Selection([('0', 'Oui'), ('1', 'Non')],
                                  "à ne pas déclarer ?", default='1')
    name = fields.Char(string="N° de bon")
    chantier_id = fields.Many2one('agentis.chantier', string="Chantier")  # , 'agentis_office_id'
    etat = fields.Boolean(string='etat')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  default=lambda self: self.env.company.currency_id)
    solde = fields.Monetary(string='Somme', compute='get_solde', store=True, currency_field='currency_id')
    somme_in = fields.Float(string=' Somme', compute='get_somme_in')
    somme_out = fields.Float(string='Somme', compute='get_somme_out')
    is_create = fields.Boolean(string='est crée')
    insible_somme = fields.Boolean(string='somme visble ou non')

