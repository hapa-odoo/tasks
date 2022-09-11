# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

USER_GENDER = [('male', 'Male'), ('female', 'Female')]
SIZE_CATEGORY = [('regular_fit', 'Regular Fit'), ('slim_flit', 'Slim Fit'), ('normal_flit', 'Normal Fit')]

class ProductColor(models.Model):
    _name = 'product.color'
    _description = 'Product Colors'

    name = fields.Char("Name")
    color = fields.Char(string='Color Index', help='Color to visulaize on Website')
    is_image = fields.Boolean(string="Image (?)")
    image = fields.Image(string="Image", help='Image to visulaize on Website')


class ProductSize(models.Model):
    _name = 'product.size'
    _description = 'Product Sizes'

    name = fields.Char("Name")
    sequence = fields.Integer("Sequence", help="Sequence in which the size will be displayed in website product view.")


class ProductIdentityGroup(models.Model):
    _name = 'ecommerce.identity.group'
    _description = 'Product Identity Group'

    name= fields.Char("Identity Name")
    image_count = fields.Integer(compute='_compute_image_count', string='Number of Images')
    product_image_ids = fields.One2many('product.image', 'ecommerce_identity_group_id', string='Product Images')

    @api.depends('product_image_ids')
    def _compute_image_count(self):
        for record in self:
            record.image_count = len(record.product_image_ids)

    def action_image_view(self):
        action = self.env["ir.actions.actions"].sudo()._for_xml_id('website_product_filter.action_product_upload_image_list')
        product_image = self.env['product.image'].sudo().search([('ecommerce_identity_group_id', '=', self.id)])
        action.update({
            'domain': [('ecommerce_identity_group_id', '=', self.id)],
            'context': {
                'default_ecommerce_identity_group_id': self.id,
            }
        })
        return action


class ProductSizeGuideCategory(models.Model):
    _name = 'product.size.guide.category'
    _description = 'Category of Product Size Guide'
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'sequence'

    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Name', index=True, required=True, translate=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True, translate=True)
    parent_id = fields.Many2one('product.size.guide.category', string='Parent Category', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('product.size.guide.category', 'parent_id', string='Child Categories')
    ref_image = fields.Image(string="Reference GIF/Image")
    child_description = fields.Html("Description", translate=True)
    find_your_size_description = fields.Html("Find your size", translate=True)

    product_size_footwear_ids = fields.One2many('product.size.guide', 'product_size_guide_categ_id', string='Footwear Records', copy=True, auto_join=True)
    product_size_clothing_ids = fields.One2many('product.size.guide.clothing', 'product_size_guide_categ_id', string='Clothing Records', copy=True, auto_join=True)
    show_footwear_field_ids = fields.Many2many('sequence.footwear', 'show_footwear_rel', 'name', 'footwear_id',  string="Will Show Footwear columns")
    show_clothing_field_ids = fields.Many2many('sequence.clothing', 'show_clothing_rel', 'name', 'clothing_id', string="Will Show Clothing columns")

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]


class ProductSizeGuide(models.Model):
    _name = 'product.size.guide'
    _description = 'Product Size Guide Footwear'
    _rec_name = 'foot_length'

    foot_length = fields.Float(string='Foot Length')
    eu_size = fields.Float(string='EU Size')
    us_size = fields.Float(string='US Size')
    uk_size = fields.Float(string='UK Size')
    product_size_guide_categ_id = fields.Many2one('product.size.guide.category', string='Product Size Guide Category',
                                                  index=True, ondelete='cascade') #o2m


class SequenceProductSizeGuide(models.Model):
    _name = 'sequence.footwear'
    _description = 'Set Footwear fields sequence Product Size Guide'
    _order = "sequence"

    sequence = fields.Integer(string='Sequence', copy=0, required=1, default=10)
    footwear_field_id = fields.Many2one('ir.model.fields', string='Footwear Fields', copy=0, required=1,
                                        domain=[('model', '=', 'product.size.guide')], ondelete='cascade')
    name = fields.Char(related='footwear_field_id.name', string='Name', readonly=1, copy=0)
    field_description = fields.Char(related='footwear_field_id.field_description', string='Field Description',
                                    readonly=1, copy=0)

    _sql_constraints = [
        ('footwear_field_id_uniq', 'unique (footwear_field_id)', "Field already exists !"),
    ]

    # Remove the model name from the name
    def name_get(self):
        if not self._context.get('from_product_size_guide_category'):
            return super(SequenceProductSizeGuide, self).name_get()
        return [(record.id, record.field_description) for record in self]


class ProductSizeGuideClothing(models.Model):
    _name = 'product.size.guide.clothing'
    _description = 'Product Size Guide: Clothing'
    _rec_name = 'chest'

    user_gender = fields.Selection(USER_GENDER, string='Gender', default='male')
    size_category = fields.Selection(SIZE_CATEGORY, string='Size Category', default='regular_fit')
    age = fields.Char(string='Age')

    chest = fields.Char(string='CHEST (cm)')
    waist = fields.Char(string='WAIST (cm)')
    hips = fields.Char(string='HIPS (cm)')
    it_size = fields.Char(string='IT SIZE')
    de_size = fields.Char(string='DE SIZE')
    fr_size = fields.Char(string='FR SIZE')
    us_size = fields.Char(string='US SIZE')
    uk_size = fields.Char(string='UK SIZE')
    normal_size = fields.Char(string='SIZE')

    neck = fields.Char(string='Neck (cm)')
    stride = fields.Char(string='Stride (cm)')
    bust = fields.Char(string='Bust (cm)')
    shoulder = fields.Char(string='Shoulder (cm)')
    cuff_width = fields.Char(string='Cuff (cm)')
    total_back_length = fields.Char(string='Total length - back')
    total_length_of_69arm = fields.Char(string='Total length - back (at 69 arm length)')
    total_length_of_72arm = fields.Char(string='Total length - back (at 72 arm length)')
    sleeve_length = fields.Char(string='Sleeve length')
    collar_size = fields.Char(string='Collar size')

    height = fields.Char(string='Height')
    leg_length = fields.Char(string='Leg Length')

    length = fields.Char(string='Length')
    arm_shoulder = fields.Char(string='ARM LENGTH FROM SHOULDER')
    arm_neck = fields.Char(string='ARM LENGTH FROM NECK')

    product_size_guide_categ_id = fields.Many2one('product.size.guide.category', string='Product Size Guide Category',
                                                  index=True, ondelete='cascade') #o2m


class SequenceProductSizeGuideClothing(models.Model):
    _name = 'sequence.clothing'
    _description = 'Set Clothing fields sequence Product Size Guide'
    _order = "sequence"

    sequence = fields.Integer(string='Sequence', copy=0, required=1, default=10)
    clothing_field_id = fields.Many2one('ir.model.fields', string='Clothing Fields', copy=0, ondelete='cascade',
                                        domain=[('model', '=', 'product.size.guide.clothing')], required=1)
    name = fields.Char(related='clothing_field_id.name', string='Name', readonly=1, copy=0)
    field_description = fields.Char(related='clothing_field_id.field_description', string='Field Description',
                                    readonly=1, copy=0)

    _sql_constraints = [
        ('clothing_field_id_uniq', 'unique (clothing_field_id)', "Field already exists !"),
    ]

    # Remove the model name from the name
    def name_get(self):
        if not self._context.get('from_product_size_guide_category'):
            return super(SequenceProductSizeGuideClothing, self).name_get()
        return [(record.id, record.field_description) for record in self]

