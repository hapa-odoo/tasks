# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    lot_id = fields.Many2one('stock.production.lot', 'Lot', related='move_line_ids_without_package.lot_id', readonly=True)

    @api.model
    def filter_on_product(self, barcode):
        res = super(StockPicking, self).filter_on_product(barcode)
        lot = self.env['stock.production.lot'].search_read([('name', '=' , barcode)], ['id'], limit=1)
        if lot:
            lot_id = lot[0]['id']
            picking_type = self.env['stock.picking.type'].search_read(
                [('id', '=', self.env.context.get('active_id'))],
                ['name'],
            )[0]
            if not self.search_count([
                ('lot_id', '=', lot_id),
                ('picking_type_id', '=', picking_type['id']),
                ('state', 'not in', ['cancel', 'done', 'draft']),
            ]):
                return {'warning': {
                    'title': _("No %s ready for this product", picking_type['name']),
                }}
            action = self.env['ir.actions.actions']._for_xml_id('stock_barcode.stock_picking_action_kanban')
            action['context'] = dict(self.env.context)
            action['context']['search_default_lot_id'] = lot_id
            return {'action': action}
        return res
