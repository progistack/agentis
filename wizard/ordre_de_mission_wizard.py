from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import json
import datetime
import pytz
import io
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools import date_utils
import os
import zipfile
import base64
import xlsxwriter
import io

# import xml.etree.ElementTree as ElementTree


try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class MissionProfile(models.TransientModel):
    _name = 'mission.profile'

    nom_prenoms = fields.Char(string="Nom et prénom(s)", required=True)
    objet_de_la_mission = fields.Char(string="Objet de la mission", required=True)
    lieu = fields.Char(string="Lieu", required=True)
    date_debut = fields.Date("Date de debut", required=True)
    date_fin = fields.Date("Date de fin", required=True)
    translate = fields.Selection([('Avion', 'Avion'), ('Car', 'Car')], string="Moyen de transport", required=True)
    house = fields.Char(string="Hébergement", default="oui", required=True)
    resto = fields.Char(string="Restauration", default="oui", required=True)
    tel_phone = fields.Char(string="Téléphone", default="oui", required=True)
    T_xi = fields.Char(string="Taxi", default="oui", required=True)



    @api.model
    def _get_default_name(self):
        return "test"