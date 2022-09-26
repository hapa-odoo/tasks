# -*- coding: utf-8 -*-
{
    'name': "pos_limit_discount",

    'summary': """
        Discount Limit in Pos
        """,

    'description': """
        If Discount applied on orderline(lines_discount+global_discount+discount_of_won_points) exceeds the
        limit_disount applied then try to reduce won points if possible otherwise
        raise an error popup.
    """,

    'author': "Odoo India",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['pos_loyalty', 'pos_discount'],

    # always loaded
    'data': [
        'views/pos_config_views.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/PaymentScreen/PaymentScreen.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
