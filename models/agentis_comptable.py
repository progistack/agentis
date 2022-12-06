from datetime import datetime
from random import randint

import pytz
from num2words import num2words

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AgentisComptable(models.Model):
    _name = 'agentis.comptable'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _order = 'name DESC, create_date DESC'
    _description = 'mouvement bancaire'
    _check_company_auto = True

    @api.model
    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    create_date = fields.Date(string='Date de création:', default=_default_time_utc, readonly=True)
    date = fields.Date(string='Date ', default=_default_time_utc)
    libele = fields.Text(string='Libellé:', default='aucun')
    num_facture = fields.Char(string="Numéro facture:", require=True)
    nature_payment = fields.Selection([('espece', 'Espèce'), ('autre', 'Autre')], default='espece')
    payment_with = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('autre', 'Autre')],
        "Par l’intermédiaire de:", default='employee')
    payment_with_employee = fields.Many2one('hr.employee', string='Employé:', check_company=True)
    payment_with_fourn = fields.Many2one('res.partner', string='Fournisseur:', check_company=True)
    payment_with_client = fields.Many2one('res.partner', string='Client:', check_company=True)
    payment_with_other = fields.Many2one('res.partner', string='Par l’intermédiaire de:', check_company=True)
    beneficiaire_is = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur'), ('autre', 'Autre')],
        "Partenaire:", default='employee')
    beneficiaire_employee = fields.Many2one('hr.employee', string='Employé Bénéficiaire:', check_company=True)
    beneficiaire_is_client = fields.Many2one('res.partner', string='Client Bénéficiaire:', check_company=True)
    beneficiaire_is_fournisseur = fields.Many2one('res.partner', string='Fournisseur Bénéficiaire:', check_company=True)
    beneficiaire_is_other = fields.Many2one('res.partner', string='Autre Bénéficiaire:', check_company=True)
    check_in_out = fields.Selection([('entrer', 'Entrée'), ('sortie', 'Sortie')], 'Entrée/Sortie', default='sortie')
    somme = fields.Float(string='Somme:')
    update = fields.Datetime(string='Mise à jour le:')
    update_by = fields.Many2one('res.users', string='Mise à jour par:')
    visibility = fields.Selection([('0', 'Oui'), ('1', 'Non')],
                                  "à ne pas déclarer ?", default='1')
    name = fields.Char(string="N° de bon")
    chantier_id = fields.Many2one('account.analytic.account', string="Projet",
                                  check_company=True)  # , 'agentis_office_id'
    etat = fields.Boolean(string='etat')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  default=lambda self: self.env.company.currency_id)
    solde = fields.Monetary(string='Somme', compute='get_solde', store=True, currency_field='currency_id')
    somme_in = fields.Float(string=' Somme', compute='get_somme_in')
    somme_out = fields.Float(string='Somme', compute='get_somme_out')
    is_create = fields.Boolean(string='est crée')
    insible_somme = fields.Boolean(string='somme visble ou non')

    donne_a_client = fields.Many2one('res.partner', string='Donné à :', check_company=True)
    donne_a_employe = fields.Many2one('hr.employee', string='Donné à :', check_company=True)
    status = fields.Selection([('brouillon', 'BROUILLONS'), ('attente', 'EN ATTENTE'), ('valide', 'VALIDE')],
                              default='brouillon')
    company_id = fields.Many2one('res.company', string='Société:', required=True, default=lambda self: self.env.company)
    product_id = fields.Many2one(
        'product.product', 'Product', required=False, default=0)
    journal_id = fields.Many2one('account.journal', string='Journal comptable:', required=True, check_company=True)
    tax_id = fields.Many2one('account.tax', string='Taxe:')
    facture_id = fields.Integer(string='id facture')
    payment_id = fields.Integer(string='id payment')
    date_prevue = fields.Date(string='Date Effective:', default=_default_time_utc)
    file = fields.Binary(string="Fichier")
    file_name = fields.Char(string='nom fichier')
    num_piece = fields.Char(string='Numéro de chèque')
    type_caisse = fields.Selection([('dga', 'DGA'), ('manager', 'Office manager'), ('comptable', 'Comptable')],
                                   'Type de caisse')
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='agentis_comptable_id',
        string='Charger vos fichiers:')
    bank_reception = fields.Many2one('agentis.bank', string='Banque Emettrice')
    methode_payment = fields.Selection(
        [('virement', 'Virement'), ('versement', 'Versement'), ('misedispo', 'Mise à Disposition'),
         ('chequebarre', 'Chèque Barré'), ('chequenonbarre', 'Chèque Non Barré'), ('espece', 'Espèce')],
        "Méthode de paiément", default='virement')
    total_somme = fields.Float(string='somme total', compute='get_total_somme')
    somme_lettre = fields.Char(string='Somme lettre')
    fideca = fields.Boolean(string='FIDECA')
    type_operation = fields.Selection([('local', 'Local'), ('inter', 'International')], "Type d'operation",
                                      default='local')
    date_escompte = fields.Date(string="Date d'escompte")
    origin_fond = fields.Many2many('origin.fond', store=True, string='origine des fonds', readonly=False)
    total_with_tax = fields.Float(string='Montant avec taxe', compute='get_total_with_tax')
    borderau = fields.Boolean(string='Borderau de livraison')
    num_borderau = fields.Char(string='N° Borderau')
    num_contrat = fields.Many2one('agentis.contrat', string='Numéro du contrat')
    identify_uni = fields.Char(string='Identifiant Unique')
    somme_char = fields.Char(string='somme en caractere', compute='get_somme_char')

    @api.onchange('chantier_id')
    def get_contrat_num(self):
        for val in self:
            val.identify_uni = val.chantier_id.identify_uni

    @api.depends('somme', 'tax_id')
    def get_total_with_tax(self):
        for val in self:
            amount_t = self.env['account.tax'].sudo().search([('id', '=', val.tax_id.ids)])
            amount_tax = 0
            if amount_t:
                amount_tax = amount_t.amount
            val.total_with_tax = abs(val.somme) + (amount_tax * abs(val.somme)) / 100

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
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('ban.sequence')
        vals['type_caisse'] = 'comptable'
        in_out = vals['check_in_out']
        if in_out == 'sortie' and not vals['etat']:
            if vals['somme'] != 0:
                vals['somme'] = - vals['somme']
        vals['update_by'] = self.env.uid
        vals['update'] = self.generate_update()
        vals['etat'] = True
        if 'visibility' in vals and vals['visibility'] == '0':
            vals['insible_somme'] = True
        result = super(AgentisComptable, self).create(vals)
        return result

    def write(self, vals):
        print('test------', vals)
        for val in vals:
            print("element modifier .........", val)
            self.message_post(body=str(val) + " ==>" + str(vals[val]))
        if self.check_in_out == 'sortie' and 'somme' in vals:
            if vals['somme'] > 0:
                print('55555555555555')
                vals['somme'] = - vals['somme']
        vals['update_by'] = self.env.uid
        vals['update'] = self.generate_update()
        result = super(AgentisComptable, self).write(vals)
        return result

    def unlink(self):
        for val in self:
            if val.status == 'valide' or val.status == 'attente':
                raise ValidationError(
                    _("Vous ne pouvez pas supprimer une opération validée ou en attente, veuillez mettre en brouillon d'abord !"))
        return super(AgentisComptable, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        print('duplication self', self)
        print('duplication self', default)
        if 'name' not in default:
            default['name'] = _("%s (Copy)") % self.name
        if 'status' not in default:
            default['status'] = 'brouillon'
        return super(AgentisComptable, self).copy(default=default)

    @api.depends('somme')
    def get_solde(self):
        amount = 0
        for agentis_dga in self:
            amount = int(amount + agentis_dga.somme)
            agentis_dga.solde = amount

    def put_suspense(self):
        print('self ------', self)
        self.status = 'attente'
        for val in self:
            val.message_post(body="satus ==> En attente")
        return True

    def get_employee_in_partner(self, employee):
        if employee:
            partner = self.env['res.partner'].sudo().search([('user_associe_id', '=', employee.id)])
            if partner:
                return partner.id
            else:
                return employee.id

    def validate_operation(self):
        for mov in self:
            if mov.status != 'valide':
                mov.status = 'valide'
                amount_t = self.env['account.tax'].sudo().search([('id', '=', mov.tax_id.ids)])
                amount_tax = amount_t.amount
                coeff = amount_t.exclude_amount
                invoice_vals = {
                    'type_caisse': 'comptable',
                    'caisse_id': 'MOUV' + str(mov.id),
                    'associe_id': mov.id,
                    'borderau': mov.borderau,
                    'num_borderau': mov.num_borderau,
                    'ref': mov.name,
                    'payment_reference': mov.num_piece,
                    'name': mov.num_facture,
                    'move_type': 'out_invoice',
                    'invoice_origin': mov.name,
                    'narration': '',
                    'somme_lettre': num2words((abs(mov.somme) + (amount_tax * abs(mov.somme)) / 100),
                                              lang='fr') + ' FCFA',
                    'partner_id': (
                            mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client).id,
                    'commercial_partner_id': (
                            mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client).id,
                    'currency_id': mov.currency_id.id,
                    'state': 'draft',
                    'invoice_date': mov.date_prevue,
                    'invoice_partner_display_name': (
                            mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client).name,
                    'invoice_line_ids': [(0, 0, {
                        'name': mov.libele,
                        'price_unit': abs(mov.somme),
                        'quantity': 1.0,
                        'product_id': 1,
                        'product_uom_id': mov.product_id.uom_id.id,
                        'analytic_account_id': mov.chantier_id.id or False,
                        'tax_ids': [(6, 0, mov.tax_id.ids)]
                    })],
                }
                if mov.tax_id.exclude_tax:
                    invoice_vals.update({'tax_exclude': (coeff * abs(mov.somme)) / 100, 'tax_exclude_visible': True,
                                         'somme_lettre': num2words((abs(mov.somme)), lang='fr') + ' ' + ' FCFA'})
                else:
                    invoice_vals.update(
                        {'somme_lettre': num2words((abs(mov.somme) + (amount_tax * abs(mov.somme)) / 100),
                                                   lang='fr') + ' ' + ' FCFA'})

                if mov.beneficiaire_is == 'client':
                    invoice_vals.update({'move_type': 'out_invoice'})
                    resut = self.env['account.move'].sudo().create(invoice_vals)
                    mov.facture_id = resut.id

                elif mov.beneficiaire_is == 'fournisseur':
                    invoice_vals.update({'move_type': 'in_invoice'})
                    resut = self.env['account.move'].sudo().create(invoice_vals)
                    mov.facture_id = resut.id

                for payment in mov:
                    print('88888888888888888', payment.id)
                    paired_payment = {
                        'type_caisse': 'comptable',
                        'caisse_id': 'MOUV' + str(payment.id),
                        'associe_id': payment.id,
                        'journal_id': payment.journal_id.id,
                        'destination_journal_id': payment.journal_id.id,
                        'move_id': None,
                        'partner_id': (
                                payment.beneficiaire_is_fournisseur or payment.beneficiaire_employee or payment.beneficiaire_is_client).id,
                        'amount': abs(payment.somme) + (amount_tax * abs(payment.somme)) / 100,
                        'ref': payment.name,
                        'date': payment.create_date,
                    }
                    '''
                    if self.beneficiaire_is == 'client':
                        print('.......................................ggg')
                        paired_payment.update({'payment_type': 'inbound'})
                        paired_payment.update({'partner_type': 'customer'})
                        resul = self.env['account.payment'].sudo().create(paired_payment)
                        self.payment_id = resul.id
        
                    elif self.beneficiaire_is == 'fournisseur':
                        print('---------------------------------------------gg')
                        paired_payment.update({'payment_type': 'outbound'})
                        paired_payment.update({'partner_type': 'supplier'})
                        resul = self.env['account.payment'].sudo().create(paired_payment)
                        self.payment_id = resul.id
                        '''

                all_val = {
                    'name': 'MOUV BAN du ' + (str(mov.create_date)),
                    'journal_id': mov.journal_id.id,
                    'date': mov.create_date,
                    'company_id': mov.company_id.id,
                    'line_ids': [(0, 0, {
                        'date': mov.create_date,
                        'payment_ref': (mov.libele or mov.create_date),
                        'num_transaction': mov.num_piece,
                        'partner_id': mov.get_employee_in_partner(
                            mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client),
                        'amount': mov.somme,
                        'caisse_id': mov.id
                    })]
                }
                date_day = mov._default_time_utc()
                caisse_dga = self.env['account.bank.statement'].sudo().search(
                    [('date', '=', mov.create_date), ('journal_id', '=', mov.journal_id.id)])
                if caisse_dga:
                    if date_day.strftime('%Y-%m-%d') == str(mov.create_date):
                        line = {
                            'date': mov.create_date,
                            'line_ids': [(0, 0, {
                                'date': mov.create_date,
                                'payment_ref': mov.libele,
                                'num_transaction': mov.num_piece,
                                'partner_id': mov.get_employee_in_partner(
                                    mov.beneficiaire_is_fournisseur or mov.beneficiaire_employee or mov.beneficiaire_is_client),
                                'amount': mov.somme,
                                'caisse_id': mov.id
                            })]
                        }
                        caisse_dga.write(line)
                        print('ici -------')
                    else:
                        self.env['account.bank.statement'].sudo().create(all_val)
                else:
                    self.env['account.bank.statement'].sudo().create(all_val)
                for val in mov:
                    val.message_post(body="satus ==> Validé")
        return True

    def put_draft(self):
        self.status = 'brouillon'
        facture = self.env['account.move'].sudo().search([('id', '=', self.facture_id)])
        if facture.state == 'posted':
            raise ValidationError(_('Vous ne pouvez pas remettre en brouillon une opération déjà comptabilisée'))
        else:
            facture.unlink()
            self.env['account.payment'].sudo().search([('id', '=', self.payment_id)]).unlink()
        for val in self:
            val.message_post(body="satus ==> Brouillon")
        return True

    def generate_update(self):
        locale_time = datetime.now()
        return locale_time

    def generate_num_bon(self):
        init = 'COM'

    def open_journal_sold(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Solde', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.bank.statement', 'view_id': False}
        domain = ([('name', '=', 'MOUV BAN du ' + (str(self.create_date))), ('journal_id', '=', self.journal_id.id)])
        action['domain'] = domain
        return action

    def open_payment(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Paiements', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.payment', 'view_id': False}

        domain = ([('caisse_id', '=', 'MOUV' + str(self.id))])
        action['domain'] = domain
        return action

    def open_facture(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Factures', 'view_mode': 'tree,form', 'view_type': 'form',
                  'res_model': 'account.move', 'view_id': False}
        if self.beneficiaire_is == 'fournisseur':
            print('*********************')
            domain = ([('caisse_id', '=', 'MOUV' + str(self.id)), ('move_type', '=', 'in_invoice')])
            action['domain'] = domain
        elif self.beneficiaire_is == 'client':
            print('......................')
            domain = ([('caisse_id', '=', 'MOUV' + str(self.id)), ('move_type', '=', 'out_invoice')])
            action['domain'] = domain
        return action


class OriginFond(models.Model):
    _name = 'origin.fond'

    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(string='Color Index', default=_get_default_color)
    name = fields.Char(struct='Nom')
