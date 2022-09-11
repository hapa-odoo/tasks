odoo.define('point_of_sale.ExtraOrderReceiptPrint', function (require) {
    'use strict';

    var rpc = require('web.rpc');

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class ExtraOrderReceiptPrint extends PosComponent {

        async willStart() {
            this.ExtraOrdername = await this.getExtraorderDetails();
        }

        getExtraorderDetails() {
            const currentPOSOrder = this.env.pos.get_order();
            const ExtraOrder = this.rpc({
                model: 'pos.extra.order',
                method: 'search_read',
                fields: ['name'],
                domain: [['pos_parent_id', '=', this.props.ExtraOrder.pos_parent_id]],
                limit: 1,
            });
            return ExtraOrder
        }

        get extraOrder() {
            if (!this.props.ExtraOrder.name) {
                this.props.ExtraOrder.name = this.ExtraOrdername[0].name
            }
            return this.props.ExtraOrder;
        }
    }

    ExtraOrderReceiptPrint.template = 'ExtraOrderReceiptPrint';
    Registries.Component.add(ExtraOrderReceiptPrint);

    return ExtraOrderReceiptPrint;
});
