odoo.define('pos_extra_order.ExtraOrderTicketButton', function (require) {
    'use strict';

    var rpc = require('web.rpc');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { posbus } = require('point_of_sale.utils');

    class ExtraOrderTicketButton extends PosComponent {

        willPatch() {
            posbus.off('extra-order-add', this);
        }
        patched() {
            posbus.on('extra-order-add', this, this.render);
        }
        mounted() {
            posbus.on('extra-order-add', this, this.render);
        }
        willUnmount() {
            posbus.off('extra-order-add', this);
        }

        onClick() {
            this.showScreen('ExtraOrderTicketScreen');
        }

        get count() {
            return this.env.pos.extra_orders.length;
        }
    }

    ExtraOrderTicketButton.template = 'ExtraOrderTicketButton';
    Registries.Component.add(ExtraOrderTicketButton);
    return ExtraOrderTicketButton;
});
