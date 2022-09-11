# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    allow_extra_order =  fields.Boolean('Allow Extra Order')
    extra_order_sequence_id = fields.Many2one('ir.sequence')

    @api.model
    def create(self, values):
        IrSequence = self.env['ir.sequence'].sudo()
        val = {
            'name': _('POS Extra Order %s', values['name']),
            'padding': 4,
            'prefix': "Extra/%s/" % values['name'],
            'code': "pos.extra.order",
            'company_id': values.get('company_id', False),
        }
        values['extra_order_sequence_id'] = IrSequence.create(val).id
        pos_config = super(PosConfig, self).create(values)
        return pos_config
