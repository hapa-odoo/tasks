# -*- coding: utf-8 -*-
{
    'name': "Sales Consolidation Report",

    'summary': """
        Sales Consolidation Report""",

    'description': """
        Sales Consolidation Report
    """,

    'author': "Odoo India",
    'website': "https://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_accountant', 'sale','point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'wizards/wizard_sales_consolidated_views.xml',
        'views/sales_consolidate_report_views.xml'
    ]
}
