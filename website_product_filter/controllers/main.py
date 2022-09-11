# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.models import ir_http


class CustomWebsiteSale(WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):
        res = super(CustomWebsiteSale, self)._prepare_product_values(product, category, search, **kwargs)
        if product._has_identity_products():
            res['color'] = res['product'].color_id
            res['size'] = res['product'].size_id
            main_identity_product = request.env['product.template'].sudo().search([
                ('ecommerce_identity_group_id','=',res['product'].ecommerce_identity_group_id.id),
                ('color_id','=',False),
                ('size_id','=',False)
            ], limit=1)
            res['product'] = main_identity_product
            res['main_object'] = main_identity_product
        return res

    def _get_pricelist(self, pricelist_id, pricelist_fallback=False):
        return request.env['product.pricelist'].sudo().browse(int(pricelist_id or 0))

    def _get_product_size_footwear_ids(self, product_size_footwear_ids, selectedFields=False):
        footwearRecords = request.env['product.size.guide'].sudo().search_read(
                domain=[('id', 'in', product_size_footwear_ids)],
                fields=selectedFields.mapped('name') if selectedFields else False,
                order='id asc')
        return footwearRecords

    def _get_product_size_clothing_ids(self, product_size_clothing_ids, selectedFields=False):
        clothingRecords = request.env['product.size.guide.clothing'].sudo().search_read(
            domain=[('id', 'in', product_size_clothing_ids)],
            fields=selectedFields.mapped('name') if selectedFields else False,
            order='id asc')
        return clothingRecords

    @http.route(['/website_sale/get_product_identity_info'], type='json', auth="public", methods=['POST'], website=True)
    def get_product_identity_info(self, product_template_id, product_id, add_qty, pricelist_id, size_id, color_id, **kw):
        combination = request.env['product.template.attribute.value'].sudo()
        pricelist = self._get_pricelist(pricelist_id)
        ProductTemplate = request.env['product.template'].sudo()
        if 'context' in kw:
            ProductTemplate = request.env['product.template'].sudo().with_context(**kw.get('context'))
        product_template = ProductTemplate.browse(int(product_template_id))
        if size_id or color_id:
            product = request.env['product.product'].sudo().search([
                ('ecommerce_identity_group_id','=',product_template.ecommerce_identity_group_id.id),
                ('color_id','=',int(color_id or 0)),
            ], limit=1)
            all_sizes = product_template._get_identity_group_sizes()
            product_for_sizes = request.env['product.product'].sudo().search([
                ('ecommerce_identity_group_id','=',product_template.ecommerce_identity_group_id.id),
                ('color_id','=',int(color_id or 0)),
            ])
            available_sizes = product_for_sizes.mapped('size_id')
            remaining_sizes = all_sizes - available_sizes
            if size_id:
                product = request.env['product.product'].sudo().search([
                    ('ecommerce_identity_group_id','=',product_template.ecommerce_identity_group_id.id),
                    ('color_id','=',int(color_id or 0)),
                    ('size_id','=',int(size_id))
                ], limit=1)
            res = product_template._get_combination_info(combination, int(product.id or 0), int(add_qty or 1), pricelist)
            website = ir_http.get_request_website()
            products_for_qty = []
            if website:
                order = website.sale_get_order()

                for tmpl in product_for_sizes.mapped('product_tmpl_id'):
                    products_for_qty_vals = {
                        'product_tmpl_id': tmpl.id,
                        'product_tmpl_name': tmpl.name,
                        'product_tmpl_qty_available': tmpl.with_context(warehouse=order.warehouse_id.id).qty_available,
                        'product_tmpl_color_id': tmpl.color_id.id,
                        'product_tmpl_color_name': tmpl.color_id.name,
                        'product_tmpl_size_id': tmpl.size_id.id,
                        'product_tmpl_size_name': tmpl.size_id.name,
                    }
                    products_for_qty.append(products_for_qty_vals)
            res['products_for_qty'] = products_for_qty
            if not product:
                res['is_combination_possible'] = False
            product_image_ids = request.env['product.image'].sudo().search([('ecommerce_identity_group_id','=',product_template.ecommerce_identity_group_id.id),
                ('color_id','=',int(color_id or 0))])
            if product:
                carousel_view = request.env['ir.ui.view'].sudo()._render_template('website_product_filter.product_image_grid',
                    values={
                        'product_image_ids': product_image_ids,
                    })
                res['carousel'] = carousel_view
                carousel_product_image_ids = request.env['ir.ui.view'].sudo()._render_template(
                    'website_product_filter.website_shop_product_filter_carousel',
                    values={'product_image_ids': product_image_ids})
                res['product_image_ids'] = carousel_product_image_ids
            res['remaining_sizes'] = remaining_sizes.ids
        return res

    @http.route(['/website_sale/get_size_guide_info'], type='json', auth="public", methods=['POST'])
    def get_size_guide_info(self, product_template_id, **kw):
        ProductTemplate = request.env['product.template'].sudo().browse(product_template_id)
        SizeGuideCategory = ProductTemplate.size_guide_category_id.read()
        if ProductTemplate.size_guide_category_id.show_footwear_field_ids:
            selectedFields = ProductTemplate.size_guide_category_id.show_footwear_field_ids
            for SGC in SizeGuideCategory:
                if 'product_size_footwear_ids' in SGC:
                    SGC['product_size_footwear_ids'] = self._get_product_size_footwear_ids(SGC['product_size_footwear_ids'], selectedFields)
            dictSelectedFields = dict(zip(selectedFields.mapped('name'), selectedFields.mapped('field_description')))
            return SizeGuideCategory, dictSelectedFields
        elif ProductTemplate.size_guide_category_id.show_clothing_field_ids:
            selectedFields = ProductTemplate.size_guide_category_id.show_clothing_field_ids
            for SGC in SizeGuideCategory:
                if 'product_size_clothing_ids' in SGC:
                    SGC['product_size_clothing_ids'] = self._get_product_size_clothing_ids(SGC['product_size_clothing_ids'], selectedFields)
            dictSelectedFields = dict(zip(selectedFields.mapped('name'), selectedFields.mapped('field_description')))
            return SizeGuideCategory, dictSelectedFields
        else:
            for SGC in SizeGuideCategory:
                if 'product_size_footwear_ids' in SGC and len(SGC['product_size_footwear_ids']) > 0:
                    SGC['product_size_footwear_ids'] = self._get_product_size_footwear_ids(SGC['product_size_footwear_ids'])
                elif 'product_size_clothing_ids' in SGC and len(SGC['product_size_clothing_ids']) > 0:
                    SGC['product_size_clothing_ids'] = self._get_product_size_clothing_ids(SGC['product_size_clothing_ids'])
                else:
                    raise UserError(_('Size guides are not configured. Please contact to administrator'))
            return SizeGuideCategory


    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super(CustomWebsiteSale, self).checkout_form_validate(mode, all_form_values, data)
        country_code = request.env['res.country'].sudo().browse(data.get('country_id')).code
        mobile_number = data.get('phone')
        if country_code == 'IL' or country_code == 'PS':
            if not mobile_number.isdigit():
                error["phone"] = 'error'
                error_message.append(_("Please Enter only digits as a Mobile Number"))
            if not mobile_number.startswith('97'):
                error["phone"] = 'error'
                error_message.append(_("Kindly check your Mobile Number, It should start with '97' "))
            if len(mobile_number) != 12:
                error["phone"] = 'error'
                error_message.append(_("Your Mobile Number should be 12 digits"))

        return error, error_message

    @http.route(['/shop/default_zip_infos/<model("res.country"):country>'], type='json', auth="public", methods=['POST'], website=True)
    def default_zip(self, country, **kw):
        return dict(
            default_zip_code=country.default_zip_code,
        )
