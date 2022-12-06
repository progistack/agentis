from odoo import fields, api, models


class CaiseMouvementEmployee(models.Model):
    _inherit = 'hr.employee'

    total_sold = fields.Monetary(string='Solde', default=0)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=False, store=True,
                                  default=lambda self: self.env.company.currency_id)


class CaiseMouvementExpense(models.Model):
    _inherit = 'hr.expense'

    total_sold = fields.Monetary(string='Solde', default=0)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=False, store=True,
                                  default=lambda self: self.env.company.currency_id)