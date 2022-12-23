from odoo import api, fields, models, _


try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class MissionProfile(models.TransientModel):
    _name = 'mission.profile'
    _inherit = 'mail.thread'
    _rec_name = 'nom_prenoms'
    _description = 'Order de mission'

    nom_prenoms = fields.Char(string="Nom et prénom(s)", required=True)
    objet_de_la_mission = fields.Text(string="Objet de la mission", required=True)
    lieu = fields.Char(string="Lieu", required=True)
    start_date = fields.Date(default=fields.date.today(), string="Date de debut", required=True)
    end_date = fields.Date("Date de fin", store=True, required=True)
    translate = fields.Selection([('Avion', 'Avion'), ('Car', 'Car')], string="Moyen de transport", required=True)
    house = fields.Selection([('oui', 'oui'), ('non', 'non')], string="Hébergement", required=True, default='oui')
    food = fields.Selection([('oui', 'oui'), ('non', 'non')], string="Restauration", required=True, default='oui')
    tel = fields.Selection([('oui', 'oui'), ('non', 'non')], string="Téléphone", required=True, default='oui')
    Ta_xi = fields.Selection([('oui', 'oui'), ('non', 'non')], string="Taxi  ", required=True, default='oui')

    name_seq = fields.Char(string='Ordre de reference', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', string='Société:', required=False, default=lambda self: self.env.company)
    chantier_id = fields.Many2one('account.analytic.account', string="Projet")



    """def name_get(self):
        result = []
        for record in self:
            name = f"[id={record.id}] {record.nom_prenoms}"
            result.append((record.id, name))

        return result"""

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('order.mission.sequence') or _('New')
        result = super(MissionProfile, self).create(vals)
        return result

