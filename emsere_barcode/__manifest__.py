# -*- coding: utf-8 -*-
{
    'name': "emsere_barcode",

    'summary': """
        Extend functionality of function filter_on_product for LOT""",

    'description': """
        when barcode is being scanned it can be:
            a barcode of a product or
            a lot name of lot of existing stock.move,line in picking
    """,

    'author': "Odoo India",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': '',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock_barcode'],

    # always loaded
    'data': [
        'views/stock_picking_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
