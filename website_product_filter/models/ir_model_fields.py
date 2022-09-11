# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class IrModelField(models.Model):
    _inherit = 'ir.model.fields'

    # Remove the model name from the name
    def name_get(self):
        if not self._context.get('from_product_size_guide_category'):
            return super(IrModelField, self).name_get()
        return [(record.id, record.field_description) for record in self]