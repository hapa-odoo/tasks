# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
from itertools import groupby
from odoo import tools
from odoo import api, fields, models


class SaleConsolidatedReport(models.Model):
    _name = "sale.consolidated.report"
    _description = "Consolidated Sales Analysis Report"
    _auto = False
    _order = 'date desc'

    name = fields.Char('# Inv. No', readonly=True)
    doc_id = fields.Integer("Document Id")
    doc_date = fields.Char("Document Date")
    date = fields.Date("Invoice Date")
    reference = fields.Char("Reference")
    invoice_status = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid'), # Considring the POS Transaction.
        ('done', 'Posted'), # Considring the POS Transaction.
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], string='Invoice Status', readonly=True)
    invoice_type = fields.Selection(selection=[
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Credit Note'),
        ('pos_order', 'POS Order'),
    ], string='Invoice Type', readonly=True)
    month = fields.Char("Month")
    year = fields.Char("Year")

    # Partner Details
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    vat_partner = fields.Char('GST No. Partner', readonly=True)
    state_id = fields.Many2one('res.country.state', 'Partner State', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', readonly=True)
    state_code = fields.Char(related="state_id.code", string='Partner State Code', readonly=True)
    l10n_in_gst_treatment = fields.Selection([
            ('regular', 'Registered Business - Regular'),
            ('composition', 'Registered Business - Composition'),
            ('unregistered', 'Unregistered Business'),
            ('consumer', 'Consumer'),
            ('overseas', 'Overseas'),
            ('special_economic_zone', 'Special Economic Zone'),
            ('deemed_export', 'Deemed Export')
        ], string="GST Treatment", readonly=True)

    # Invoice/PoS Line Summmary
    price_unit = fields.Float('Unit Price', readonly=True)
    price_subtotal  = fields.Monetary('Taxable Amount', readonly=True)
    price_total = fields.Monetary('Total Amount', compute="_compute_tax_details", compute_sudo=True)
    tax_value = fields.Monetary('Tax Amount', readonly=True)
    inv_value = fields.Monetary('Invoice Total', readonly=True)
    move_line_id = fields.Many2one('account.move.line', 'Invoice Line', readonly=True)
    pos_line_id = fields.Many2one('pos.order.line', 'Pos Order Line', readonly=True)
    discount_per = fields.Float("Discount (%)")

    # Product Summary
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    product_name = fields.Char(compute="_compute_product_name_without_code")
    product_code = fields.Char(related='product_id.code', string="Product Code")
    default_code = fields.Char('Product Reference', readonly=True)
    total_qty = fields.Float("Sales Qty", readonly=True)
    bonus_qty = fields.Float("Bonus Qty", readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    l10n_in_hsn_code = fields.Char('HSN Code', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', 'Product Uom', readonly=True)

    # Tax Summary
    invoice_tax_ids = fields.Many2many('account.tax', 'Taxes', related='move_line_id.tax_ids')
    igst_amount = fields.Float("IGST Amount", compute="_compute_tax_details", compute_sudo=True)
    cgst_amount = fields.Float("CGST Amount", compute="_compute_tax_details", compute_sudo=True)
    sgst_amount = fields.Float("SGST Amount", compute="_compute_tax_details", compute_sudo=True)
    cess_amount = fields.Float("CESS Amount", compute="_compute_tax_details", compute_sudo=True)
    sale_tax_ids = fields.Many2many('account.tax', 'Taxes', related='move_line_id.tax_ids')
    pos_tax_ids = fields.Many2many('account.tax', 'Taxes', related='pos_line_id.tax_ids')
    tax_rate = fields.Char('Tax Rate', compute="_compute_tax_rate", compute_sudo=True)

    # Company Details
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    branch_state_id = fields.Many2one('res.country.state', related="company_id.state_id", string="Branch State", readonly=True)

    def _select_sale(self):
        select_ = """
            WITH currency_rate AS (%s)
            SELECT
                MIN(ml.id) AS id,
                MIN(am.id) AS doc_id,
                am.name AS name,
                ml.date::date AS date,
                to_char(ml.date::date, 'DD/MM/YYYY') AS doc_date,
                ml.partner_id AS partner_id,
                rp.vat AS vat_partner,
                rp.state_id AS state_id,
                rp.l10n_in_gst_treatment AS l10n_in_gst_treatment,
                ml.id AS move_line_id,
                NULL AS pos_line_id,
                ml.product_id AS product_id,
                product_t.name AS product_name,
                ml.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN am.move_type IN ('out_refund') THEN -1 ELSE 1 END)
                - COALESCE(bml.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN am.move_type IN ('out_refund') THEN -1 ELSE 1 END),0.0) AS total_qty,
				COALESCE(bml.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN am.move_type IN ('out_refund') THEN -1 ELSE 1 END),0.0)
                                                                            AS bonus_qty,
                -ml.balance * currency_table.rate + (COALESCE(-bml.balance, 0.0) * currency_table.rate) AS price_subtotal,
                product_t.default_code AS default_code,
                SUM(ml.price_unit / COALESCE(currency_table.rate, 1.0))::decimal(16,2) AS price_unit,
                CASE WHEN ml.partner_id in (%s) THEN 'BT' ELSE 'SOP' END AS reference,
                ml.company_id AS company_id,
                to_char(date_trunc('month', ml.date),'Month') AS month,
				to_char(date_trunc('year', ml.date),'YYYY') AS year,
                product_t.categ_id AS categ_id,
                product_t.l10n_in_hsn_code AS l10n_in_hsn_code,
                ml.product_uom_id AS product_uom_id,
                am.state AS invoice_status,
                am.move_type as invoice_type,
                ml.discount as discount_per,
                am.amount_total * currency_table.rate AS inv_value,
                ((ml.price_total - ml.price_subtotal) + (COALESCE(bml.price_total,0.0) - COALESCE(bml.price_subtotal,0.0))) AS tax_value,
                ml.currency_id AS currency_id
                """ % (self.env['res.currency']._select_companies_rates(),','.join(map(str,self.env['res.company'].search([]).mapped('partner_id.id'))))
        return select_

    @api.model
    def _from_sale(self):
        return """
            FROM account_move_line ml
        """
    
    @api.model
    def _join_sale(self):
        return """
            LEFT JOIN account_move_line bml ON ml.free_product_line_id = bml.id
            LEFT JOIN res_partner rp ON ml.partner_id = rp.id
            LEFT JOIN res_company company ON ml.company_id = company.id
            LEFT JOIN res_partner comp_partner ON company.partner_id = comp_partner.id
            LEFT JOIN product_product product ON product.id = ml.product_id
            LEFT JOIN product_template product_t ON product.product_tmpl_id = product_t.id
            LEFT JOIN uom_uom uom_line ON uom_line.id = ml.product_uom_id
            LEFT JOIN uom_uom uom_template ON uom_template.id = product_t.uom_id
            INNER JOIN account_move am ON am.id = ml.move_id
            JOIN {currency_table} ON currency_table.company_id = ml.company_id
            """.format(
                currency_table=self.env['res.currency']._get_query_currency_table({'multi_company': True, 'date': {'date_to': fields.Date.today()}}),
            )
            
    
    @api.model
    def _where_sale(self):
        return '''
            WHERE am.move_type IN ('out_invoice','out_refund')
                AND ml.account_id IS NOT NULL
                AND NOT ml.exclude_from_invoice_tab
                AND am.state = 'posted'
        '''
    
    @api.model
    def _group_by_sale(self):
        group_by_str = '''
            GROUP BY ml.id,
            bml.id,
            am.name,
            am.state,
            am.date,
            product_t.name,
            currency_table.rate,
            uom_line.factor,
            uom_template.factor,
            product_t.l10n_in_hsn_code,
            product_t.categ_id,
            product_t.default_code,
            rp.vat,
            rp.state_id,
            rp.l10n_in_gst_treatment,
            am.move_type,
            am.amount_total,
            am.amount_tax
        '''
        return group_by_str
    
    def _select_pos(self):
        select_ = """
            SELECT
                -MIN(l.id) AS id,
                -MIN(pos.id) AS doc_id,
                pos.name,
                pos.date_order::date AS date,
                to_char(pos.date_order::date, 'DD/MM/YYYY') AS doc_date,
                pos.partner_id AS partner_id,
                partner.vat AS vat_partner,
                partner.state_id AS state_id,
                partner.l10n_in_gst_treatment AS l10n_in_gst_treatment,
                NULL AS move_line_id,
                l.id AS pos_line_id,
                l.kit_product_id AS product_id,
                t.name AS product_name,
                l.kit_qty AS total_qty,
                0.0 AS bonus_qty,
                (l.price_subtotal) / MIN(CASE COALESCE(pos.currency_rate, 1) WHEN 0 THEN 1.0 ELSE pos.currency_rate END)::decimal(16,2) AS price_subtotal,
                t.default_code AS default_code,
                ((l.price_unit / CASE COALESCE(pos.currency_rate, 1) WHEN 0 THEN 1.0 ELSE pos.currency_rate END))::decimal(16,2) AS price_unit,
                CASE 
                    WHEN (SELECT
                        MIN(pm.id)
                    FROM
                        pos_payment AS payment
                    JOIN pos_payment_method pm ON (payment.payment_method_id = pm.id AND pm.is_wallet = 't')
                    WHERE
                        payment.pos_order_id = l.order_id
                    LIMIT 1) IS NOT NULL 
                THEN 
                    'EMPLOYEE'
                ELSE 'POS' END AS reference,
                pos.company_id AS company_id,
                to_char(date_trunc('month', pos.date_order),'Month') AS month,
				to_char(date_trunc('year', pos.date_order),'YYYY') AS year,
                t.categ_id AS categ_id,
                t.l10n_in_hsn_code AS l10n_in_hsn_code,
                t.uom_id AS product_uom_id,
                pos.state AS invoice_status,
                'pos_order' AS invoice_type,
                l.discount as discount_per,
                pos.amount_total * CASE COALESCE(pos.currency_rate, 1) WHEN 0 THEN 1.0 ELSE pos.currency_rate END AS inv_value,
                (SUM(l.price_subtotal_incl) / MIN(CASE COALESCE(pos.currency_rate, 1) WHEN 0 THEN 1.0 ELSE pos.currency_rate END) - 
                SUM(l.price_subtotal) / MIN(CASE COALESCE(pos.currency_rate, 1) WHEN 0 THEN 1.0 ELSE pos.currency_rate END))::decimal(16,2) AS tax_value,
                NULL AS currency_id
        """ 
        return select_

    def _from_pos(self):
        from_ = '''
        FROM
            pos_order_line l
                join pos_order pos on (l.order_id=pos.id)
                LEFT JOIN res_partner partner ON (pos.partner_id = partner.id OR pos.partner_id = NULL)
                LEFT JOIN product_product p on (p.id = l.kit_product_id)
                LEFT JOIN product_template t on (t.id = p.product_tmpl_id)
                LEFT JOIN uom_uom u ON (t.uom_id = u.id)
                LEFT JOIN pos_session session ON (pos.session_id = session.id)
                LEFT JOIN pos_config config ON (session.config_id = config.id)
                LEFT JOIN pos_payment ppay ON (pos.id = ppay.pos_order_id)
                LEFT JOIN pos_payment_method pm ON (ppay.payment_method_id = pm.id)
                LEFT JOIN product_pricelist pp on (pos.pricelist_id = pp.id)
        '''
        return from_
    
    def _group_by_pos(self):
        groupby_ = '''
        GROUP BY
            l.id,
            l.order_id,
            l.kit_product_id,
            t.name,
            pos.state,
            l.price_unit,
            l.kit_qty,
            t.uom_id,
            t.l10n_in_hsn_code,
            t.categ_id,
            t.default_code,
            pos.name,
            pos.date_order,
            pos.partner_id,
            partner.vat,
            partner.state_id,
            partner.l10n_in_gst_treatment,
            pos.user_id,
            pos.company_id,
            p.product_tmpl_id,
            u.factor,
            pos.amount_total,
            pos.amount_tax,
            pos.currency_rate
        '''
        return groupby_
    
    def _query(self):
        sale_query = f"""
            {self._select_sale()}
            {self._from_sale()}
            {self._join_sale()}
            {self._where_sale()}
            {self._group_by_sale()}
        """ 
        pos_query = f"""
            {self._select_pos()}
            {self._from_pos()}
            {self._group_by_pos()}
        """
        return '%s UNION ALL %s' % (sale_query, pos_query)
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW {self._table} AS ({self._query()})""")

    def _compute_product_name_without_code(self):
        for rec in self:
            variant = rec.product_id.product_template_attribute_value_ids._get_combination_name()
            rec.product_name = variant and "%s (%s)" % (rec.product_id.name, variant) or rec.product_id.name
            if not rec.product_id:
                rec.product_name = rec.move_line_id.name
                rec.product_code = rec.move_line_id.name

    # Tax Amount
    def _compute_tax_rate(self):
        for rec in self:
            if rec.reference in ['SOP','BT']:
                rec.tax_rate = rec.sale_tax_ids.mapped('name')[0] if rec.sale_tax_ids.mapped('name') else ""
            else:
                rec.tax_rate = rec.pos_tax_ids.mapped('name')[0] if rec.pos_tax_ids.mapped('name') else ""

    def _compute_tax_details(self):
        AccountMoveLine = self.env['account.move.line'].sudo()
        # this querry to speed up process
        pos_lines = self.filtered(lambda line:line.reference in ['POS','EMPLOYEE'])
        sop_lines = self - pos_lines
        if sop_lines:
            for line in sop_lines:
                tax_by_group = line.move_line_id.tax_amount_by_tax_group
                igst_amount = self._find_tax_amount_by_tag("IGST", tax_by_group)
                cgst_amount = self._find_tax_amount_by_tag("CGST", tax_by_group)
                sgst_amount = self._find_tax_amount_by_tag("SGST", tax_by_group)
                cess_amount = self._find_tax_amount_by_tag("CESS", tax_by_group)
                if line.move_line_id.free_product_line_id:
                    tax_by_group_free = line.move_line_id.free_product_line_id.tax_amount_by_tax_group
                    igst_amount += self._find_tax_amount_by_tag("IGST", tax_by_group_free)
                    cgst_amount += self._find_tax_amount_by_tag("CGST", tax_by_group_free)
                    sgst_amount += self._find_tax_amount_by_tag("SGST", tax_by_group_free)
                    cess_amount += self._find_tax_amount_by_tag("CESS", tax_by_group_free)
                line.igst_amount = igst_amount
                line.cgst_amount = cgst_amount
                line.sgst_amount = sgst_amount
                line.cess_amount = cess_amount
                line.price_total = line.price_subtotal + (igst_amount + cgst_amount + sgst_amount + cess_amount)
        for line in pos_lines:
            tag_wise_amount = line.pos_line_id.tax_rate_by_tax_group
            line.igst_amount = self._find_tax_amount_by_tag("IGST", tag_wise_amount)
            line.cgst_amount = self._find_tax_amount_by_tag("CGST", tag_wise_amount)
            line.sgst_amount = self._find_tax_amount_by_tag("SGST", tag_wise_amount)
            line.cess_amount = self._find_tax_amount_by_tag("CESS", tag_wise_amount)
            line.price_total = line.price_subtotal + (line.igst_amount + line.cgst_amount + line.sgst_amount + line.cess_amount)

    def _find_tax_amount_by_tag(self, tag_name, tag_wise_amount):
        return sum(re.search(tag_name, k, re.IGNORECASE) and v or 0.0 for k, v in tag_wise_amount.items())
