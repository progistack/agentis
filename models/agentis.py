# -*- coding: utf-8 -*-

from odoo import models, api, fields


class Agentis(models.Model):
    _name = 'agentis.table'

    name = fields.Char(string='Nom')
    surname = fields.Char(string='Prenom')
    test_check = fields.Char(string='Test')
    priority = fields.Selection([('0', 'Oui'), ('1', 'Non')],
                                "à ne pas déclarer ", default='0')
