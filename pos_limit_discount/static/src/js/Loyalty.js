odoo.define('pos_limit_discount.pos_loyalty', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
    var utils = require('web.utils');

    var round_pr = utils.round_precision;

    models.load_fields('loyalty.reward', 'discount_product_id');

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        get_reward_by_reward_id: function (reward_id) {
            var rewards = this.pos.loyalty.rewards;
            const reward_line = rewards.filter((reward) => {
                return reward.id == reward_id;
            })
            return reward_line;
        }
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function () {
            _super_order.initialize.apply(this, arguments);
            this.is_reduced = false;
            this.points_to_reduce = 0.0;
        },
        set_points_to_reduce: function (points) {
            this.points_to_reduce = round_pr(points, 1);
            this.is_reduced = true;
            this.trigger('change', this);
        },
        get_points_to_reduce: function () {
            return this.points_to_reduce;
        },
        get_won_points: function () {
            if (this.is_reduced) {
                var points_won = _super_order.get_won_points.apply(this, arguments);
                return (points_won - this.get_points_to_reduce());
            }
            return _super_order.get_won_points.apply(this, arguments);
        },
    });

});
