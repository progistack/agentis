from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class InheritEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_type = fields.Selection([('employee', 'Employé'), ('partner', 'partner')])

    nom_prenoms_de_employe = fields.Char(string="Nom et prénom de l'employé")
    poste_occupe = fields.Char(string="Poste occupé")
    nom_societe = fields.Char(string="Nom de la sociéte")
    date_du_jour = fields.Date("Date du jour")

    def print_attestation(self):
        return self.env.ref('agentis.agentis_print_attestation_travail').report_action(self)

    def print_certificat(self):
        return self.env.ref('agentis.agentis_print_certificat_travail').report_action(self)

    @api.model
    def create(self, vals_list):
        """ crée un employee comme partner lors de la creation de employee"""
        val = {
            'name': vals_list['name'],
            'company_type': 'person',
            'employee_type': 'employee'
        }
        if 'phone' in vals_list:
            val.update({'phone': vals_list['phone']})
        if 'private_email' in vals_list:
            val.update({'email': vals_list['private_email']})
        if 'work_email' in vals_list:
            val.update({'email': vals_list['work_email']})
        res = super(InheritEmployee, self).create(vals_list)
        print("nameee", res.name)
        partner = self.env['res.partner'].search([('name', '=', res.name)]).mapped('name')
        val.update({'user_associe_id': res.id})
        if not partner:
            self.env['res.partner'].create(val)
        return res


class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    employee_type = fields.Selection([('employee', 'Employé'), ('partner', 'partner')])
    user_associe_id = fields.Integer('employee associate id')
    
    @api.model
    def create(self, vals_list):
        name = vals_list.get('name')
        partner = self.env['res.partner'].search([]).mapped('name')
        for value in partner:
            if value.upper() == name.upper():
                raise ValidationError(
                    _("Ce nom existe déjà !"))

        return super(InheritResPartner, self).create(vals_list)


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    capital = fields.Float(string='Capital')
    rccm = fields.Char(string='RCCM')
