odoo.define('pos_limit_discount.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');

    var round_pr = utils.round_precision;

    const PosLimitDiscountProductScreen = (ProductScreen) =>
        class extends ProductScreen {

            constructor() {
                super(...arguments);
            }

            _setValue(val) {
                super._setValue(val);
                this.currentOrder.set_points_to_reduce(0);
                if(this.currentOrder.get_selected_orderline()){
                    this.currentOrder.get_orderlines().forEach(function(line){
                        line.set_is_reduced(false);
                    });
                }
            }

            async _onClickPay() {
                var is_limit_discount = this.env.pos.config.limit_discount;
                var is_loyalty_enable = this.env.pos.config.module_pos_loyalty;
                if (is_limit_discount && is_loyalty_enable) {
                    var order = this.env.pos.get_order();
                    var order_lines = order.get_orderlines();
                    var loyalty_rules = this.env.pos.loyalty.rules;
                    var limit_discount_pc = Math.abs(this.env.pos.config.limit_discount_pc);
                    var won_points = order.get_won_points();
                    var points_to_reduce = 0.0;
                    for (var line of order_lines){
                        if (line.get_reward()) {  // Reward products are ignored
                            continue;
                        }
                        if (line.is_reduced) {
                            continue;
                        }
                        var line_discount_pc = line.get_discount() + line.get_global_discount_pc();
                        if(line_discount_pc > 0){
                            var line_points_currency = 0;
                            loyalty_rules.forEach(function(rule) {
                                var rule_points_currency = 0;
                                if(rule.valid_product_ids.find(function(product_id) {return product_id === line.get_product().id})) {
                                    rule_points_currency += rule.points_currency;
                                }
                                if(Math.abs(rule_points_currency) > Math.abs(line_points_currency)){
                                    line_points_currency = rule_points_currency;
                                }
                            });
                            if(line_discount_pc <= limit_discount_pc){
                                var discount_amount = (line_discount_pc/100) * line.get_price_with_tax_before_discount();
                                var current_line_points = line_points_currency * (line.get_price_with_tax());
                                var points_amount = current_line_points/line_points_currency;
                                var total_discount = points_amount + discount_amount ;
                                var limit_discount = (limit_discount_pc/100) * line.get_price_with_tax_before_discount();
                                if(total_discount > limit_discount){
                                    var difference_amount =  total_discount - limit_discount;
                                    var current_line_points_to_reduce = round_pr(difference_amount * line_points_currency, 1) ;
                                    if(current_line_points_to_reduce <= won_points){
                                        points_to_reduce += current_line_points_to_reduce;
                                        this.currentOrder.set_points_to_reduce(points_to_reduce);
                                    } 
                                }
                            } else {
                                return await this.showPopup('ErrorPopup', {
                                    title: this.env._t("Maximum Discount Limit Exceeds"),
                                    body: this.env._t("Discount Limit set on the current session is " + limit_discount_pc + "%. but product "+line.get_product().display_name+" exceeds the limit.You need to reduce discount to complete the order"),
                                });
                            }
                        } 
                        line.set_is_reduced(true);
                    }
                }
                super._onClickPay();
            }
        };

    Registries.Component.extend(ProductScreen, PosLimitDiscountProductScreen);

    return ProductScreen;

});
