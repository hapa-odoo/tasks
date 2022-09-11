odoo.define('pos_extra_order.ExtraOrderTicketScreen', function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const { useListener } = require('web.custom_hooks');
    const { posbus } = require('point_of_sale.utils');

//    only the screen data is showed, rest of function need to be done.

    class ExtraOrderTicketScreen extends IndependentToOrderScreen {
        constructor() {
            super(...arguments);
            useListener('close-screen', this.close);
            useListener('filter-selected', this._onFilterSelected);
            useListener('search', this._onSearch);
            this.searchDetails = {};
            this.filter = null;
            this._initializeSearchFieldConstants();
            this.ExtraOrderList = this.env.pos.extra_orders;
        }
        mounted() {
            posbus.on('ticket-button-clicked', this, this.close);
            this.env.pos.get('orders').on('add remove change', () => this.render(), this);
            this.env.pos.on('change:selectedOrder', () => this.render(), this);
        }

        willUnmount() {
            posbus.off('ticket-button-clicked', this);
            this.env.pos.get('orders').off('add remove change', null, this);
            this.env.pos.off('change:selectedOrder', null, this);
        }

        _onFilterSelected(event) {
            this.filter = event.detail.filter;
            this.render();
        }

        _onSearch(event) {
            const searchDetails = event.detail;
            Object.assign(this.searchDetails, searchDetails);
            this.render();
        }

        _updateStatus(order, status) {
            this.rpc({
                model: 'pos.extra.order',
                method: 'write',
                args: [[order.id], { extra_order_status: status }],
            });
        }

        async onClickStatusComplete(order) {
            var status = 'complete';
            await this._updateStatus(order, status);
            order.extra_order_status = status;
            this.render();
        }

        async onClickStatusCancel(order) {
            var status = 'cancel';
            await this._updateStatus(order, status);
            order.extra_order_status = status;
            this.render();
        }

        get filteredOrderList() {
            if(this.env.pos.config.allow_extra_order){
                const { AllTickets, complete, cancel, New } = this.getOrderStates();
                const filterCheck = (order) => {
                    if (this.filter && this.filter !== AllTickets) {
                        return order.extra_order_status === this.filter.toLowerCase();
                    }
                    return true;
                };
                const { fieldValue, searchTerm } = this.searchDetails;
                const fieldAccessor = this._searchFields[fieldValue];
                const searchCheck = (order) => {
                    if (!fieldAccessor) return true;
                    const fieldValue = fieldAccessor(order);
                    if (fieldValue === null) return true;
                    if (!searchTerm) return true;
                    return fieldValue && fieldValue.toString().toLowerCase().includes(searchTerm.toLowerCase());
                };
                const predicate = (order) => {
                    return filterCheck(order) && searchCheck(order);
                };

            return this.ExtraOrderList.filter(predicate);
            }
        }

        async selectExtraOrder(order) {
            if (order.pos_parent_id){
                this.showScreen('ExtraOrderReceiptScreen', {
                    pos_order_id: order.pos_parent_id[0],
                    backScreen: 'ExtraOrderTicketScreen',
                    extra_order: order,
                });
            }
        }

        getDate(order) {
            return moment(order.creation_date).format('YYYY-MM-DD hh:mm A');
        }

        get searchBarConfig() {
            return {
                searchFields: this.constants.searchFieldNames,
                filter: { show: true, options: this.filterOptions },
            };
        }
        get filterOptions() {
            const { AllTickets, complete, cancel, New } = this.getOrderStates();
            return [AllTickets, complete, cancel, New];
        }

        get _searchFields() {
            if(this.env.pos.config.allow_extra_order){
                const { pos_reference, barcode, customer_id, customer_mobile, name } = this.getSearchFieldNames();
                var fields = {
                    [name]: (order) => order.name,
                    [pos_reference]: (order) =>order.pos_reference,
                    [customer_id]: (order) => order.customer_id[1],
                    [customer_mobile]: (order) => order.customer_mobile,
                   // [barcode]: (order) => order.f_barcode,
                };
                
            return fields;
            }
        }
        /**
         * Maps the order screen params to order status.
         */
        get _screenToStatusMap() {
            const { Ongoing, Payment, Receipt } = this.getOrderStates();
            return {
                ProductScreen: Ongoing,
                PaymentScreen: Payment,
                ReceiptScreen: Receipt,
            };
        }

        _initializeSearchFieldConstants() {
            this.constants = {};
            Object.assign(this.constants, {
                searchFieldNames: Object.keys(this._searchFields),
                screenToStatusMap: this._screenToStatusMap,
            });
        }

        getOrderStates() {
            return {
                AllTickets: this.env._t('All Extra Order'),
                complete: this.env._t('Complete'),
                cancel: this.env._t('Cancel'),
                New: this.env._t('New'),
            };
        }

        getSearchFieldNames() {
            if(this.env.pos.config.allow_extra_order){
                return {
                    pos_reference: this.env._t('POS Order Receipt No.'),
//                    barcode: this.env._t('Barcode'),
                    customer_id: this.env._t('Customer'),
                    customer_mobile: this.env._t('Customer Mobile'),
                    name: this.env._t('Sequence'),
                };
            }
        }
        async _onEditNote(order){
            const { confirmed, payload: inputNote } = await this.showPopup('TextAreaPopup', {
                startingValue: order.note,
                title: this.env._t('Update Extra Order Note'),
            });
            if (confirmed) {      
                this.ExtraOrderList.forEach(extra_order => {
                    if (extra_order.id === order.id){
                        extra_order.note = inputNote;
                    }
                });
                await this.rpc({
                    model: 'pos.extra.order',
                    method: 'write',
                    args: [[order.id],{ note: inputNote}],
                });
            }
        }
    }
    ExtraOrderTicketScreen.template = 'ExtraOrderTicketScreen';

    Registries.Component.add(ExtraOrderTicketScreen);

    return ExtraOrderTicketScreen;
});
