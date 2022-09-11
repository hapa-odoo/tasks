# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class ResCountry(models.Model):
    _inherit = 'res.country'

    default_zip_code = fields.Char(string="Default Zip Code")
