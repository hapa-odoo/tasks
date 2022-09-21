# -*- coding: utf-8 -*-

import base64
import calendar
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from werkzeug.urls import url_encode
from odoo.osv import expression
from odoo.addons.web.controllers.main import ExcelExport

DOCUMENT_TYPE = {
    'out_invoice': 'Customer Invoice',
    'out_refund': 'Customer Credit Note',
    'pos_order': 'POS Order',
}
GST_TREATMENT = {
    'regular' : 'Registered Business - Regular' ,
    'composition' : 'Registered Business - Composition' ,
    'unregistered' : 'Unregistered Business' ,
    'consumer' : 'Consumer' ,
    'overseas' : 'Overseas' ,
    'special_economic_zone' : 'Special Economic Zone' ,
    'deemed_export' : 'Deemed Export',
}


class SalesConsolidatedReportWizard(models.TransientModel):
    _name = 'sales.consolidated.report.wizard'
    _description = 'Print Sales Consolidated Report'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    product_ids = fields.Many2many('product.product', string='Products')
    partner_tag_ids = fields.Many2many('res.partner.category', string='Partners to Ignore')
    report_type = fields.Selection([('summary','Summary'), ('detailed', 'Detailed'), ('hsn', 'HSN')], default='summary')
    company_ids = fields.Many2many('res.company', string="Companies", help="Select the companies for filtering the result, if not selected the record will be of current selected company.")
    is_sop = fields.Boolean("SOP", help="Sales Order")
    is_pos = fields.Boolean("POS", help="Point Of Sales")
    is_bt = fields.Boolean("Branch Transfer", help="Branch Transfer")
    is_employee_wallet = fields.Boolean("Employee Wallet", help="Employee Wallet")

    report_data = fields.Binary('Report file', readonly=True, attachment=False)
    report_filename = fields.Char(string='Filename', readonly=True)
    mimetype = fields.Char(string='Mimetype', readonly=True)

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        today = fields.Datetime.now()
        first_day, last_day = map(int,calendar.monthrange(today.year, today.month))
        # vals['start_date'] = datetime(today.year,today.month,first_day).date()
        vals['end_date'] = datetime(today.year,today.month,last_day).date()
        return vals
    
    def _get_domain(self):
        domain = [
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date)
        ]
        if self.company_ids:
            domain += [('company_id','in',self.company_ids.ids)]
        else:
            domain += [('company_id','in', self.env.company.ids)]
        
        if self.product_ids:
            domain = expression.AND([domain,[('product_id', 'in', self.product_ids.ids)]])

        # Ignore the free product lines
        free_line_ids = self.env['account.move.line'].sudo().search(domain).mapped('free_product_line_id.id')
        domain += [('move_line_id','not in', free_line_ids)]

        reference_type = []
        if self.is_sop:
            reference_type += ['SOP']
        if self.is_pos:
            reference_type += ['POS']
        if self.is_bt:
            reference_type += ['BT']
        if self.is_employee_wallet:
            reference_type += ['EMPLOYEE']

        if reference_type:
            domain += [('reference','in',reference_type)]
        else:
            domain += [('reference','in',['SOP','POS','BT', 'EMPLOYEE'])]

        # Ignore the Partner with specific Tags.
        if self.partner_tag_ids:
            domain += [('partner_id.category_id','not in', self.partner_tag_ids.ids)]

        return domain

    def action_print(self):
        if self.start_date > self.end_date:
            raise UserError(_("Start Date must be less than End Date."))

        date_date_from = fields.Date.from_string(self.start_date)
        date_date_to = fields.Date.from_string(self.end_date)
        date_diff_days = (date_date_to - date_date_from).days

        if date_diff_days > 31 and not self.product_ids and not self.report_type == "summary":
            raise UserError(_("You can select data for a range of 31 days."))

        SaleReportExtend = self.env['sale.consolidated.report']

        domain = self._get_domain()

        fields_get = SaleReportExtend.fields_get()
        fields_list = list()

        if self.report_type == 'summary':
            summary_fields = ['name', 'partner_id', 'state_id', 'vat_partner', 'l10n_in_gst_treatment', 'doc_date', 'company_id','invoice_type', 'price_subtotal', 'tax_value', 'price_total']
            for field in summary_fields:
                fields_list.append(fields_get[field].get('string'))
            grouped_data = SaleReportExtend.sudo().read_group(domain, fields=['doc_id','name','reference','partner_id', 'vat_partner', 'l10n_in_gst_treatment', 'state_id', 'invoice_type', 'doc_date', 'company_id', 'price_subtotal:sum',
        'tax_value:sum'], groupby=['doc_id','name','doc_date','reference', 'invoice_type', 'partner_id','state_id', 'vat_partner', 'l10n_in_gst_treatment', 'company_id'], orderby="date", lazy=False)
            records = list([
                dict([
                ("name", record['name']),
                ("partner_id", str(record['partner_id'][1] if record['partner_id'] else "")),
                ("state_id", str(record['state_id'][1] if record['state_id'] else "")),
                ('vat_partner', record['vat_partner']),
                ('l10n_in_gst_treatment', record['l10n_in_gst_treatment']),
                ("date", record['doc_date']),
                ("company_id", str(record['company_id'][1])),
                ("invoice_type", record['invoice_type']),
                ("price_subtotal", record['price_subtotal']),
                ("tax_value", record['tax_value']),
                ("price_total", (record['price_subtotal'] + record['tax_value'])),
            ]) for record in grouped_data])
        if self.report_type == "hsn":
            hsn_fields = ['reference', 'invoice_type', 'branch_state_id', 'company_id', 'vat_partner', 'l10n_in_gst_treatment', 'partner_id', 'name','date', 'inv_value', 'l10n_in_hsn_code', 'total_qty', 'price_subtotal', 'tax_value', 
            'price_total', 'cgst_amount', 'sgst_amount', 'igst_amount', 'cess_amount', 'state_id', 'state_code']
            for field in hsn_fields:
                fields_list.append(fields_get[field].get('string'))
            records = SaleReportExtend.sudo().search_read(domain, fields=hsn_fields, order="date asc")
        if self.report_type == 'detailed':
            detailed_fields = ['name', 'date', 'partner_id', 'state_id', 'vat_partner', 'l10n_in_gst_treatment', 'product_name', 'product_code', 'categ_id', 'l10n_in_hsn_code', 'total_qty', 'bonus_qty', 'discount_per',
            'price_subtotal', 'price_total', 'tax_rate', 'tax_value', 'cgst_amount', 'sgst_amount', 'igst_amount', 'cess_amount',
            'price_unit', 'reference', 'invoice_type', 'company_id', 'month', 'year']
            for field in detailed_fields:
                fields_list.append(fields_get[field].get('string'))
            records = SaleReportExtend.sudo().search_read(domain, fields=detailed_fields, order="date asc")


        if len(records) > 65535:
            raise UserError(
                _("There are too many rows (limit: 65535) to export as Excel 97-2003 (.xls) format. Consider splitting the export."))

        data_list = []
        for rec in records:
            temp_list = []
            if self.report_type == "hsn" or self.report_type == "summary" or self.report_type == "detailed":
                if 'id' in rec:
                    rec.pop('id')
                for key, value in rec.items():
                    if isinstance(value, tuple):
                        rec[key] = value[1]
                    if isinstance(value, bool) and not value:
                        rec[key] = ''
                    if key == "invoice_type" and value in DOCUMENT_TYPE:
                        rec[key] = DOCUMENT_TYPE[value]
                    if key == "l10n_in_gst_treatment" and value in GST_TREATMENT:
                        rec[key] = GST_TREATMENT[value]
                temp_list = list(rec.values())
            data_list.append(temp_list)
            del temp_list
        try:
            obj = ExcelExport()
            data = obj.from_data(fields_list, data_list)
        except Exception as e:
            raise UserError(_(e))

        self.write({
                'report_data': base64.b64encode(data),
                'report_filename': 'Consolidated Sales Analysis Report.xls',
                'mimetype': 'application/vnd.ms-excel',
            })

        return {
            'type': 'ir.actions.act_url',
            'url':  '/web/content/?' + url_encode({
                        'model': self._name,
                        'id': self.id,
                        'filename_field': 'report_filename',
                        'field': 'report_data',
                        'download': 'true'
                    }),
            'target': 'self'
        }

    def open_report_data(self):
        if self.report_type == 'summary':
            tree_view_id = self.env.ref('sales_consolidated_report.sale_consolidated_report_summary_view_tree').id
        if self.report_type == 'detailed':
            tree_view_id = self.env.ref('sales_consolidated_report.sale_consolidated_report_detailed_view_tree').id
        if self.report_type == "hsn":
            tree_view_id = self.env.ref('sales_consolidated_report.sale_consolidated_report_hsn_view_tree').id
        pivot_view_id = self.env.ref('sales_consolidated_report.sale_consolidated_report_view_pivot').id
        search_view_id = self.env.ref('sales_consolidated_report.sale_consolidated_report_view_search').id
        domain = self._get_domain()
        if self.product_ids:
            domain = expression.AND([domain,[('product_id', 'in', self.product_ids.ids)]])
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (pivot_view_id, 'pivot'), (search_view_id, 'search')],
            'view_mode': 'tree,pivot',
            'name': _('Consolidated Sales Report'),
            'res_model': 'sale.consolidated.report',
            'domain': domain,
            'context': {'group_by':['date','reference']},
        }
        if self.report_type == "summary":
            action['context'] = {'group_by':['date','name']}
        return action
