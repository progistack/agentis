import xlsxwriter
from odoo import models, api, fields
from odoo.http import request
from odoo.tools import float_round


class ProjectReportParser(models.AbstractModel):
    _name = 'report.agentis.agentis_principale_pdf'

    def _get_report_values(self, docids, data=None):
        total_sortie = 0
        total_entree = 0
        solde = 0
        dates = []
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('agentis.agentis_dga_users') and not res_user.has_group('agentis.agentis_dga'):
            dga = self.env['agentis.dga'].search([('id', '=', data['ids']), ('prive', '=', False)])

            for line in dga:
                if line.check_in_out == 'entrer':
                    total_entree += abs(line.somme)
                else:
                    total_sortie += abs(line.somme)
            solde = total_entree - total_sortie
            solde = '{:,}'.format(solde).replace(',', ' ')
            total_sortie = float_round(total_sortie, 0)
            total_sortie = '{:,}'.format(total_sortie).replace(',', ' ')
            total_entree = float_round(total_entree, 0)
            total_entree = '{:,}'.format(total_entree).replace(',', ' ')
            for val in dga:
                dates.append(val.create_date)

            dic = {
                'docs': dga,
                'total_sortie': total_sortie,
                'total_entree': total_entree,
                'solde': solde
            }
            if len(dates) > 0:
                dic.update(
                    {'start_date': min(dates) or None,
                     'end_date': max(dates) or None
                     })
            return dic
        else:
            dga = self.env['agentis.dga'].search([('id', '=', data['ids'])])
            print('search ............', dga)
            for line in dga:
                if line.check_in_out == 'entrer':
                    total_entree += abs(line.somme)
                else:
                    total_sortie += abs(line.somme)
            solde = total_entree - total_sortie
            solde = '{:,}'.format(solde).replace(',', ' ')
            total_sortie = float_round(total_sortie, 0)
            total_sortie = '{:,}'.format(total_sortie).replace(',', ' ')
            total_entree = float_round(total_entree, 0)
            total_entree = '{:,}'.format(total_entree).replace(',', ' ')
            for val in dga:
                dates.append(val.create_date)

            dic = {
                'docs': dga,
                'total_sortie': total_sortie,
                'total_entree': total_entree,
                'solde': solde
            }
            if len(dates) > 0:
                dic.update(
                    {'start_date': min(dates) or None,
                     'end_date': max(dates) or None
                     })
            return dic
