# -*- coding: utf-8 -*-
from datetime import datetime

import pytz
from num2words import num2words

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


def return_abs_somme(somme):
    return abs(somme)


class OfficeManager(models.Model):
    _name = 'office.manager'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _order = 'name DESC, create_date DESC, update DESC'
    _description = 'caisse secondaire'

    @api.model
    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    def _default_account_journal_id(self):
        journal = self.env['account.journal'].search([('code', '=', 'CAIOM'), ('company_id', '=', self.env.company.id)])
        return journal.id

    create_date = fields.Date(string='Date de création:', default=_default_time_utc, readonly=True)
    date = fields.Date(string='Date ', default=_default_time_utc, track_visibility='always')
    libele = fields.Text(string='Libellé:', default='aucun', track_visibility='always')
    num_facture = fields.Char(string="Numéro facture:", track_visibility='always')
    nature_payment = fields.Selection([('espece', 'Espèce'), ('autre', 'Autre')], default='espece',
                                      track_visibility='always')
    payment_with = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('autre', 'Autre')],
        "Par l’intermédiaire de:", default='employee', track_visibility='always')
    payment_with_other = fields.Many2one('res.partner', string="Par l’intermédiaire de:", track_visibility='always')
    beneficiaire_is = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('dga', 'Caisse Principale'),
         ('autre', 'Autre')], "Partenaire:", default='employee', track_visibility='always')
    beneficiaire_employee = fields.Many2one('hr.employee', string='Employé Bénéficiaire:', track_visibility='always')
    beneficiaire_is_fournisseur = fields.Many2one('res.partner', string='Fournisseur Bénéficiaire:',
                                                  track_visibility='always')
    check_in_out = fields.Selection([('entrer', 'Entrée'), ('sortie', 'Sortie')], "type d'operation:", default='sortie',
                                    track_visibility='always')
    somme = fields.Float(string='Montant payé:', help="Montant de l'opération", track_visibility='onchange')
    update = fields.Datetime(string='Mise à jour le:', track_visibility='always')
    update_by = fields.Many2one('res.users', string='Mise à jour par:', track_visibility='always')
    prive = fields.Boolean(string="Privé")
    name = fields.Char(string="reference", track_visibility='always')
    num_bon = fields.Char(string='N° de bon: ')
    chantier_id = fields.Many2one('account.analytic.account', string="Projet:",
                                  track_visibility='always')  # , 'agentis_office_id'
    etat = fields.Boolean(string='etat')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  default=lambda self: self.env.company.currency_id)
    solde = fields.Monetary(string='Solde', compute='get_solde', store=True, currency_field='currency_id')
    somme_in = fields.Float(string=' Somme', compute='get_somme_in', store=True)
    somme_out = fields.Float(string='Somme', compute='get_somme_out', store=True)
    is_create = fields.Boolean(string='est crée')
    insible_somme = fields.Boolean(string='somme visble ou non')

    donne_a_client = fields.Many2one('res.partner', string='Donné à :', track_visibility='always')
    status = fields.Selection(
        [('brouillon', 'BROUILLONS'), ('attente', 'EN ATTENTE'), ('valide', 'VALIDE'), ('annule', 'ANNULE'),
         ('compta', 'COMPTABILISE')],
        default='brouillon', track_visibility='always')
    company_id = fields.Many2one('res.company', string='Société:', required=True, track_visibility='always')
    product_id = fields.Many2one(
        'product.product', 'Product', required=False, default=0)
    journal_id = fields.Many2one('account.journal', string='journal:', default=_default_account_journal_id)
    tax_id = fields.Many2one('account.tax', string='Taxe:')
    facture_id = fields.Integer(string='id facture')
    payment_id = fields.Integer(string='id payment')
    date_prevue = fields.Date(string='Date Effective:', default=_default_time_utc, track_visibility='always')
    type_caisse = fields.Selection([('dga', 'DGA'), ('manager', 'Office manager'), ('comptable', 'Comptable')],
                                   'Type de caisse', track_visibility='always')
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='agentis_manager_id',
        string='Charger vos fichiers:')
    total_somme = fields.Float(string='somme total', compute='get_total_somme')
    somme_lettre = fields.Char(string='Somme lettre')
    fideca = fields.Boolean(string='FIDECA', track_visibility='always')
    origin_fond = fields.Selection([('banque', 'Banque'), ('client', 'Client')], 'Orogine des fonds', default='client')
    total_facture_with_tax = fields.Float(string='Montant avec taxe', compute='get_total_with_tax')
    total_with_payment = fields.Float(string='Montant avec taxe', compute='get_total_payment_with')
    borderau = fields.Boolean(string='Borderau de livraison', track_visibility='always')
    num_borderau = fields.Char(string='N° Borderau', track_visibility='always')
    nature = fields.Char(string="Nature de l'operation", track_visibility='always')
    note = fields.Text(string='Note', track_visibility='always')
    somme_char = fields.Char(string='somme en caractere', compute='get_somme_char')
    facture = fields.Boolean(string='Crée une Facture ?')
    amount_facture = fields.Integer(string='somme facture', track_visibility='always')
    exist_facture_select = fields.Many2one('account.move', string='Selectionner la facture')
    exist_facture = fields.Boolean(string='Facture existante ?')
    hide_boolean = fields.Boolean(string='Cacher fact et pay', default=False)
    maroc = fields.Boolean(string='MAROC')
    company_create = fields.Many2one('res.company', string='Créer dans:', track_visibility='always',
                                     default=lambda self: self.env.company)
    caisse_id = fields.Char(string='Identifiant Caisse')
    no_see_dga = fields.Boolean(string='A caché', help='permert de cahé les ligne privé consolidé')

    def archive_project(self):
        data = [388, 1561, 1844, 1911, 1124, 390, 1587, 1700, 1735, 1559, 1925, 1916, 1896, 415, 428, 563, 1114, 1113,
                1924, 1934, 1943, 1935, 1929, 1774, 1948, 1096, 11, 1737, 1709, 1942, 357, 1061, 371, 1084, 544, 1066,
                1100, 1095, 1063, 1560, 1710, 408, 411, 352, 1117, 389, 1897, 1110, 384, 1707, 1563, 1708, 1078, 1755,
                1736]
        project = self.env['account.analytic.account'].search([])
        for line in project:
            if line.id in data:
                line.action_archive()

    def change_project_id(self):
        manager = self.env['office.manager'].search([])
        dga = self.env['agentis.dga'].search([])

        for line in manager:
            # ij
            if line.chantier_id.id in [388, 1844, 1911, 1124]:
                line.write({'chantier_id': 387})
            # entre
            elif line.chantier_id.id == 390:
                line.write({'chantier_id': 393})
            # a determiner
            elif line.chantier_id.id == 1587:
                line.write({'chantier_id': 351})
            # BA
            elif line.chantier_id.id in [1700, 1735, 1559, 1745]:
                line.write({'chantier_id': 382})
            # 5 service
            elif line.chantier_id.id == 1925:
                line.write({'chantier_id': 1940})
            # hg kong
            elif line.chantier_id.id in [1916, 1896]:
                line.write({'chantier_id': 1910})
            # hydrolique
            elif line.chantier_id.id == 415:
                line.write({'chantier_id': 386})
            # senegal
            elif line.chantier_id.id == 428:
                line.write({'chantier_id': 404})
            # vacin
            elif line.chantier_id.id == 563:
                line.write({'chantier_id': 436})
            # vacin 2
            elif line.chantier_id.id in [1114, 1113]:
                line.write({'chantier_id': 1899})
            # burkina
            elif line.chantier_id.id in [1924, 1934]:
                line.write({'chantier_id': 1930})
            # entrepot
            #
            elif line.chantier_id.id == 1943:
                line.write({'chantier_id': 1927})
            # entrepot
            elif line.chantier_id.id == 1935:
                line.write({'chantier_id': 1923})
            # hotel yakro
            elif line.chantier_id.id == 1929:
                line.write({'chantier_id': 1928})
            # hotel yakro
            elif line.chantier_id.id == 1774:
                line.write({'chantier_id': 1599})
            # dao
            elif line.chantier_id.id == 1948:
                line.write({'chantier_id': 1942})
            # voiture
            elif line.chantier_id.id in [1096, 11, 1737, 1709, 1942, 1561, 1707, 1563, 1708, 1078, 1755, 1736]:
                line.write({'chantier_id': 373})
            elif line.chantier_id.id in [357, 1061]:
                line.write({'chantier_id': 1072})
            elif line.chantier_id.id == 371:
                line.write({'chantier_id': 392})
            # adzope
            elif line.chantier_id.id in [1084, 544, 1066, 1100, 1064]:
                line.write({'chantier_id': 359})
            # aboisso
            elif line.chantier_id.id in [1095, 1063]:
                line.write({'chantier_id': 358})
            # kit scolaire
            elif line.chantier_id.id == 1560:
                line.write({'chantier_id': 1701})
            # onep
            elif line.chantier_id.id == 1710:
                line.write({'chantier_id': 370})
            # pdu universite
            elif line.chantier_id.id == 408:
                line.write({'chantier_id': 407})
            # beceao
            elif line.chantier_id.id == 411:
                line.write({'chantier_id': 405})
            # appart
            elif line.chantier_id.id == 352:
                line.write({'chantier_id': 1071})
            # ram 2
            elif line.chantier_id.id == 1117:
                line.write({'chantier_id': 1116})
            # terrain
            elif line.chantier_id.id == 389:
                line.write({'chantier_id': 385})
            # defense
            elif line.chantier_id.id == 1897:
                line.write({'chantier_id': 1119})
            # saifi
            elif line.chantier_id.id in [1110, 384]:
                line.write({'chantier_id': 397})

        for dg in dga:
            if dg.chantier_id.id in [388, 1844, 1911, 1124]:
                dg.write({'chantier_id': 387})
            elif dg.chantier_id.id == 390:
                dg.write({'chantier_id': 393})
            elif dg.chantier_id.id == 1587:
                dg.write({'chantier_id': 351})
            elif dg.chantier_id.id in [1700, 1735, 1559, 1745]:
                dg.write({'chantier_id': 382})
            elif dg.chantier_id.id == 1925:
                dg.write({'chantier_id': 1940})
            elif dg.chantier_id.id in [1916, 1896]:
                dg.write({'chantier_id': 1910})
            elif dg.chantier_id.id == 415:
                dg.write({'chantier_id': 386})
            elif dg.chantier_id.id == 428:
                dg.write({'chantier_id': 404})
            # vacin
            elif dg.chantier_id.id == 563:
                dg.write({'chantier_id': 436})
            # vacin
            elif dg.chantier_id.id in [1114, 1113]:
                dg.write({'chantier_id': 1899})
            elif dg.chantier_id.id in [1924, 1934]:
                dg.write({'chantier_id': 1930})
            elif dg.chantier_id.id == 1943:
                dg.write({'chantier_id': 1927})
            elif dg.chantier_id.id == 1935:
                dg.write({'chantier_id': 1923})
            elif dg.chantier_id.id == 1929:
                dg.write({'chantier_id': 1928})
            elif dg.chantier_id.id == 1774:
                dg.write({'chantier_id': 1599})
            elif dg.chantier_id.id == 1948:
                dg.write({'chantier_id': 1942})
            elif dg.chantier_id.id in [1096, 11, 1737, 1709, 1942]:
                dg.write({'chantier_id': 373})
            elif dg.chantier_id.id in [357, 1061]:
                dg.write({'chantier_id': 1072})
            elif dg.chantier_id.id == 371:
                dg.write({'chantier_id': 392})
            elif dg.chantier_id.id in [1084, 544, 1066, 1100, 1064]:
                dg.write({'chantier_id': 359})
            elif dg.chantier_id.id in [1095, 1063]:
                dg.write({'chantier_id': 358})
            # kit scolaire
            elif dg.chantier_id.id == 1560:
                dg.write({'chantier_id': 1701})
            # onep
            elif dg.chantier_id.id == 1710:
                dg.write({'chantier_id': 370})
            # pdu universite
            elif dg.chantier_id.id == 408:
                dg.write({'chantier_id': 407})
            # beceao
            elif dg.chantier_id.id == 411:
                dg.write({'chantier_id': 405})
            # appart
            elif dg.chantier_id.id == 352:
                dg.write({'chantier_id': 1071})
            # ram 2
            elif dg.chantier_id.id == 1117:
                dg.write({'chantier_id': 1116})
            # terrain
            elif dg.chantier_id.id == 389:
                dg.write({'chantier_id': 385})
            # defense
            elif dg.chantier_id.id == 1897:
                dg.write({'chantier_id': 1119})
            # saifi
            elif dg.chantier_id.id in [1110, 384]:
                dg.write({'chantier_id': 397})
            # france
            elif dg.chantier_id.id == 1921:
                dg.write({'chantier_id': 1920})

    @api.onchange('exist_facture_select')
    def onchange_exist_facture_select(self):
        self.num_facture = self.exist_facture_select.ref

    @api.onchange('somme')
    def onchange_dif_som_pay_inv(self):
        if self.facture:
            if self.somme > self.total_facture_with_tax:
                warning_mess = {
                    'title': _('Avertissement!'),
                    'message': _("le montant payé ne doit pas dépassr le montant de la facture !")
                }
                self.somme = 0
                return {'warning': warning_mess}

    @api.onchange('amount_facture')
    def onchange_amount_facture(self):
        if self.facture:
            if self.somme > self.total_facture_with_tax:
                warning_mess = {
                    'title': _('Avertissement!'),
                    'message': _("le montant payé ne doit pas dépassr le montant de la facture !")
                }
                self.somme = 0
                return {'warning': warning_mess}

    @api.onchange('beneficiaire_is')
    def onchange_beneficiaire_is(self):
        if self.beneficiaire_is == 'employee' or self.beneficiaire_is == 'autre':
            self.hide_boolean = True
        elif self.beneficiaire_is == 'dga' and self.check_in_out == 'sortie':
            warning_mess = {
                'title': _('Avertissement!'),
                'message': _("Pas de sortie vers la caisse principale")
            }
            self.beneficiaire_is = 'employee'
            return {'warning': warning_mess}

        elif self.beneficiaire_is == 'client' and self.check_in_out == 'entrer':
            self.hide_boolean = False
        elif self.beneficiaire_is == 'fournisseur' and self.check_in_out == 'sortie':
            self.hide_boolean = False
        else:
            self.hide_boolean = True

    @api.onchange('check_in_out')
    def onchange_check_in_out(self):
        if self.check_in_out == 'sortie' and self.beneficiaire_is == 'dga':
            warning_mess = {
                'title': _('Avertissement!'),
                'message': _("Pas de sortie vers la caisse principale")
            }
            self.beneficiaire_is = 'employee'
            return {'warning': warning_mess}
        elif self.beneficiaire_is == 'client' and self.check_in_out == 'entrer':
            self.hide_boolean = False
        elif self.beneficiaire_is == 'fournisseur' and self.check_in_out == 'sortie':
            self.hide_boolean = False
        else:
            self.hide_boolean = True

    @api.depends('amount_facture', 'tax_id')
    def get_total_with_tax(self):
        for val in self:
            amount_t = self.env['account.tax'].sudo().search([('id', '=', val.tax_id.ids)])
            amount_tax = 0
            if amount_t:
                amount_tax = amount_t.amount
            if val.facture:
                val.total_facture_with_tax = abs(val.amount_facture) + (amount_tax * abs(val.amount_facture)) / 100
            else:
                val.total_facture_with_tax

    @api.depends('somme')
    def get_total_payment_with(self):
        for val in self:
            val.total_with_payment = abs(val.somme)

    @api.depends('somme')
    def get_total_somme(self):
        for som in self:
            som.total_somme = abs(som.somme)
            som.somme_lettre = num2words((abs(som.somme)), lang='fr') + ' ' + ' FCFA'

    @api.depends('somme')
    def get_somme_char(self):
        for som in self:
            som.somme_char = '{:,}'.format(abs(som.somme)).replace(',', ' ')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if view_type == 'tree' and res_user.has_group('agentis.agentis_office_manager_prive'):
            self.get_somme_out()
            self.get_somme_in()
        return res

    @api.depends('somme')
    def get_somme_in(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        default_date = dt_utc.date()
        query = '''SELECT sum(somme) AS somme,office_manager.status,office_manager.prive FROM office_manager 
                WHERE office_manager.create_date = %(default_date)s AND office_manager.prive IS TRUE AND office_manager.somme 
                > 0  GROUP BY office_manager.status,office_manager.prive ORDER BY somme '''
        self._cr.execute(query, {'default_date': default_date})
        docs = self._cr.dictfetchall()
        if len(docs) != 0:
            office_manager_search = self.env['office.manager'].search(
                [('is_create', '=', True),
                 ('create_date', '=', default_date), ('somme', '>', 0)])

            if office_manager_search:
                for line in office_manager_search:
                    line.status = 'brouillon'
                    line.unlink()
            for val in docs:
                seq = self.env['ir.sequence'].next_by_code('office.sequence')
                val.update({
                    'somme_in': abs(val['somme']),
                    'check_in_out': 'entrer',
                    'is_create': True,
                    'prive': False,
                    'name': seq,
                    'create_date': default_date,
                    'etat': False,
                    'no_see_dga': True,
                    'company_id': self.env.company.id
                })
                self.env['office.manager'].create(val)

    def get_somme_out(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        default_date = dt_utc.date()
        query = '''SELECT sum(somme) AS somme,office_manager.status,office_manager.prive FROM office_manager 
        WHERE office_manager.create_date = %(default_date)s AND office_manager.prive IS TRUE AND office_manager.somme 
        < 0  GROUP BY office_manager.status,office_manager.prive ORDER BY somme '''
        self._cr.execute(query, {'default_date': default_date})
        docs = self._cr.dictfetchall()
        if len(docs) != 0:
            office_manager_search = self.env['office.manager'].search(
                [('is_create', '=', True), ('somme', '<', 0),
                 ('create_date', '=', default_date)])
            if office_manager_search:
                for line in office_manager_search:
                    line.status = 'brouillon'
                    line.unlink()
            for val in docs:
                seq = self.env['ir.sequence'].next_by_code('office.sequence')
                val.update({
                    'somme_out': abs(val['somme']),
                    'somme': abs(val['somme']),
                    'check_in_out': 'sortie',
                    'is_create': True,
                    'prive': False,
                    'name': seq,
                    'create_date': default_date,
                    'etat': False,
                    'no_see_dga': True,
                    'company_id': self.env.company.id
                })
                self.env['office.manager'].create(val)

    def generate_update(self):
        locale_time = datetime.now()
        return locale_time

    @api.model
    def create(self, vals):
        if 'chantier_id' in vals:
            if not vals.get('chantier_id'):
                print('ici 0808')
                raise ValidationError(_("veuillez choisir un projet svp !"))
        vals['name'] = self.env['ir.sequence'].next_by_code('office.sequence')
        vals['type_caisse'] = 'manager'
        in_out = vals['check_in_out']
        if in_out == 'sortie' and not vals['etat']:
            if vals['somme'] != 0:
                vals['somme'] = - vals['somme']
        vals['update_by'] = self.env.uid
        vals['update'] = self.generate_update()
        vals['etat'] = True
        vals.update({'journal_id': self._default_account_journal_id()})
        result = super(OfficeManager, self).create(vals)
        return result

    def write(self, vals):
        if 'chantier_id' in vals:
            if not vals.get('chantier_id'):
                print('ici 0909')
                raise ValidationError(_("veuillez choisir un projet svp !"))
        if self.check_in_out == 'sortie' and 'somme' in vals:
            if vals['somme'] > 0:
                vals['somme'] = - vals['somme']
        vals['update_by'] = self.env.uid
        vals['update'] = self.generate_update()
        vals.update({'journal_id': self._default_account_journal_id()})
        result = super(OfficeManager, self).write(vals)
        return result

    def unlink(self):
        for val in self:
            if val.status == 'valide' or (val.status == 'attente' or val.status == 'compta'):
                raise ValidationError(
                    _("Vous ne pouvez pas supprimer une opération validée ou en attente, veuillez mettre en brouillon "
                      "d'abord !"))
            else:
                history = {
                    'amount': val.somme,
                    'num_caisse': val.name,
                    'type_caisse': 'manager',
                    'chantier_id': val.chantier_id.id,
                    'company_id': val.company_id.id,
                    'libele': val.libele,
                    'check_in_out': val.check_in_out,
                    'date_mvt': val.create_date
                }
                self.env['history.delete'].create(history)
        return super(OfficeManager, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        print('duplication self', self)
        if 'name' not in default:
            default['name'] = _("%s (Copy)") % self.name
        if 'status' not in default:
            default['status'] = 'brouillon'
        return super(OfficeManager, self).copy(default=default)

    @api.depends('somme')
    def get_solde(self):
        amount = 0
        for agentis_dga in self:
            amount = amount + agentis_dga.somme
            agentis_dga.solde = amount

    def make_payment(self):

        action = {'type': 'ir.actions.act_window', 'name': 'Caisse DGA', 'view_mode': 'form', 'target': 'new',
                  'res_model': 'account.payment', 'view_id': self.env.ref('account.view_account_payment_form').id}

        context = {
            'default_partner_type': 'supplier',
            'default_move_journal_types': ('bank', 'cash'),
            'default_payment_type': 'inbound'
        }
        action['context'] = context
        return action

    def put_suspense(self):
        self.status = 'attente'
        return True

    def get_employee_in_partner(self, employee):
        if employee:
            partner = self.env['res.partner'].sudo().search([('user_associe_id', '=', employee.id)])
            if not partner:
                partner = self.env['res.partner'].sudo().search([('id', '=', employee.id)])
            return partner.id

    def validate_mvt(self):
        for manager in self:
            if manager.status != 'valide':
                manager.status = 'valide'

        return True

    def validate_operation(self):

        num_fact = ''
        for manager in self:
            actual_company = self.env.company
            operation_company = manager.company_id
            if actual_company != operation_company:
                message = f"Impossible de comptabiliser dans cette société, veuillez selectionner" \
                          f" {operation_company.name} pour comptabiliser !"
                raise ValidationError(
                    _(message))
        if manager.status != 'compta':
            manager.status = 'compta'
            invoice_vals = {
                'type_caisse': 'manager',
                'caisse_id': 'CAI' + str(manager.id),
                'manager_id': manager.id,
                'borderau': manager.borderau,
                'num_borderau': manager.num_borderau,
                'ref': num_fact,
                'comp_id': manager.company_id.id,
                'move_type': 'out_invoice',
                'invoice_origin': manager.name,
                'narration': '',
                'partner_id': manager.beneficiaire_is_fournisseur.id,
                'commercial_partner_id': manager.beneficiaire_is_fournisseur.id,
                'currency_id': manager.currency_id.id,
                'state': 'draft',
                'invoice_date': manager.date_prevue,
                'invoice_partner_display_name': manager.beneficiaire_is_fournisseur.name,
                'invoice_line_ids': [(0, 0, {
                    'name': manager.libele,
                    'price_unit': abs(manager.amount_facture),
                    'quantity': 1.0,
                    'product_id': 1,
                    'product_uom_id': manager.product_id.uom_id.id,
                    'analytic_account_id': manager.chantier_id.id or False,
                    'tax_ids': [(6, 0, manager.tax_id.ids)]
                })],
            }

            if manager.facture:
                amount_t = self.env['account.tax'].sudo().search([('id', '=', manager.tax_id.ids)])
                amount_tax = amount_t.amount
                coeff = amount_t.exclude_amount
                if manager.num_facture:
                    invoice_vals.update({'name': manager.num_facture})
                if manager.tax_id.exclude_tax:
                    invoice_vals.update(
                        {'tax_exclude': (coeff * abs(manager.amount_facture)) / 100, 'tax_exclude_visible': True,
                         'somme_lettre': num2words((abs(manager.amount_facture)), lang='fr') + ' ' + ' FCFA'})
                else:
                    invoice_vals.update(
                        {'somme_lettre': num2words(
                            (abs(manager.amount_facture) + (amount_tax * abs(manager.amount_facture)) / 100),
                            lang='fr') + ' ' + ' FCFA'})
                if manager.beneficiaire_is == 'client' and manager.check_in_out == 'entrer':
                    invoice_vals.update({'move_type': 'out_invoice'})
                    resut = self.env['account.move'].sudo().create(invoice_vals)
                    manager.facture_id = resut.id
                    resut.action_post()
                    # resut.invoice_outstanding_credits_debits_widget

                elif manager.beneficiaire_is == 'fournisseur' and manager.check_in_out == 'sortie':
                    invoice_vals.update({'move_type': 'in_invoice'})
                    resut = self.env['account.move'].sudo().create(invoice_vals)
                    manager.facture_id = resut.id
                    resut.action_post()
                    # num_fact = resut.name

                for payment in manager:
                    paired_payment = {
                        'type_caisse': 'manager',
                        'caisse_id': 'CAI' + str(payment.id),
                        'manager_id': payment.id,
                        'journal_id': payment.journal_id.id,
                        'nature': payment.nature,
                        'destination_journal_id': payment.journal_id.id,
                        'move_id': None,
                        'partner_id': payment.beneficiaire_is_fournisseur.id,
                        'amount': abs(payment.somme),
                        'ref': payment.num_facture,
                        'date': payment.date_prevue,
                        'num_transaction': payment.name,
                        'type_operation': 'local',
                        'methode_payment': 'espece',
                        'libele': payment.libele,
                        'chantier_id': payment.chantier_id.id,
                        'select_operation': 'espece',
                    }

                    if payment.beneficiaire_is == 'client' and payment.check_in_out == 'entrer':
                        paired_payment.update({'payment_type': 'inbound'})
                        paired_payment.update({'partner_type': 'customer'})
                        resul = self.env['account.payment'].sudo().create(paired_payment)
                        payment.payment_id = resul.id
                        resul.action_post()
                        # num_fact = resul.ref or manager.num_facture

                    elif payment.beneficiaire_is == 'fournisseur' and payment.check_in_out == 'sortie':
                        paired_payment.update({'payment_type': 'outbound'})
                        paired_payment.update({'partner_type': 'supplier'})
                        resul = self.env['account.payment'].sudo().create(paired_payment)
                        payment.payment_id = resul.id
                        resul.action_post()
                        # num_fact = resut.ref or manager.num_facture

            elif manager.exist_facture:
                for payment in manager:
                    paired_payment = {
                        'type_caisse': 'manager',
                        'caisse_id': 'CAI' + str(payment.id),
                        'manager_id': manager.id,
                        'journal_id': payment.journal_id.id,
                        'nature': payment.nature,
                        'destination_journal_id': payment.journal_id.id,
                        'move_id': None,
                        'partner_id': payment.beneficiaire_is_fournisseur.id,
                        'amount': abs(payment.somme),
                        'ref': payment.num_facture,
                        'date': payment.date_prevue,
                        'num_transaction': payment.name,
                        'type_operation': 'local',
                        'methode_payment': 'espece',
                        'libele': payment.libele,
                        'chantier_id': payment.chantier_id.id,
                        'select_operation': 'espece',
                    }

                    if manager.beneficiaire_is == 'client' and manager.check_in_out == 'entrer':
                        paired_payment.update({'payment_type': 'inbound'})
                        paired_payment.update({'partner_type': 'customer'})
                        resul = self.env['account.payment'].sudo().create(paired_payment)
                        manager.payment_id = resul.id
                        resul.action_post()
                        # num_fact = resul.ref or manager.num_facture

                    elif manager.beneficiaire_is == 'fournisseur' and manager.check_in_out == 'sortie':
                        paired_payment.update({'payment_type': 'outbound'})
                        paired_payment.update({'partner_type': 'supplier'})
                        resul = self.env['account.payment'].sudo().create(paired_payment)
                        manager.payment_id = resul.id
                        resul.action_post()
            else:
                # employee ou autre ecrit dans le releve
                if manager.beneficiaire_is == 'employee' or manager.beneficiaire_is == 'autre':
                    move_line = self.env['account.bank.statement.line'].search(
                        [('caisse_id', '=', 'MAN' + str(manager.id))])

                    if move_line:

                        line = {
                            'date': manager.date,
                            'caisse_id': 'MAN' + str(manager.id),
                            'payment_ref': manager.libele,
                            'nature': manager.nature,
                            'num_transaction': manager.name,
                            'partner_id': manager.get_employee_in_partner(manager.beneficiaire_is_fournisseur),
                            'chantier_id': manager.chantier_id.id,
                            'ref': manager.name,

                        }
                        if manager.check_in_out == 'sortie':
                            line.update({'amount': - abs(manager.somme)})
                        move_line.write(line)
                    else:
                        all_val = {
                            'name': 'Caisse Secondaire du ' + (str(manager.create_date)),
                            'journal_id': manager.journal_id.id,
                            'date': manager.create_date,
                            'date_prevue': datetime.now(),
                            'line_ids': [(0, 0, {
                                'date': manager.date_prevue,
                                'payment_ref': (manager.libele or ' '),
                                'partner_id': manager.get_employee_in_partner(manager.beneficiaire_is_fournisseur),
                                'amount': manager.somme,
                                'caisse_id': 'MAN' + str(manager.id),
                                'num_transaction': manager.name,
                                'chantier_id': manager.chantier_id.id,
                                'nature': manager.nature,

                            })]
                        }
                        date_day = manager._default_time_utc()
                        caisse_dga = self.env['account.bank.statement'].sudo().search(
                            [('date', '=', manager.create_date), ('journal_id', '=', manager.journal_id.id)])
                        if caisse_dga:
                            if date_day.strftime('%Y-%m-%d') == str(manager.create_date):
                                line = {
                                    'date': manager.create_date,
                                    'line_ids': [(0, 0, {
                                        'date': manager.date_prevue,
                                        'payment_ref': (manager.libele or 'aucun'),
                                        'partner_id': manager.get_employee_in_partner(
                                            manager.beneficiaire_is_fournisseur),
                                        'amount': manager.somme,
                                        'caisse_id': 'MAN' + str(manager.id),
                                        'chantier_id': manager.chantier_id.id,
                                        'nature': manager.nature,

                                    })]
                                }
                                caisse_dga.write(line)
                            else:
                                self.env['account.bank.statement'].sudo().create(all_val)
                        else:
                            self.env['account.bank.statement'].sudo().create(all_val)
                elif manager.beneficiaire_is == 'client' or manager.beneficiaire_is == 'fournisseur':
                    for payment in manager:
                        paired_payment = {
                            'type_caisse': 'manager',
                            'caisse_id': 'CAI' + str(payment.id),
                            'manager_id': payment.id,
                            'journal_id': payment.journal_id.id,
                            'nature': payment.nature,
                            'destination_journal_id': payment.journal_id.id,
                            'move_id': None,
                            'partner_id': payment.beneficiaire_is_fournisseur.id,
                            'amount': abs(payment.somme),
                            'ref': payment.num_facture,
                            'date': payment.date_prevue,
                            'num_transaction': payment.name,
                            'type_operation': 'local',
                            'methode_payment': 'espece',
                            'libele': payment.libele,
                            'chantier_id': payment.chantier_id.id,
                            'select_operation': 'espece',
                        }

                        if manager.beneficiaire_is == 'client' and manager.check_in_out == 'entrer':
                            paired_payment.update({'payment_type': 'inbound'})
                            paired_payment.update({'partner_type': 'customer'})
                            resul = self.env['account.payment'].sudo().create(paired_payment)
                            manager.payment_id = resul.id
                            resul.action_post()
                            # num_fact = resul.ref or manager.num_facture

                        elif manager.beneficiaire_is == 'fournisseur' and manager.check_in_out == 'sortie':
                            paired_payment.update({'payment_type': 'outbound'})
                            paired_payment.update({'partner_type': 'supplier'})
                            resul = self.env['account.payment'].sudo().create(paired_payment)
                            manager.payment_id = resul.id
                            resul.action_post()
        return True

    def put_draft(self):
        for manager in self:
            manager.status = 'brouillon'
            facture = self.env['account.move'].sudo().search([('id', '=', manager.facture_id)])
            payment = self.env['account.payment'].sudo().search([('id', '=', manager.payment_id)])
            # if facture.state == 'posted':
            #     raise ValidationError(_('Vous ne pouvez pas remettre en brouillon une opération déjà comptabilisée'))
            # else:
            #     facture.unlink()
            #     payment.unlink()
            # caisse_line = self.env['account.bank.statement.line'].sudo().search(
            #     [('caisse_id', '=', 'MAN' + str(manager.id))])
            # if caisse_line:
            #     caisse_line.sudo().unlink()
            # facture.button_draft()
            # payment.action_draft()
        return True

    def export_operation(self):

        action = {'type': 'ir.actions.act_window', 'name': 'Export', 'view_mode': 'form', 'target': 'new',
                  'res_model': 'dga.report', 'view_id': self.env.ref('agentis.view_agentis_dga_export').id}
        return action

    @api.model
    def retrieve_dashboard(self):
        """ This function returns the values to populate the custom dashboard in
            the office manager views.
        """
        self.check_access_rights('read')

        result = {
            'all_total_validate': 0,
            'all_total_draft': 0,
            'all_total_suspense': 0,
            'company_currency_symbol': self.env.company.currency_id.symbol
        }
        all_total_validate, all_total_draft, all_total_suspense = 0, 0, 0
        office_manager = self.env['office.manager'].search([])
        for office in office_manager:
            if not office.no_see_dga:
                if office.status == 'brouillon':
                    all_total_draft = all_total_draft + office.somme
                elif office.status == 'attente':
                    all_total_suspense = all_total_suspense + office.somme
                elif office.status == 'valide' or office.status == 'compta':
                    all_total_validate = all_total_validate + office.somme

        result['all_total_validate'] = '{:,}'.format(all_total_validate)
        result['all_total_suspense'] = '{:,}'.format(all_total_suspense)
        result['all_total_draft'] = '{:,}'.format(all_total_draft + all_total_suspense)
        return result

    def open_facture(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Factures', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.move', 'view_id': False}
        if self.beneficiaire_is == 'fournisseur':
            domain = ([('caisse_id', '=', 'CAI' + str(self.id)), ('move_type', '=', 'in_invoice')])
            action['domain'] = domain
        elif self.beneficiaire_is == 'client':
            domain = ([('caisse_id', '=', 'CAI' + str(self.id)), ('move_type', '=', 'out_invoice')])
            action['domain'] = domain
        return action

    def open_payment(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Paiements', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.payment', 'view_id': False}

        domain = ([('caisse_id', '=', 'CAI' + str(self.id))])
        action['domain'] = domain
        return action
