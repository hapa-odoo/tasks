odoo.define('pos_extra_order.ExtraOrderNoteScreen', function (require) {
    'use strict';

    const { useRef } = owl.hooks;
    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const ExtraOrderNoteScreen = (AbstractReceiptScreen) => {
        class ExtraOrderNoteScreen extends AbstractReceiptScreen {
            constructor () {
                super(...arguments)
                this.receiptRef = useRef('pos-receipt');
                this.receipt = this.props.receipt;
            }
            onClickBack () {
                var order = this.env.pos.get_order();
                this.trigger('close-temp-screen');
                const { name, props } = order.get_screen_data();
                this.showScreen("ReceiptScreen", props);
            }
            tryReprint() {
                this._printReceipt();
            }
        }
        ExtraOrderNoteScreen.template = 'ExtraOrderNoteScreen';
        return ExtraOrderNoteScreen;
    };
    Registries.Component.addByExtending(ExtraOrderNoteScreen, AbstractReceiptScreen);

    return ExtraOrderNoteScreen;
});
