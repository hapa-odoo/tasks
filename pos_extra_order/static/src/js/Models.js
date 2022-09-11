odoo.define('pos_extra_order.POSExtraOrdersModels', function (require) {

    var models = require('point_of_sale.models');
    var DB = require('point_of_sale.DB');

        models.load_models({
            model: "pos.extra.order",
            fields: ['name', 'extra_order_date', 'extra_order_status', 'pos_parent_id', 'customer_id', 'customer_mobile', 'company_id', 'note'],
            domain: function(self){ return [['session_id', 'in', self.env.pos.config.session_ids]]; },
           // domain: function(self){ return [['session_id', '=', self.pos_session.id]]; },
            loaded: function(self, extra_orders){
                self.extra_orders = extra_orders;
            },
            }, {
                'after': "pos.order"
        });

});

