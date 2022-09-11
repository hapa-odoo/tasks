odoo.define('pos_extra_order.ReceiptScreen', function(require) {
    'use strict';

    var rpc = require('web.rpc');

    const Registries = require("point_of_sale.Registries");
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const { useRef } = owl.hooks;

    const PosExtraOrderReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {

            /**
             * @override
            */
            constructor(...args) {
                super(...args);
                this._extraOrderNoteRef = useRef('note');
            }
            async willStart() {
                this._currentPosOrder = await this._currentPosOrder();
                this._currentExtraOrder =  await this._currentExtraOrder();
            }

            extraOrderPrintNote() {
                //need to create new screen and map the tag below
                if (this._currentExtraOrder) {
                    this.showScreen('ExtraOrderNoteScreen', {receipt: {
                        'number': this._currentExtraOrder.name,
                        'customer': this._currentExtraOrder.customer_id && this._currentExtraOrder.customer_id[1] || '',
                        'customer_mobile': this._currentExtraOrder.customer_mobile || '',
                        'note' : this._currentExtraOrder.note,
                    }});
                }
            }

            _currentPosOrder() {
                const currentOrder = this.env.pos.get_order();
                const PosOrder = this.rpc({
                    model: 'pos.order',
                    method: 'search_read',
                    fields: ['id', 'partner_id', 'company_id'],
                    domain: [
                        ['pos_reference', '=', currentOrder.name]
                    ],
                    limit: 1,
                });
                return PosOrder
            }

            async _currentExtraOrder() {
                const currentOrder = this._currentPosOrder;
                const extraOrder = await this.rpc({
                    model: 'pos.extra.order',
                    method: 'search_read',
                    fields: ['id', 'extra_order_date', 'extra_order_status',
                    'customer_id','company_id','name','customer_mobile','note'],
                    domain: [['pos_parent_id', '=', currentOrder[0].id]],
                    limit: 1,
                });
                return extraOrder[0]
            }

            async  extraOrderPrintReceipt() {
                const currentDate = new Date();
                const PosOrder =   this._currentPosOrder;
                if ( ! _.size(this._currentExtraOrder)) {
                    const ExtraOrder = await this.rpc({
                        model: 'pos.extra.order',
                        method: 'create_extra_order_from_ui',
                        args: [{
                            'extra_order_date': currentDate,
                            'extra_order_status': 'new',
                            'customer_id': PosOrder[0].partner_id[0],
                            'company_id': PosOrder[0].company_id[0],
                            'pos_parent_id': PosOrder[0].id ,
                            'note': this._extraOrderNoteRef.el.value,
                        }],
                    });
                    this._currentExtraOrder = ExtraOrder;
                    this.env.pos.extra_orders.push(ExtraOrder);
                    this.trigger('extra-order-add');
                }
                this.showScreen('ExtraOrderReceiptScreen', {
                    pos_order_id: PosOrder[0].id, 'extra_order': this._currentExtraOrder});
            }
        };
    Registries.Component.extend(ReceiptScreen, PosExtraOrderReceiptScreen);
    return PosExtraOrderReceiptScreen;
});
