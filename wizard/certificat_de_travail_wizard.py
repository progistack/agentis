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


class CertificatProfile(models.TransientModel):
    _name = 'certificat.profile'

    nom_prenoms = fields.Char(string="Nom et prénom(s)")
    societe = fields.Char(string="Nom de la société")
    capital = fields.Char(string="Capital de la société")
    adresse_postal = fields.Char(string="Adresse postal")



