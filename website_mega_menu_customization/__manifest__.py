# -*- coding: utf-8 -*-
{
    'name': "website_mega_menu_customization",

    'summary': """
        Making Mega Menu Collapsible
    """,

    'description': """
        Making Sub Menu collapsible for Appropriate Mobile View
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website'],

    # always loaded
    'data': [
        'views/template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
