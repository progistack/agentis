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
from time import strftime
# import xml.etree.ElementTree as ElementTree


try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class AttestationProfile(models.TransientModel):
    _name = 'attestation.profile'

    nom_prenoms_de_employe = fields.Char(string="Nom et prénom de l'employé")
    poste_occupe = fields.Char(string="Poste occupé")
    nom_societe = fields.Char(string="Nom de la sociéte")



    @api.model
    def test(self):
        print('Bonjour tout le monde')