from random import randint

from odoo import fields, models


class AgentisTags(models.Model):
    _name = 'agentis.tags'

    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(string='Color Index', default=_get_default_color)
    name = fields.Char(struct='Nom')
