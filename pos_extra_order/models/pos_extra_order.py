# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api,_
from datetime import date
from odoo.exceptions import UserError, ValidationError


class PosExtraOrder(models.Model):
    _name = 'pos.extra.order'
    _description = 'Extra Order'
   

    name = fields.Char('Extra Order Sequence')
    extra_order_date = fields.Date('Extra Order Date',default=date.today().strftime('%Y-%m-%d'))
    extra_order_status = fields.Selection([
        ('new', 'New'),
        ('complete', 'Complete'),
        ('cancel', 'Cancelled'),
    ])
    pos_parent_id = fields.Many2one('pos.order', 'POS Order Ref')
    customer_id = fields.Many2one('res.partner', 'Customer Name')
    customer_mobile = fields.Char('Customer Mobile', related='customer_id.mobile')
    company_id = fields.Many2one(
        'res.company', string='Company', related='pos_parent_id.company_id',
        store=True, readonly=True)
    session_id = fields.Many2one(related="pos_parent_id.session_id", relation='pos.session', store=True)
    note = fields.Text(string='Extra Order Note')
    
    
    def extraorder_report_print(self):
        
        datas = {'ids': self._ids,
                 'form': self.read()[0],
                
                 'model': 'pos.extra.order'}
        
        return self.env.ref('pos_extra_order.extra_order_report').report_action(self, data=datas)
    
    
            
    
    
    @api.onchange('customer_id')
    def get_pos_oder(self):
        # print("pos_order555555555555s",self.env.user.pos_config_ids.ids,self.customer_id )
        pos_domains= []
        zz=self.env['pos.order'].search([('config_id','in',self.env.user.pos_config_ids.ids),('session_id.state','=','opened')]) 
        for x in zz :
            pos_domains.append(x.id)
        domain_on_types=[('id' ,'in',pos_domains)]
                
                
        if self.customer_id :
            pos_orders = self.env['pos.order'].search([('partner_id','=',self.customer_id.id),('config_id','in',self.env.user.pos_config_ids.ids)],order='date_order desc ',limit=1)
            print("pos_orders",pos_orders.name)
            if pos_orders:
                self.pos_parent_id = pos_orders
            else:
                self.pos_parent_id = False
        
        return {'domain': {'pos_parent_id': domain_on_types}}
        
                
        

    @api.model
    def create(self, vals):
        if vals.get('pos_parent_id'):
            sequence = self.env['pos.order'].browse(vals['pos_parent_id']).session_id.config_id.extra_order_sequence_id
            vals['name'] = sequence._next()
        res = super(PosExtraOrder, self).create(vals)
        return res
    
    @api.model
    def create_extra_order_from_ui(self, values):
        extra_order = self.create(values)
        res = extra_order.read([
            'extra_order_date',
            'extra_order_status',
            'customer_id',
            'company_id',
            'name',
            'customer_mobile',
            'pos_parent_id',
            'note'])[0]
        return res
