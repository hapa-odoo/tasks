odoo.define('pos_extra_order.ExtraOrderReceipt', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class ExtraOrderReceipt extends PosComponent {
        constructor() {
            super(...arguments);
            this.receipt = this.props.receipt;
            this.order = this.env.pos.get_order();

            const order = this.order;
            this.barcode = order.f_barcode;
            console.log(order, this.barcode, "this.barcode")
            try {
                //	 window.
                setTimeout(function () {
                    JsBarcode("#barcode", order.f_barcode, {
                        format: "EAN13",
                        displayValue: true,
                        fontSize: 50
                    });
                }, 100);
                console.log("barcococococode", $("#barcode"))
            } catch (error) {

            }
        }
    }
    ExtraOrderReceipt.template = 'ExtraOrderReceipt';

    Registries.Component.add(ExtraOrderReceipt);

    return ExtraOrderReceipt;
});

