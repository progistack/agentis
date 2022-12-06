from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class InheritAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    agentis_tags = fields.Many2many('agentis.tags', store=True, string='Numéros de marché', readonly=False)
    contrat_id = fields.One2many('agentis.contrat', 'inherit_analytic_id', string='montant du Contrat', copy=True,
                                 readonly=False)
    total = fields.Float(string="Total :", compute='_get_total_chantier')
    project_total = fields.Float(string="Total :", compute='_get_total_project')
    somme_sortie = fields.Float(string="Somme Sortie", compute='get_somme_sortie')
    ecart = fields.Float(string='Ecart', compute='get_ecart')
    domiciliation = fields.Many2one('account.journal', required=False, check_company=True, string='domiciliation')
    identify_uni = fields.Char(string='Identifiant Unique')
    taux = fields.Char(string='Taux de réalisation', compute='get_taux_realise')
    origin_fond = fields.Many2many('origin.fond', store=True, string='origine des fonds', readonly=False)
    is_particular_company = fields.Boolean('appartient à une société')

    @api.onchange('name')
    def onchange_name(self):
        pass

    @api.depends('contrat_id.amount')
    def _get_total_chantier(self):
        for agentis_dga in self:
            amount1 = 0
            for val in agentis_dga.contrat_id:
                amount1 = amount1 + val.amount
            agentis_dga.total = amount1
            agentis_dga.identify_uni = 'CA' + str(agentis_dga._origin.id)
            agentis_dga.contrat_id.identify_uni = 'CA' + str(agentis_dga._origin.id)

    @api.depends('total')
    def get_somme_sortie(self):
        manager = self.env['office.manager']
        mouvement = self.env['account.payment']
        for val in self:
            total_manager = 0
            total_mouvement = 0
            sortie_mouvement = manager.search([('chantier_id', '=', val.id), ('check_in_out', '=', 'sortie'),('status', '=', 'valide')]).mapped('somme')
            entree_mouvement = mouvement.search([('chantier_id', '=', val.id), ('partner_type', '=', 'supplier'), ('type_caisse', '!=', 'manager')]).mapped('amount')

            """for sortie in sortie_manager:
                total_manager = total_manager + sortie"""
            for sort in entree_mouvement:
                total_mouvement = total_mouvement + sort
            for som in sortie_mouvement:
                total_manager += som
            val.somme_sortie = abs(total_mouvement) + abs(total_manager)

    @api.depends('project_total', 'somme_sortie')
    def get_ecart(self):
        for val in self:
            ecart = 0
            ecart = val.project_total - abs(val.somme_sortie)
            val.ecart = ecart

    @api.depends('total')
    def _get_total_project(self):
        for agentis_dga in self:
            amount1 = 0
            for val in agentis_dga.contrat_id:
                amount1 = amount1 + val.amount
            agentis_dga.project_total = amount1

    @api.depends('somme_sortie')
    def get_taux_realise(self):
        total = 0
        for val in self:
            if val.project_total != 0:
                total = (val.somme_sortie * 100) / abs(val.project_total)
                total = round(total, 2)
                val.taux = str(total) + '%'
            else:
                val.taux = '0 %'

    def open_analyse_view(self):
        action = {'type': 'ir.actions.act_window', 'name': 'Analyse projet', 'view_mode': 'tree', 'target': 'current',
                  'res_model': 'account.analytic.account', 'view_id': self.env.ref('agentis'
                                                                                   '.view_agentis_analyse_tree_view').id}
        domain = [('name', '=', self.name)]
        action['domain'] = domain
        return action

    @api.model
    def create(self, vals_list):
        is_company = vals_list.get('is_particular_company')

        if (not is_company) and (not vals_list.get('domiciliation')):
            vals_list['company_id'] = None

        name = vals_list.get('name')
        account_analytic = self.env['account.analytic.account'].search([]).mapped('name')
        for value in account_analytic:
            if value.upper() == name.upper():
                raise ValidationError(
                    _("Ce projet existe déjà !")
                )
        return super(InheritAnalyticAccount, self).create(vals_list)


