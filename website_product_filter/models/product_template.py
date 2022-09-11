# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    color_id = fields.Many2one("product.color", string="Color")
    size_id = fields.Many2one("product.size", string="Size")
    ecommerce_identity_group_id = fields.Many2one("ecommerce.identity.group", string="eCommerce Identity Group", copy=False)
    ecommerce_name = fields.Char("eCommerce Name", translate=True)
    ecommerce_identity_main_product = fields.Boolean("Identity Product (?)", default=False, copy=False)
    size_guide_category_id = fields.Many2one('product.size.guide.category', string='Size guide Category')
    tilde_image = fields.Image(string="Tilde Image", copy=False,)
    bestseller_rank = fields.Integer(string="Best Seller Rank")

    @api.constrains('ecommerce_identity_main_product', 'ecommerce_identity_group_id')
    def _check_unique_identity_group_leader(self):
        if self.search_count([
            ('ecommerce_identity_main_product', '=', True),
            ('ecommerce_identity_group_id','=',self.ecommerce_identity_group_id.id)
        ]) > 1:
            raise UserError(_('Only One Product is allowed to be the group leader per Identity Group.'))

    def _has_identity_products(self):
        """Return whether this `product.template` has at least one Identity group Child
        Product.

        :return: True if at least one identity child product, False otherwise
        :rtype: bool
        """
        self.ensure_one()
        identity_product_id = self.env['product.template'].sudo().search_count([
            ('ecommerce_identity_group_id','=',self.ecommerce_identity_group_id.id),
            ('color_id','!=',False),
            ('size_id','!=',False)
        ])
        return True if identity_product_id >= 1 else False

    def _get_identity_group_sizes(self):
        """Return the list of the available product sizes related to the current Idenitity
        Group.

        :return: Recordset for all the available size related to the current product identity
        group
        :rtype: Recordset
        """
        self.ensure_one()
        identity_product_id = self.env['product.template'].sudo().search([
            ('ecommerce_identity_group_id','=',self.ecommerce_identity_group_id.id),
        ])
        product_size_ids = identity_product_id.mapped('size_id').sorted(lambda l: l.sequence)
        return product_size_ids

    def _get_identity_group_colors(self):
        """Return the list of the available product colors related to the current Idenitity
        Group.

        :return: Recordset for all the available size related to the current product identity
        group
        :rtype: Recordset
        """
        self.ensure_one()
        identity_product_id = self.env['product.template'].sudo().search([
            ('ecommerce_identity_group_id','=',self.ecommerce_identity_group_id.id),
        ])
        product_color_ids = identity_product_id.mapped('color_id')
        return product_color_ids

    @api.onchange('size_guide_category_id')
    def _onchange_size_guide_category_id(self):
        if self.size_guide_category_id:
            if not self.size_guide_category_id.show_footwear_field_ids and not self.size_guide_category_id.show_clothing_field_ids:
                #self.size_guide_category_id = False
                raise UserError( _(f"Please add the columns visibility for {self.size_guide_category_id.display_name}"))

class ProductImage(models.Model):
    _inherit = 'product.image'

    sequence = fields.Integer(string='Sequence', default=10)
    color_id = fields.Many2one("product.color", string="Color")
    ecommerce_identity_group_id = fields.Many2one("ecommerce.identity.group", string="eCommerce Identity Group", copy=False)
