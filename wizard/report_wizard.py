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


class DGAReportWizard(models.TransientModel):
    _name = 'dga.report.wizard'

    start_date = fields.Date(string='Date Début')
    end_date = fields.Date(string='Date fin')
    fideca = fields.Boolean(string='FIDECA', default=False)
    facture_type = fields.Selection(
        [('employee', 'Employé'), ('client', 'Client'), ('fournisseur', 'Fournisseur')],
        "type facture", default='employee')
    type_caisse = fields.Selection([('dga', 'DGA'), ('manager', 'Office manager'), ('comptable', 'Comptable')],
                                   'Type de caisse')
    company_id = fields.Many2one('res.company', string='Société',
                                 default=lambda self: self.env.company)

    def export_data_pdf(self):
        data = {'start_date': self.start_date, 'end_date': self.end_date}
        return self.env.ref('agentis.agentis_dga_principale_pdf').report_action([], data=data)

    def export_datas(self):
        print('bonjour .....', self.type_caisse)
        for i in self:
            print('self val ....', i)
        start_date = self.start_date
        end_date = self.end_date
        fideca = self.fideca
        company_id = self.company_id.id
        datas = []
        if self.type_caisse == 'comptable':
            datas = self.env['agentis.comptable'].search([('create_date', '>=', start_date),
                                                          ('create_date', '<=', end_date), ('fideca', '=', fideca)])
        elif self.type_caisse == 'dga':
            datas = self.env['agentis.dga'].search([('create_date', '>=', start_date),
                                                    ('create_date', '<=', end_date)])
        elif self.type_caisse == 'manager':
            datas = self.env['office.manager'].search([('create_date', '>=', start_date),
                                                       ('create_date', '<=', end_date),
                                                       ('fideca', '=', fideca),
                                                       ('company_id', '=', company_id)])

        # getting working module where your current python file (model.py) exists
        # path = os.path.dirname(os.path.realpath(__file__))

        """
        For custom addons path, use :
        
        path = os.path.dirname(os.getcwd()) + "addons location"  # odoo directory
        
        """

        """
        my local path : \\progistack\\agentis\\static\\exports\\
        use the default addons:
        path = os.getcwd() + '\\addons\\agentis\\static\\'  "mnt/extra-addons/agentis/static/exports" """

        path = os.path.dirname(os.getcwd()) + "opt/odoo/customs_addons/agentis/static/exports"
        # creating dynamic path to create zip file
        name = self.type_caisse + '-' + str(start_date) + '-to-' + str(end_date)
        file_name = name
        file_name_zip = file_name + ".zip"
        zipfilepath = os.path.join(path, file_name_zip)
        # creating zip file in above mentioned path
        table_header_comp = ['N° Chèque', 'Libellé', 'Nature Paiement', 'Employé', 'Client/Fournisseur',
                             'Employé Bénéficiaire', 'Entrée/Sortie', 'Chantier', 'Date', 'Date prévue', 'Sommes']
        table_header = ['N° BC', 'Libellé', 'Numéro facture', 'Entreprise', 'Employé',
                        'Bénéficiaire', 'Entrée/Sortie', 'Projet', 'Date', 'Sommes']
        with zipfile.ZipFile(zipfilepath, "w") as zip_archive:
            # all for one
            fp = io.BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            worksheet = workbook.add_worksheet()
            row = 1
            inc = 0
            dir_name = 'Mouvement du ' + str(start_date) + '-au-' + str(end_date)
            if self.type_caisse == 'comptable':
                for i in table_header_comp:
                    worksheet.write(0, inc, i)
                    inc = inc + 1
            else:
                inc = 0
                for i in table_header:
                    worksheet.write(0, inc, i)
                    inc = inc + 1

            for data in datas:
                if self.type_caisse == "comptable":
                    worksheet.write(1, 0, data.num_piece)
                    worksheet.write(1, 1, data.libele)
                    worksheet.write(1, 2, data.nature_payment)
                    if data.payment_with_employee:
                        worksheet.write(1, 3, data.payment_with_employee.name)
                    else:
                        worksheet.write(1, 3, '')
                    if data.payment_with_other:
                        worksheet.write(1, 4, data.payment_with_other.name)
                    else:
                        worksheet.write(1, 4, '')
                    if data.beneficiaire_employee:
                        worksheet.write(1, 5, data.beneficiaire_employee.name)
                    else:
                        worksheet.write(1, 5, '')
                    worksheet.write(1, 6, data.check_in_out)
                    worksheet.write(1, 7, data.chantier_id.name)
                    format2 = workbook.add_format({'num_format': 'dd/mm/yy'})
                    worksheet.write(1, 8, data.date, format2)
                    worksheet.write(1, 9, data.date_prevue, format2)
                    worksheet.write(1, 10, abs(data.somme))
                else:

                    if self.type_caisse == 'dga':
                        if data.num_caisse:
                            worksheet.write(row, 0, data.num_caisse)
                        else:
                            worksheet.write(row, 0, ' ')
                    else:
                        if data.name:
                            worksheet.write(row, 0, data.name)
                        else:
                            worksheet.write(row, 0, ' ')
                    if data.libele:
                        worksheet.write(row, 1, data.libele)
                    else:
                        worksheet.write(row, 1, '')
                    if self.type_caisse == 'dga':
                        if data.name:
                            worksheet.write(row, 2, data.name)
                        else:
                            worksheet.write(row, 2, '')
                    else:
                        if data.num_facture:
                            worksheet.write(row, 2, data.num_facture)
                        else:
                            worksheet.write(row, 2, '')
                    if data.company_id:
                        worksheet.write(row, 3, data.company_id.name)
                    else:
                        worksheet.write(row, 3, '')
                    if data.beneficiaire_employee:
                        worksheet.write(row, 4, data.beneficiaire_employee.name)
                    else:
                        worksheet.write(row, 4, '')
                    if data.beneficiaire_is_fournisseur:
                        worksheet.write(row, 5, data.beneficiaire_is_fournisseur.name)
                    else:
                        worksheet.write(row, 5, '')
                    worksheet.write(row, 6, data.check_in_out)
                    if data.chantier_id:
                        worksheet.write(row, 7, data.chantier_id.name)
                    else:
                        worksheet.write(row, 7, '')
                    format2 = workbook.add_format({'num_format': 'dd/mm/yy'})
                    worksheet.write(row, 8, data.date, format2)
                    worksheet.write(row, 9, abs(data.somme))
                    row += 1

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            file_download = base64.b64decode(file_download)
            fp.close()
            object_name = "/opt/odoo/customs_addons/agentis/static/exports/excel.xlsx"
            object_handle = open(object_name, "wb")
            object_handle.write(file_download)
            object_handle.close()
            # save xlsx report
            zip_archive.write(object_name, dir_name + '.xlsx')
            if self.type_caisse == 'manager' or self.type_caisse == "comptable":
                for data in datas:
                    if self.type_caisse == 'dga':
                        if data.num_caisse:
                            dir_name = data.num_caisse
                        else:
                            dir_name = 'Caisse principale'
                    else:
                        dir_name = data.name
                    fp = io.BytesIO()
                    workbook = xlsxwriter.Workbook(fp)
                    worksheet = workbook.add_worksheet()

                    if self.type_caisse == "comptable":
                        inc = 0
                        for i in table_header_comp:
                            worksheet.write(0, inc, i)
                            inc = inc + 1
                        worksheet.write(1, 0, data.num_piece)
                        worksheet.write(1, 1, data.libele)
                        worksheet.write(1, 2, data.nature_payment)
                        if data.payment_with_employee:
                            worksheet.write(1, 3, data.payment_with_employee.name)
                        else:
                            worksheet.write(1, 3, '')
                        if data.payment_with_other:
                            worksheet.write(1, 4, data.payment_with_other.name)
                        else:
                            worksheet.write(1, 4, '')
                        if data.beneficiaire_employee:
                            worksheet.write(1, 5, data.beneficiaire_employee.name)
                        else:
                            worksheet.write(1, 5, '')
                        worksheet.write(1, 6, data.check_in_out)
                        worksheet.write(1, 7, data.chantier_id.name)
                        format2 = workbook.add_format({'num_format': 'dd/mm/yy'})
                        worksheet.write(1, 8, data.date, format2)
                        worksheet.write(1, 9, data.date_prevue, format2)
                        worksheet.write(1, 10, abs(data.somme))

                    else:
                        inc = 0
                        row = 1
                        for i in table_header:
                            worksheet.write(0, inc, i)
                            inc = inc + 1
                        if self.type_caisse == 'dga':
                            if data.num_caisse:
                                worksheet.write(row, 0, data.num_caisse)
                            else:
                                worksheet.write(row, 0, ' ')
                        else:
                            if data.num_bon:
                                worksheet.write(row, 0, data.num_bon)
                            elif data.name:
                                worksheet.write(row, 0, data.name)
                            else:
                                worksheet.write(row, 0, ' ')
                        if data.libele:
                            worksheet.write(row, 1, data.libele)
                        else:
                            worksheet.write(row, 1, '')
                        if self.type_caisse == 'dga':
                            if data.name:
                                worksheet.write(row, 2, data.name)
                            else:
                                worksheet.write(row, 2, '')
                        else:
                            if data.num_facture:
                                worksheet.write(row, 2, data.num_facture)
                            else:
                                worksheet.write(row, 2, '')
                        if data.company_id:
                            worksheet.write(row, 3, data.company_id.name)
                        else:
                            worksheet.write(row, 3, '')
                        if data.beneficiaire_employee:
                            worksheet.write(row, 4, data.beneficiaire_employee.name)
                        else:
                            worksheet.write(row, 4, '')
                        if data.beneficiaire_is_fournisseur:
                            worksheet.write(row, 5, data.beneficiaire_is_fournisseur.name)
                        else:
                            worksheet.write(row, 5, '')
                        worksheet.write(row, 6, data.check_in_out)
                        if data.chantier_id:
                            worksheet.write(row, 7, data.chantier_id.name)
                        else:
                            worksheet.write(row, 7, '')
                        format2 = workbook.add_format({'num_format': 'dd/mm/yy'})
                        worksheet.write(row, 8, data.date, format2)
                        worksheet.write(row, 9, abs(data.somme))
                    workbook.close()

                    file_download = base64.b64encode(fp.getvalue())
                    file_download = base64.b64decode(file_download)
                    fp.close()
                    object_name = "/opt/odoo/customs_addons/agentis/static/exports/excel.xlsx"
                    object_handle = open(object_name, "wb")
                    object_handle.write(file_download)
                    object_handle.close()
                    # save xlsx report
                    zip_archive.write(object_name, dir_name + '/' + dir_name + '.xlsx')

                    for file in data.attachment_ids:
                        decoded_data = base64.b64decode(file.datas)
                        # creating file name (like example.txt) in which we have to write binary field data or attachment
                        object_name = "/opt/odoo/customs_addons/agentis/static/exports" + file.name
                        object_path = dir_name + '/' + file.name
                        object_handle = open(object_name, "wb")
                        # writing binary data into file handle
                        object_handle.write(decoded_data)
                        object_handle.close()
                        # writing file into zip file
                        zip_archive.write(object_name, object_path)

        # code snipet for downloading zip file
        return {
            'type': 'ir.actions.act_url',
            'url': str('/agentis/static/exports/' + name + '.zip'),
            'target': 'new'
        }
