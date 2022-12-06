from odoo import fields, models, api, tools


class AgentisConsolidated(models.Model):
    _name = 'consolidated.body'
    _auto = False
    _description = 'rapport des caisses'

    create_date = fields.Date(string='Date de création:')
    libele = fields.Text(string='Libellé:', default='aucun')
    somme = fields.Float(string='Montant payé:', help="Montant de l'opération")
    name = fields.Char(string='Reference facture')
    move_id = fields.Many2one('account.move', string='Facture Associée')
    chantier_id = fields.Many2one('account.analytic.account', string="Projet")
    partner_id = fields.Many2one('res.partner', string='Béneficiaire')
    bank_reception = fields.Many2one('agentis.bank', string='Banque Reception')
    methode_payment = fields.Selection(
        [('virement', 'Virement'), ('versement', 'Versement'), ('misedispo', 'Mise à Disposition'),
         ('chequebarre', 'Chèque Barré'), ('chequenonbarre', 'Chèque Non Barré'), ('espece', 'Espèce'),('prele', 'Prélèvement')],
        "Méthode de paiément")
    type_operation = fields.Selection([('local', 'Local'), ('inter', 'International')], "Type d'operation")
    nature_operation = fields.Char(string='Nature opération')
    company_id = fields.Many2one('res.company', string='Société')
    user_id = fields.Many2one('res.users', string='Crée par')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'consolidated_body')
        self.env.cr.execute('''CREATE OR REPLACE VIEW consolidated_body AS ( SELECT min(bk.id) as id,bk.payment_ref 
        AS libele, bk.num_transaction AS name,bk.amount AS somme,bk.partner_id AS partner_id,bk.create_date AS 
        create_date,bk.bank_reception AS bank_reception,bk.methode_payment AS methode_payment,bk.type_operation AS 
        type_operation, bk.chantier_id AS chantier_id,bk.move_id AS move_id,bk.nature AS nature_operation,
        bk.company_id AS company_id,bk.create_uid AS user_id FROM account_bank_statement_line bk WHERE bk.amount < 0 GROUP BY create_date,
        libele,name,somme,partner_id, bank_reception,chantier_id,methode_payment,type_operation,move_id,
        nature_operation,company_id,user_id)''')

    @api.depends('move_id')
    def get_company(self):
        for move in self:
            print('coùmpany id is .............', move.company_id)
            move.company_id = move.move_id.company_id
