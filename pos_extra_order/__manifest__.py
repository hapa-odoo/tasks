# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "pos_extra_order",
    'summary': """
        This module allow the user to create the extra order in POS even when the order is confirmed.
       """,
    'description': """   
    """,
    'author': "falak-solution",
    'category': 'Point of Sale',
    'version': '1.0',
    'depends': ['point_of_sale','web','pos_debt','pos_total_item','pos_multicurrency','pos_order_barcode'],
    'data': [
        'security/ir.model.access.csv',

        'views/pos_config_view.xml',
        'views/pos_extra_order_view.xml',
        'views/assets_view.xml',
        'views/extra_ordernote_report.xml',
        'views/extra_order_report.xml',
        'data/data.xml'
    ],
    'qweb': [
        # 'static/src/xml/ExtraOrderReceiptPrint.xml',
        'static/src/xml/ReceiptScreen.xml',
        'static/src/xml/ExtraOrderReceiptScreen.xml',
        'static/src/xml/ExtraOrderTicket.xml',
        'static/src/xml/ExtraOrderTicketScreen.xml',
        'static/src/xml/ChromeExtraOrder.xml',
        'static/src/xml/ExtraOrderNoteScreen.xml',
        'static/src/xml/ExtraOrderNoteReceipt.xml',
        'static/src/xml/ExtraOrderReceipt.xml',
    ],
}
