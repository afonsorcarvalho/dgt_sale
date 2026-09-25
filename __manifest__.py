# -*- coding: utf-8 -*-
{
    'name': "Sales Report Diagnostica",
	'version': '1.1',
    'sequence': 200,
    'category': 'Sales',
    'summary': 'Novo report de vendas para diagnostica',

    'summary': """
        Novo report de vendas para diagnostica
        """,

    'description': """
        Novo report de vendas para diagnostica
    """,

    'author': "Engº Afonso Carvalho",
    'website': "http://www.diagnostica-ma.com.br",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
   
    # any module necessary for this one to work correctly
    'depends': [
        'br_sale',
        'sale_management',
    ],

    # always loaded
    'data': [
        'security/dgt_sale_security.xml',
        'security/ir.model.access.csv',
        'wizard/copy_spec_wizard_views.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
        'reports/report_sales_assinatura_template.xml',
        'reports/report_sales_client_template.xml',
        'reports/dgt_sale_report.xml',
        'reports/dgt_sale_report_template.xml',
        'reports/dgt_proposal_report.xml',
        'reports/proposal/layout.xml',
        'reports/proposal/cover.xml',
        'reports/proposal/letter_summary.xml',
        'reports/proposal/sheets.xml',
        'reports/proposal/closing.xml',
        'reports/proposal/proposal_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
	'installable': True,
    'auto_install': False,
    'application': False,
}
