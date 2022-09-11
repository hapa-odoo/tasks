# -*- coding: utf-8 -*-


from odoo import tools
from odoo import models, fields, api



class ReportIextraorderpdfCustom(models.AbstractModel):
    _name = 'report.pos_extra_order.extra_order_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print("111111")
        report = self.env['ir.actions.report']._get_report_from_name('pos_extra_order.report_extraorderpdf_custom')
        if data and data.get('form') and data.get('form').get('user_ids'):
            docs = self.env['pos.extra.order'].browse(data['form']['user_ids'])
        return {
                'doc_model': report.model,
                'docs': self.env['pos.extra.order'].browse(data.get('ids')),
                'data': data,
          
                }
        
        
class ReportInoteextraorderpdfCustom(models.AbstractModel):
    _name = 'report.pos_extra_order.extra_noteorder_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print("111111")
        report = self.env['ir.actions.report']._get_report_from_name('pos_extra_order.report_noteextraorderpdf_custom')
        if data and data.get('form') and data.get('form').get('user_ids'):
            docs = self.env['pos.extra.order'].browse(data['form']['user_ids'])
        return {
                'doc_model': report.model,
                'docs': self.env['pos.extra.order'].browse(data.get('ids')),
                'data': data,
          
                }