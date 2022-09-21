# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    limit_discount = fields.Boolean(string='Limit Discount')
    limit_discount_pc = fields.Float(string='Limit Discount  (%)', default=0.0, digits='Discount')
    product_to_skip_ids = fields.Many2many(string='Products to Skip', comodel_name='product.product', help='Product to skip at the time of distribution of global discount on each line')
    