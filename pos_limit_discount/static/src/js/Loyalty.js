odoo.define('pos_limit_discount.pos_loyalty', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
    var utils = require('web.utils');

    var round_pr = utils.round_precision;

    models.load_fields('loyalty.reward', 'discount_product_id');

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function () {
            _super_orderline.initialize.apply(this, arguments);
            this.is_reduced = false;
            this.global_discount_pc = 0;
        },
        set_global_discount_pc : function(pc){
            this.global_discount_pc = pc;
            this.trigger('change', this);
        },
        set_is_reduced : function (is_reduce) {
            this.is_reduced = is_reduce;
            this.trigger('change', this);
        },
        get_global_discount_pc : function() {
            return this.global_discount_pc;
        },
        export_as_JSON: function(){
            var json = _super_orderline.export_as_JSON.apply(this,arguments);
            json.is_reduced = this.is_reduced;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.is_reduced = json.is_reduced;
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function () {
            _super_order.initialize.apply(this, arguments);
            this.points_to_reduce = 0.0;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.points_to_reduce = json.points_to_reduce;
        },
        set_points_to_reduce: function (points) {
            this.points_to_reduce = round_pr(points, 1);
            this.trigger('change', this);
        },
        get_points_to_reduce: function () {
            return this.points_to_reduce;
        },
        get_won_points: function () {
            var points_won = _super_order.get_won_points.apply(this, arguments);
            return (points_won - this.get_points_to_reduce());
        },
        export_as_JSON: function(){
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.points_to_reduce = this.points_to_reduce;
            return json;
        },
    });

});
