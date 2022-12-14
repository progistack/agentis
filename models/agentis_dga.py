# -*- coding: utf-8 -*-

from datetime import datetime
import pytz
from num2words import num2words

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AgentisDGA(models.Model):
    _name = 'agentis.dga'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _order = 'num_caisse DESC, create_date DESC, update DESC'
    _description = 'caisse principale'
    _rec_name = 'num_caisse'

    @api.model
    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    """def _default_account_journal_id(self):
        journal = self.env['account.journal'].search([('code', '=', 'CSH1'), ('company_id', '=', self.env.company.id)])
        return journal.id
    """
    create_date = fields.Date(string='Date de création:', default=_default_time_utc, readonly=True)
    date = fields.Date(string='Date Effective:', default=_default_time_utc, track_visibility='onchange')
    libele = fields.Text(string='Libellé:', default='aucun', track_visibility='onchange')
    name = fields.Char(string="Numéro facture:", track_visibility='onchange')
    nature_payment = fields.Selection([('espece', 'Espèce'), ('autre', 'Autre')], default='espece',
                                      track_visibility='onchange')
    payment_with = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('autre', 'Autre')],
        "Par l’intermédiaire de:", default='employee', track_visibility='onchange')
    payment_with_other = fields.Many2one('res.partner', string='Nom partenaire:', track_visibility='onchange')
    beneficiaire_is = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('autre', 'Autre'),
         ('dga', 'Office manager')], "Partenaire:", default='fournisseur', track_visibility='onchange')
    beneficiaire_employee = fields.Many2one('hr.employee', string='Employé beneficiaire:', track_visibility='onchange')
    beneficiaire_is_fournisseur = fields.Many2one('res.partner', string='Beneficiaire final:',
                                                  track_visibility='onchange')
    check_in_out = fields.Selection([('entrer', 'Entrée'), ('sortie', 'Sortie'), ('transfert', 'Transfert de fond')],
                                    "type d'operation:", default='sortie', track_visibility='onchange',
                                    require=True)
    somme = fields.Float(string='Montant:', track_visibility='onchange')
    update = fields.Datetime(string='Mise à jour le:', track_visibility='onchange')
    update_by = fields.Many2one('res.users', string='Mise à jour par:', track_visibility='onchange')
    chantier_id = fields.Many2one('account.analytic.account', string="Projet:",
                                  track_visibility='onchange')  # 'agentis_pga_id'
    etat = fields.Boolean(string='etat')
    currency_id = fields.Many2one('res.currency', string='Devise:', required=True, readonly=False, store=True,
                                  default=lambda self: self.env.company.currency_id)
    solde = fields.Monetary(string='Solde', compute='get_solde', store=True, currency_field='currency_id')
    donne_a_client = fields.Many2one('res.partner', string='Donné à :', track_visibility='onchange')
    status = fields.Selection([('brouillon', 'BROUILLONS'), ('attente', 'EN ATTENTE'), ('valide', 'VALIDE')],
                              default='brouillon', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Société:', track_visibility='onchange', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal comptable:', check_company=True)
    tax_id = fields.Many2one('account.tax', string='Taxe:')
    facture_id = fields.Integer(string='id facture:')
    payment_id = fields.Integer(string='id payment:')
    type_caisse = fields.Selection(
        [('dga', 'Caisse Principale'), ('manager', 'Caisse secondaire'), ('comptable', 'Mouvement bancaire')],
        'Type de caisse:', track_visibility='onchange')
    total_somme = fields.Float(string='somme total', compute='get_total_somme')
    somme_lettre = fields.Char(string='Somme lettre', compute='get_somme_lettre', store=True)
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='agentis_dga_id',
        string='Charger vos fichiers:')
    list_check_in_out = []
    origin_fond = fields.Selection([('banque', 'Banque'), ('espece', 'Espece')], 'Origine des fonds', default='banque')
    num_caisse = fields.Char(string='numero Caisse:', track_visibility='onchange')
    prive = fields.Boolean(string='Privé:')
    fideca = fields.Boolean(string='FIDECA:')
    user = fields.Boolean(string='user', compute='get_user')
    partner_om = fields.Selection([('dga', 'Caisse secondaire')], 'caisse secondaire', default='dga')
    somme_char = fields.Char(string='somme en caractere', compute='get_somme_char')
    bank_id = fields.Many2one('agentis.bank', string='Méthode de paiément:', track_visibility='onchange')
    nature_operation = fields.Char(string='Nature opération:', track_visibility='onchange')
    caisse_id = fields.Char(string='Identifiant Caisse')
    somme_in = fields.Float(string=' Somme', compute='get_somme_in', store=True)
    somme_out = fields.Float(string='Somme', compute='get_somme_out', store=True)
    is_create = fields.Boolean(string='est crée')
    no_see_dga = fields.Boolean(string='A caché', help='permert de cahé les ligne privé consolidé')
    nature_operation_id = fields.Many2one('nature.operation', string='Nature Operation:', track_visibility='onchange')
    note = fields.Text(string='Note:', compute='_compute_note', default=' aucune', store=True)
    analytic_user_id = fields.Many2one('account.analytic.account', string="Restriction Projet")
    user_instance = fields.Boolean()
    private_beneficial = fields.Many2one('res.partner', string='Beneficiaire final:')
    private_beneficial_employee = fields.Many2one('hr.employee', string='Beneficiaire employé:')

    @api.depends('activity_user_id', 'somme')
    def _compute_note(self):
        """
        recupere les notes sur les activite planifier
        """
        for line in self:
            for ln in line.activity_ids:
                line.note = ' aucune'
                if ln.note.striptags():
                    line.note = ln.note.striptags()

    @api.depends('prive')
    def get_user(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('agentis.agentis_dga_users') and not res_user.has_group('agentis.agentis_dga'):
            self.user = True
        else:
            self.user = False

    @api.depends('somme')
    def get_total_somme(self):
        for som in self:
            som.total_somme = abs(som.somme)

    @api.depends('somme')
    def get_somme_lettre(self):
        for som in self:
            som.somme_lettre = num2words((abs(som.somme)), lang='fr') + ' ' + ' FCFA'

    @api.depends('somme')
    def get_somme_char(self):
        for som in self:
            som.somme_char = '{:,}'.format(abs(som.somme)).replace(',', ' ')

    @api.depends('somme')
    def get_solde(self):
        amount = 0
        for agentis_dga in self:
            amount = amount + agentis_dga.somme
            agentis_dga.solde = amount

    @api.depends('somme')
    def get_somme_in(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        default_date = dt_utc.date()
        query = '''SELECT sum(somme) AS somme,agentis_dga.status,agentis_dga.prive FROM agentis_dga 
                    WHERE agentis_dga.create_date = %(default_date)s AND agentis_dga.prive IS TRUE AND agentis_dga.somme 
                    > 0  GROUP BY agentis_dga.status,agentis_dga.prive ORDER BY somme '''
        self._cr.execute(query, {'default_date': default_date})
        docs = self._cr.dictfetchall()
        if len(docs) != 0:
            office_manager_search = self.env['agentis.dga'].search(
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
                    'libele': 'Aucun',
                    'company_id': self.env.company.id,
                    'company_create': self.env.company.id,

                })
                self.env['agentis.dga'].create(val)

    @api.depends('somme_out')
    def get_somme_out(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        default_date = dt_utc.date()
        query = '''SELECT sum(somme) AS somme,agentis_dga.status,agentis_dga.prive FROM agentis_dga 
            WHERE agentis_dga.create_date = %(default_date)s AND agentis_dga.prive IS TRUE AND agentis_dga.somme 
            < 0  GROUP BY agentis_dga.status,agentis_dga.prive ORDER BY somme '''
        self._cr.execute(query, {'default_date': default_date})
        docs = self._cr.dictfetchall()
        if len(docs) != 0:
            office_manager_search = self.env['agentis.dga'].search(
                [('is_create', '=', True),
                 ('create_date', '=', default_date), ('somme', '<', 0)])
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
                    'libele': 'Aucun',
                    'no_see_dga': True,
                    'company_id': self.env.company.id,
                    'company_create': self.env.company.id,
                })
                self.env['agentis.dga'].create(val)

    @api.onchange('user_instance')
    def onchange_user_instance(self):
        connect_user = self.env['res.users'].search([('id', '=', self._uid)])
        create_user = self.env['res.users'].search([('id', '=', self.create_uid.id)])
        if self.prive:
            if connect_user.has_group('agentis.agentis_dga_users') and create_user.has_group('agentis.agentis_dga'):
                warning_mess = {
                    'title': _('Avertissement !'),
                    'message': _("Vous ne pouvez pas modifier l'état de cette opération")
                }
                self.user_instance = False
                return {'warning': warning_mess}
            else:
                self.prive = self.user_instance

    @api.onchange('prive')
    def onchange_prive(self):
        for val in self:
            if not val.prive:
                val.user_instance = val.prive
            elif val.prive:
                val.beneficiaire_is_fournisseur = False
                val.payment_with_other = False
                val.beneficiaire_employee = False

    @api.onchange('beneficiaire_is_fournisseur', 'beneficiaire_employee')
    def onchange_beneficaire_for_user(self):
        for val in self:
            if not val.prive:
                if val.beneficiaire_is_fournisseur:
                    val.private_beneficial = val.beneficiaire_is_fournisseur or val.payment_with_other

                elif val.beneficiaire_employee:
                    val.private_beneficial_employee = val.beneficiaire_employee

    '''
    modification des donnees prives lorsqu'on se connecte en tant qu'un utilisateur dga prive
    '''

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if view_type == 'tree' and res_user.has_group('agentis.agentis_dga_prive'):
            self.get_somme_out()
            self.get_somme_in()
        return res

    '''
    retire des chapms dans la vue search
    '''

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(AgentisDGA, self).fields_get(allfields, attributes=attributes)
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('agentis.agentis_dga_users') and not res_user.has_group('agentis.agentis_dga'):
            hide_fields = ['no_see_dga', 'etat', 'update', 'private_beneficial', 'private_beneficial_employee',
                           'update_by', 'analytic_user_id']
            for fld in hide_fields:
                if fld in res:
                    res[fld]['selectable'] = False
                    res[fld]['sortable'] = False
                    res[fld]['searchable'] = False
                    res[fld]['exportable'] = False
        elif res_user.has_group('agentis.agentis_dga'):
            hide_fields = ['no_see_dga', 'etat', 'nature_operation_id', 'update', 'update_by',
                           'beneficiaire_is_fournisseur', 'beneficiaire_employee', 'libele', 'analytic_user_id']
            for fld in hide_fields:
                if fld in res:
                    res[fld]['selectable'] = False
                    res[fld]['sortable'] = False
                    res[fld]['searchable'] = False
                    res[fld]['exportable'] = False
        return res

    @api.model
    def create(self, vals):
        vals['num_caisse'] = self.env['ir.sequence'].next_by_code('DGA.sequence')
        vals['type_caisse'] = 'dga'
        in_out = vals['check_in_out']
        if (in_out == 'sortie' or in_out == 'transfert') and not vals['etat']:
            if vals['somme'] != 0:
                vals['somme'] = - vals['somme']
        chantier = vals.get('chantier_id')
        if chantier:
            pass
        else:
            vals.update({'chantier_id': vals.get('analytic_user_id')})

        chantier_user = vals.get('analytic_user_id')
        if chantier_user:
            pass
        else:
            vals.update({'analytic_user_id': vals.get('chantier_id')})
        if vals.get('user_instance'):
            vals.update({'prive': True,
                         'beneficiaire_is_fournisseur': False,
                         'payment_with_other': False,
                         'beneficiaire_employee': False
                         })
        vals['update_by'] = self.env.uid
        vals['update'] = self.generate_update()
        vals['etat'] = True
        result = super(AgentisDGA, self).create(vals)
        return result

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (Copy)") % self.name
        if 'status' not in default:
            default['status'] = 'brouillon'
        return super(AgentisDGA, self).copy(default=default)

    def write(self, vals):

        if self.check_in_out == 'sortie' or self.check_in_out == 'transfert':
            if 'somme' in vals and vals['somme'] > 0:
                vals['somme'] = - vals['somme']
            elif self.somme > 0:
                vals.update({'somme': - self.somme})
        elif self.somme < 0:
            vals.update({'somme': - self.somme})
        elif 'check_in_out' in vals:
            if vals['check_in_out'] == 'sortie' or vals['check_in_out'] == 'transfert':
                if self.somme > 0:
                    vals.update({'somme': - self.somme})
            else:
                if self.somme < 0:
                    vals.update({'somme': - self.somme})
        chantier = vals.get('chantier_id')
        if chantier:
            vals.update({'analytic_user_id': vals.get('chantier_id')})
        chantier_user = vals.get('analytic_user_id')
        if chantier_user:
            vals.update({'chantier_id': vals.get('analytic_user_id')})
        if vals.get('user_instance'):
            vals.update({'prive': True,
                         'beneficiaire_is_fournisseur': False,
                         'payment_with_other': False,
                         'beneficiaire_employee': False
                         })
        vals['update_by'] = self.env.uid
        vals['update'] = self.generate_update()
        result = super(AgentisDGA, self).write(vals)
        return result

    def unlink(self):
        for val in self:
            if val.status == 'valide' or val.status == 'attente':
                raise ValidationError(
                    _("Vous ne pouvez pas supprimer une opération validée ou en attente, veuillez mettre en brouillon "
                      "d'abord !"))
            else:
                history = {
                    'amount': val.somme,
                    'num_caisse': val.num_caisse,
                    'type_caisse': 'dga',
                    'chantier_id': val.chantier_id.id,
                    'company_id': val.company_id.id,
                    'libele': val.libele,
                    'check_in_out': val.check_in_out,
                    'date_mvt': self.create_date
                }
                self.env['history.delete'].create(history)

        return super(AgentisDGA, self).unlink()

    def generate_update(self):
        locale_time = datetime.now()
        return locale_time

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

    def export_data_pdf(self):
        data = {'ids': self.ids}
        return self.env.ref('agentis.agentis_dga_principale_pdf').report_action([], data=data)

    def put_suspense(self):
        self.status = 'attente'
        if self.check_in_out == 'transfert':
            manager = self.env['office.manager'].sudo().search([('caisse_id', '=', 'TRANS' + str(self.id))])
            if manager:
                for man in manager:
                    man.write({'status': 'annule'})
        return True

    def get_employee_in_partner(self, employee):
        if employee:
            partner = self.env['res.partner'].sudo().search([('user_associe_id', '=', employee.id)])
            return partner.id

    def update_private_beneficial(self):
        all_data = self.env['agentis.dga'].search([])
        for val in all_data:
            if val.beneficiaire_is == 'employee':
                if val.prive:
                    val.beneficiaire_is_fournisseur = False
            # if val.beneficiaire_is == 'employee':
            #     print('00000000000000000000', val.beneficiaire_employee)
            #     val.write({'private_beneficial_employee': val.beneficiaire_employee.id})
            #     if val.prive:
            #         val.beneficiaire_employee = False
            # else:
            #
            #     if val.beneficiaire_is_fournisseur:
            #         val.write({'private_beneficial': val.beneficiaire_is_fournisseur.id
            #                    })
            #         print('test .................beneficiaire_is_fournisseur', val.beneficiaire_is_fournisseur)
            #     elif val.payment_with_other:
            #         val.write({'private_beneficial': val.payment_with_other.id
            #                    })
            #         print('test .................payment_with_other', val.payment_with_other)
            #
            #     if val.prive:
            #         val.beneficiaire_is_fournisseur = False
            #         val.payment_with_other = False

    def validate_operation(self):
        for dga in self:
            if dga.status != 'valide':
                dga.status = 'valide'
                if dga.check_in_out == 'transfert':
                    vals = dga.copy_data()
                    manager = self.env['office.manager'].sudo().search([('caisse_id', '=', 'TRANS' + str(self.id))])
                    if manager:
                        for man in manager:
                            for val in vals:
                                val.pop('num_caisse')
                                val.pop('prive')
                                val.pop('partner_om')
                                val.pop('bank_id')
                                val.pop('nature_operation_id')
                                val.pop('nature_operation')
                                val.pop('analytic_user_id')
                                val.pop('user_instance')
                                val['beneficiaire_is'] = 'dga'
                                val['check_in_out'] = 'entrer'
                                val['status'] = 'valide'
                                val['somme'] = abs(val['somme'])
                                val.update(
                                    {'num_facture': val['name'], 'nature': dga.nature_operation_id.nature_operation,
                                     'caisse_id': 'TRANS' + str(dga.id)})
                            man.write(val)
                    else:
                        for val in vals:
                            val.pop('num_caisse')
                            val.pop('prive')
                            val.pop('partner_om')
                            val.pop('bank_id')
                            val.pop('nature_operation_id')
                            val.pop('nature_operation')
                            val.pop('analytic_user_id')
                            val.pop('user_instance')
                            val['beneficiaire_is'] = 'dga'
                            val['check_in_out'] = 'entrer'
                            val['status'] = 'valide'
                            val['somme'] = abs(val['somme'])
                            val.update({'num_facture': val['name'], 'nature': dga.nature_operation_id.nature_operation,
                                        'caisse_id': 'TRANS' + str(dga.id)})
                        dga.env['office.manager'].sudo().create(val)

                """elif dga.check_in_out == 'entrer':
                    caisse_dga = dga.env['account.bank.statement'].sudo().search(
                        [('date', '=', dga.create_date), ('journal_id', '=', dga._default_account_journal_id())])
                    all_val = {
                        'name': 'Caisse Principale du ' + (str(dga.create_date)),
                        'journal_id': dga._default_account_journal_id(),
                        'date': dga.create_date,
                        'company_id': dga.company_id.id,
                        'line_ids': [(0, 0, {
                            'date': dga.create_date,
                            'payment_ref': dga.libele,
                            'partner_id': dga.get_employee_in_partner(
                                dga.beneficiaire_is_fournisseur or dga.beneficiaire_employee or dga.beneficiaire_is_client or dga.beneficiaire_is_other),
                            'amount': dga.somme,
                            'caisse_id': dga.id
                        })]
                    }
                    date_day = dga._default_time_utc()
                    if caisse_dga:
                        if date_day.strftime('%Y-%m-%d') == str(dga.create_date):
                            line = {
                                'date': dga.create_date,
                                'line_ids': [(0, 0, {
                                    'date': dga.create_date,
                                    'payment_ref': dga.libele or '',
                                    'partner_id': dga.get_employee_in_partner(
                                        dga.beneficiaire_is_fournisseur or dga.beneficiaire_employee or dga.beneficiaire_is_client),
                                    'amount': dga.somme,
                                    'caisse_id': dga.id
                                })]
                            }
                            caisse_dga = dga.env['account.bank.statement'].sudo().search([('date', '=', dga.create_date)])
                            caisse_dga.write(line)
                        else:
                            dga.env['account.bank.statement'].sudo().create(all_val)
                    else:
                        dga.env['account.bank.statement'].sudo().create(all_val)
"""

        return True

    def create_enter(self):
        enter_out = self.check_in_out
        if enter_out == 'entrer':
            """
            vals = {
                'create_date': self.create_date,
                'libele': self.libele,
                'name': self.name,
                'nature_payment': self.nature_payment,
                'payment_with': self.payment_with,
                'payment_with_employee': self.payment_with_employee.id,
                'payment_with_other': self.payment_with_other.id,
                'beneficiaire': self.beneficiaire.id,
                'check_in_out': self.check_in_out,
                'somme': self.somme,
                'update': self.update,
                'update_by': self.update_by.id,
                'visibility': self.visibility,
                'chantier_id': self.chantier_id.id,
                'etat': self.etat,

            }
            self.env['agentis.dga'].create(vals)"""

            return {
                'type': 'ir.actions.act_window',
                'name': 'Caisse DGA',
                'view_mode': 'tree,form',
                'tag': 'history_back',
                'target': 'inline',
                'res_model': 'agentis.dga'
            }
        else:
            raise ValidationError("l'entrée/sortie n'est pas une entrée")

    def put_draft(self):
        self.status = 'brouillon'
        if self.check_in_out == 'entrer':
            caisse_line = self.env['account.bank.statement.line'].sudo().search([('caisse_id', '=', self.id)])
            if caisse_line:
                print('............')
                # caisse_line.unlink()
        if self.check_in_out == 'transfert':
            manager = self.env['office.manager'].sudo().search([('caisse_id', '=', 'TRANS' + str(self.id))])
            if manager:
                for man in manager:
                    man.write({'status': 'annule'})
        return True

    def make_facture(self):

        invoice_line_ids = [(0, 0, {
            'name': self.libele,
            'price_unit': self.somme,
            'quantity': 1.0,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'analytic_account_id': self.chantier_id.id or False,
        })]
        action = {'type': 'ir.actions.act_window', 'name': 'Caisse Principale', 'view_mode': 'form', 'target': 'new',
                  'res_model': 'account.payment', 'view_id': self.env.ref('account.view_move_form').id}

        context = {'default_move_type': 'in_invoice',
                   'default_invoice_date': self.create_date,
                   'default_partner_id': self.beneficiaire_is_fournisseur.id,
                   'default_ref': self.name,
                   'default_currency_id': 1,
                   'default_company_id': self.company_id.id,
                   'default_invoice_line_ids': invoice_line_ids,
                   }
        action['context'] = context
        return action

    def export_operation(self):

        action = {'type': 'ir.actions.act_window', 'name': 'Export', 'view_mode': 'form', 'target': 'new',
                  'res_model': 'dga.report', 'view_id': self.env.ref('agentis.view_agentis_dga_export').id}
        return action

    def action_print(self):
        return self.env.ref('agentis.dga_report_id').report_action(self)

    @api.model
    def retrieve_dashboard(self):
        """ This function returns the values to populate the custom dashboard in
            the purchase order views.
        """
        self.check_access_rights('read')

        result = {
            'all_total_validate_dga': 0,
            'all_total_draft_dga': 0,
            'all_total_suspense_dga': 0,
            'all_total_sortie_dga': 0,
            'all_total_entree_dga': 0,
            'company_currency_symbol_dga': self.env.company.currency_id.symbol
        }
        all_total_validate, all_total_draft, all_total_suspense = 0, 0, 0
        office_manager = self.env['agentis.dga'].search([])
        for office in office_manager:
            if office.status == 'attente':
                all_total_suspense = all_total_suspense + office.somme
            elif office.status == 'valide':
                all_total_validate = all_total_validate + office.somme
            elif office.status == 'brouillon':
                all_total_draft = all_total_draft + office.somme

        result['all_total_validate_dga'] = '{:,}'.format(all_total_validate)
        result['all_total_suspense_dga'] = '{:,}'.format(all_total_suspense)
        result['all_total_draft_dga'] = '{:,}'.format(all_total_draft + all_total_suspense)
        return result

    def get_nature_operation(self):

        dga = self.env['agentis.dga'].sudo().search([])
        nature = []
        for dg in dga:
            if dg.nature_operation:
                op = {
                    'id_associeted': dg.id,
                    'nature_operation': dg.nature_operation
                }
                nature.append(op)

        for val in nature:
            self.env['nature.operation'].sudo().create(val)

    '''
    permet de mettre les nouvelle valeur de nature d'operation
    '''

    def new_nature(self):

        nature = self.env['nature.operation'].sudo().search([])
        dga = self.env['agentis.dga'].sudo().search([])

        for na in nature:
            for dg in dga:
                if na.nature_operation == dg.nature_operation:
                    dg.nature_operation_id = na.id


class NatureOperation(models.Model):
    _name = 'nature.operation'
    _rec_name = "nature_operation"

    id_associeted = fields.Integer(string='id caisse')
    nature_operation = fields.Char(string='nature operation')
