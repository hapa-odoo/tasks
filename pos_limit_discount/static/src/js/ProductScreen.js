odoo.define('pos_limit_discount.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

    const PosLimitDiscountProductScreen = (ProductScreen) =>
        class extends ProductScreen {

            constructor() {
                super(...arguments);
            }

            async _onClickPay() {
                if (this.env.pos.config.limit_discount) {
                    var order = this.env.pos.get_order();
                    var order_lines = order.get_orderlines();
                    var lines_discount = order.get_total_discount();
                    var won_points = order.get_won_points();
                    var limit_discount_pc = this.env.pos.config.limit_discount_pc;
                    var loyalty = this.env.pos.loyalty;
                    var total_discount = 0.0;
                    var is_loyalty_enable = this.env.pos.config.module_pos_loyalty;
                    var is_global_discount = this.env.pos.config.module_pos_discount;
                    var other_discount = 0.0;
                    var order_total = order_lines.reduce((function (sum, orderLine) {
                        if (!orderLine.reward_id && orderLine.product.id !== discount_product_id) {
                            sum += orderLine.get_price_with_tax_before_discount();
                        }
                        return sum;
                    }), 0);
                    if (is_global_discount) {
                        var discount_product_id = this.env.pos.config.discount_product_id[0];
                        var global_discount = order_lines.reduce((function (sum, orderLine) {
                            if (!orderLine.reward_id && orderLine.product.id === discount_product_id) {
                                sum += orderLine.get_price_with_tax_before_discount();
                            }
                            return sum;
                        }), 0);
                        other_discount += Math.abs(global_discount);
                    }
                    if (is_loyalty_enable) {
                        var loyalty_product_discount = order_lines.reduce((function (sum, orderLine) {
                            if (orderLine.reward_id && orderLine.get_reward_by_reward_id(orderLine.reward_id)[0].reward_type === "discount") {
                                if (orderLine.get_reward_by_reward_id(orderLine.reward_id)[0].discount_product_id[0] === orderLine.product.id) {
                                    sum += orderLine.get_price_with_tax_before_discount();
                                }
                            }
                            return sum;
                        }), 0);
                        other_discount += Math.abs(loyalty_product_discount);
                        var loyalty_discount = (loyalty.points / 100) * won_points;
                        other_discount += loyalty_discount;
                    }
                    total_discount = other_discount + lines_discount;
                    var discount_limit = order_total * (Math.abs(limit_discount_pc) / 100);
                    if (Math.abs(total_discount) > discount_limit) {
                        var difference = Math.abs(total_discount - discount_limit);
                        console.log("\n**difference**", difference);
                        var points_to_reduce = loyalty && loyalty.points * difference;
                        if (points_to_reduce < won_points && points_to_reduce > 0.0) {
                            this.currentOrder.set_points_to_reduce(points_to_reduce);
                        } else {
                            return await this.showPopup('ErrorPopup', {
                                title: this.env._t("Max Discount Limit Exceeds"),
                                body: this.env._t("Discount Limit set on the current session is " + limit_discount_pc + "%.You need to reduce discount to complete the order"),
                            });
                        }
                    }
                }
                super._onClickPay();
            }
        };

    Registries.Component.extend(ProductScreen, PosLimitDiscountProductScreen);

    return ProductScreen;

});
