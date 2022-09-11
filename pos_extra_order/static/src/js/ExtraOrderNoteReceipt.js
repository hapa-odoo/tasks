odoo.define('pos_extra_order.ExtraOrderNoteReceipt', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class ExtraOrderNoteReceipt extends PosComponent {
        constructor() {
            super(...arguments);
            this.receipt = this.props.receipt;
            this.order = this.env.pos.get_order();
        }
    }
    ExtraOrderNoteReceipt.template = 'ExtraOrderNoteReceipt';

    Registries.Component.add(ExtraOrderNoteReceipt);

    return ExtraOrderNoteReceipt;
});
