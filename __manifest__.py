# -*- coding: utf-8 -*-

{
    'name': 'agentis module',
    'version': '15.0.1.0.0',
    'summary': 'gestion de la comptabilite agentis',
    'description': """gestion de la comptabilite agentis""",
    'author': 'progistack',
    'company': 'progistack',
    'maintainer': 'emmanuel.kissi@progistack.com',
    'depends': ['base', 'hr_expense', 'account_accountant', 'contacts', 'hr'],
    'website': 'https://www.progistack.com',
    'data': [
        'security/agentis_security.xml',
        'security/ir.model.access.csv',
        # 'views/mouvement_caise.xml',
        'wizard/export_view.xml',
        'wizard/ordre_mission_wizard.xml',
        'views/inherit_employee_partner.xml',
        'views/agentis_pga.xml',
        'views/sequence_numero_facture_dga.xml',
        'views/mouvement_bancaire_sequence.xml',
        'views/agentis_office_manager.xml',
        'views/agentis_chantier.xml',
        'views/office_manger_prive.xml',
        'views/agentis_dga_prive_view.xml',
        'views/inherit_account_view_move_form.xml',
        # 'views/charge_transfert_view.xml',
        'views/inherit_account_tax.xml',
        'views/dga_sequence.xml',
        'views/inherit_res_partner.xml',
        'views/analytic_analyse.xml',
        'views/inherit_analytique_account_view.xml',
        'views/contrat_view.xml',
        'views/attestation_agentis_view.xml',
        'views/certificat_de_travail_agentis.xml',
        'views/ordre_de_mission.xml',
        'views/agentis_caisse_consolide.xml',
        'views/history_delete.xml',
        'reports/report.xml',
        'reports/report_dga_template.xml',
        'reports/inherit_fourn_facture.xml',
        'reports/compte_analytique_report.xml',
        'reports/inherit_account_releve.xml',
        'reports/attestation_travail_report.xml',
        'reports/certificat_travail_report.xml',
        'reports/ordre_mission_report.xml',
        'reports/export_principale_pdf_template.xml',
        # 'reports/import_btn.xml',
        'wizard/inherit_account_register_payment.xml',
        # 'views/agentis_consolide.xml',


    ],
    'assets': {
        'web.assets_backend': [
            "/agentis/static/src/js/office_manager_dashbord.js",
            "/agentis/static/src/js/dga_dashbord.js",
        ],

        'web.assets_qweb': [
            '/agentis/static/src/xml/office_manager_dashbord.xml',
            '/agentis/static/src/xml/dga_dashbord.xml',

                ]

    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
