odoo.define('pos_limit_discount.PaymentScreen', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const utils = require('web.utils');

    const round_pr = utils.round_precision;

    const PosLimitDiscountPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            get_points_won() {
                return round_pr(this.currentOrder.get_won_points(), this.env.pos.loyalty.rounding);
            }
        }
        Registries.Component.extend(PaymentScreen, PosLimitDiscountPaymentScreen);

        return PaymentScreen;
});