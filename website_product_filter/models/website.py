# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        domain = super(Website,self).sale_product_domain()
        domain += [('ecommerce_identity_main_product','=',True)]
        return domain


class CountryState(models.Model):
    _inherit = 'res.country.state'

    name = fields.Char(string='State Name', required=True, translate=True,
               help='Administrative divisions of a country. E.g. Fed. State, Departement, Canton')