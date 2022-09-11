odoo.define('pos_extra_order.ExtraOrderReceiptScreen', function (require) {
    'use strict';

    const { useRef } = owl.hooks;
    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const ExtraOrderReceiptScreen = (AbstractReceiptScreen) => {
        class ExtraOrderReceiptScreen extends AbstractReceiptScreen {
            constructor () {
                super(...arguments)
                this.receiptRef = useRef('pos-receipt');
                this.receipt = this.props.extra_order;
                this.pos_order_id = this.props.pos_order_id
            }

            onClickBack () {
                var order = this.env.pos.get_order();
                this.trigger('close-temp-screen');
                if (this.props.backScreen) {
                    this.showScreen(this.props.backScreen);
                } else {
                    var order = this.env.pos.get_order();
                    const { name, props } = order.get_screen_data();
                    this.showScreen("ReceiptScreen", props);
                }
            }
            tryReprint() {
                this._printReceipt();
            }
        }
        ExtraOrderReceiptScreen.template = 'ExtraOrderReceiptScreen';
        return ExtraOrderReceiptScreen;
    };
    Registries.Component.addByExtending(ExtraOrderReceiptScreen, AbstractReceiptScreen);

    return ExtraOrderReceiptScreen;
});
