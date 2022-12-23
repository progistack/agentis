# -*- coding: utf-8 -*-

from odoo import models, api, fields


class AgentisChantier(models.Model):
    _name = 'agentis.chantier'

    name = fields.Char(string='Nom du chantier')
    agentis_pga_id = fields.One2many('agentis.dga', 'chantier_id', string='DGA')
    agentis_office_id = fields.One2many('office.manager', 'chantier_id', string='Office manager')
    description = fields.Text(string='Description')
    client = fields.Many2one('res.partner', string='Client')


class AgentisBank(models.Model):
    _name = 'agentis.bank'

    name = fields.Char(string='Nom banque: ')
    code = fields.Char(string='Code')
