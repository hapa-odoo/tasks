odoo.define('website_product_filter.cart', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var session = require('web.session');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    publicWidget.registry.WebsiteSale.include({
        xmlDependencies: ['/website_product_filter/static/src/xml/website_sale_modals.xml'],
        events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events, {
            'change input[name="size_id"]': '_change_product_size',
            'change input[name="color_id"]': '_change_product_color',

            'click #size_guide_button': '_onClick_size_guide_button',

            'click .toggle_product_zoom': '_click_product_detail_img',
            'click .carousel_zoom_product': '_onZoomodooclick',
            'mousemove .carousel_zoomMoov_product': '_onZoomodooMove',
            'mouseout .carousel_zoomMoov_product': '_onZoomMoovFocusout',
            'click .carousel_zoomMoov_product': '_click_ZoomodooMove',

            'touchstart .carousel_zoom_product': '_onZoomodootouch',    // for mobile screen
            'touchmove .carousel_zoom_product': '_onZoomodootouch',     // for mobile screen

            'mouseenter .oe_product_cart': '_onProductCardMouseenter',
            'mouseleave .oe_product_cart': '_onProductCardMouseleave',

        }),

        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            var $first_color = this.$('input[name="color_id"]').first();
            if ($first_color.length > 0){
                this._change_product_color()
            }
            return def;
        },

        /**
         * Extracted to a method to be extendable by other modules
         *
         * @param {$.Element} $parent
         */
        _getProductId: function ($parent) {
            return parseInt($parent.find('.product_id').val());
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Event} ev
         */
        _onChangeCountry: function (ev) {
            this._super.apply(this, arguments);
            this._update_zip_code();
        },

        /**
         * @private
         */
        _update_zip_code: function(){
            this._rpc({
                route: "/shop/default_zip_infos/" + $("#country_id").val(),
            }).then(function (data) {
                $("input[name='zip']").val(data.default_zip_code)
            });
        },

        /**
         * @private
         * @param {Event} ev
         */
        _change_product_size: function(ev){
            this._change_identity_product_filter();
        },

        /**
         * @private
         */
        _change_product_color: function(ev){
            this._change_identity_product_filter();
        },

        /**
         * @private
         * @param {Event} ev
         */
        _click_product_detail_img: function(ev) {
            $(document.querySelector('#modal-fullscreen-xl')).modal('toggle');
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onZoomodooclick: function(ev) {
            var img = (ev.currentTarget);
            var modalBody = $(img).closest('.modal-body');
            const x = ev.clientX - modalBody.offset()['left'];
            const y = ev.clientY - modalBody.offset()['top'];
            img.style.transformOrigin = `${x}px ${y}px`;
            img.style.transform = "scale(4)";
            img.style.cursor = 'url(/website_product_filter/static/img/zoom-in.svg), auto';
            if (window.screen.width <= 768) {
                this._onZoomodootouch(ev);
            }
            else {
                img.classList.add('carousel_zoomMoov_product');
            }
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onZoomodooMove: function(ev) {
            var img = (ev.currentTarget);
            var modalBody = $(img).closest('.modal-body');
            const x = ev.clientX - modalBody.offset()['left'];
            const y = ev.clientY - modalBody.offset()['top'];
            img.style.transformOrigin = `${x}px ${y}px`;
            img.style.transform = "scale(4)";
            img.style.cursor = 'url(/website_product_filter/static/img/zoom-in.svg), auto';
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onZoomMoovFocusout: function(ev) {
            this._click_ZoomodooMove(ev);
        },

        /**
         * @private
         * @param {Event} ev
         */
        _click_ZoomodooMove: function(ev) {
            var img = (ev.currentTarget);
            img.classList.remove('carousel_zoomMoov_product');
            img.style.transformOrigin = 'center center';
            img.style.transform = 'none';
            img.style.cursor = 'pointer';
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onZoomodootouch: function(event) {
            var touch;
            if (event.originalEvent.touches && event.originalEvent.touches[0]) {
                touch = event.originalEvent.touches[0];
            }
            else if (event.originalEvent.changedTouches && event.originalEvent.changedTouches[0]) {
                touch = event.originalEvent.changedTouches[0];
            }
            if (touch) {
                var modalBody = $(touch.target).closest('.modal-body');
                const x = touch.clientX - modalBody.offset()['left'];
                const y = touch.clientY - modalBody.offset()['top'];
                $(touch.target).css({
                    'transform-origin': `${x}px ${y}px`,
                    'cursor': 'url(/website_product_filter/static/img/zoom-in.svg), auto',
                });
                touch.target.style.setProperty('transform', 'scale(3.5)', 'important');
            }
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onZoomodooHovered: function(ev) {
            var modalWidth = $(document.querySelector('.modal-xl')).css('width');
            if ($('.zoomodoo-flyout').length > 0) {
                $('.zoomodoo-flyout').css({
                    'z-index': 1051,
                    'max-width': modalWidth,
                    'width': modalWidth,
                    'height': '520px',
                    'left': 7,
                    'right': 0,
                    'top': -99,
                });
            }
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onProductCardMouseenter: function(ev) {
            if ($(ev.currentTarget.querySelectorAll('.oe_product_image span')).length > 1) {
                setTimeout(function() {
                    $(ev.currentTarget.querySelectorAll('.oe_product_image span:first-child')).addClass('d-none').removeClass('d-flex');
                    $(ev.currentTarget.querySelectorAll('.oe_product_image span:last-child')).removeClass("d-none").addClass('d-flex');
                }, 200);
            }
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onProductCardMouseleave: function(ev) {
            if ($(ev.currentTarget.querySelectorAll('.oe_product_image span')).length > 1) {
                setTimeout(function() {
                   $(ev.currentTarget.querySelectorAll('.oe_product_image span:first-child')).removeClass("d-none").addClass('d-flex');
                   $(ev.currentTarget.querySelectorAll('.oe_product_image span:last-child')).addClass('d-none').removeClass('d-flex');
                }, 200);
            }
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onZoomodooMove: function(ev) {
            var img = (ev.currentTarget);
            var modalBody = $(img).closest('.modal-body');
            const x = ev.clientX - modalBody.offset()['left'];
            const y = ev.clientY - modalBody.offset()['top'];
            img.style.transformOrigin = `${x}px ${y}px`;
            img.style.transform = "scale(4)";
            img.style.cursor = 'url(/website_product_filter/static/img/zoom-in.svg), auto';
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onZoomMoovFocusout: function(ev) {
            this._click_ZoomodooMove(ev);
        },

        /**
         * @private
         * @param {Event} ev
         */
        _click_ZoomodooMove: function(ev) {
            var img = (ev.currentTarget);
            img.classList.remove('carousel_zoomMoov_product');
            img.style.transformOrigin = 'center center';
            img.style.transform = 'none';
            img.style.cursor = 'pointer';
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onZoomodootouch: function(event) {
            var touch;
            if (event.originalEvent.touches && event.originalEvent.touches[0]) {
                touch = event.originalEvent.touches[0];
            }
            else if (event.originalEvent.changedTouches && event.originalEvent.changedTouches[0]) {
                touch = event.originalEvent.changedTouches[0];
            }
            if (touch) {
                var modalBody = $(touch.target).closest('.modal-body');
                const x = touch.clientX - modalBody.offset()['left'];
                const y = touch.clientY - modalBody.offset()['top'];
                $(touch.target).css({
                    'transform-origin': `${x}px ${y}px`,
                    'cursor': 'url(/website_product_filter/static/img/zoom-in.svg), auto',
                });
                touch.target.style.setProperty('transform', 'scale(3.5)', 'important');
            }
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onZoomodooHovered: function(ev) {
            var modalWidth = $(document.querySelector('.modal-xl')).css('width');
            if ($('.zoomodoo-flyout').length > 0) {
                $('.zoomodoo-flyout').css({
                    'z-index': 1051,
                    'max-width': modalWidth,
                    'width': modalWidth,
                    'height': '520px',
                    'left': 7,
                    'right': 0,
                    'top': -99,
                });
            }
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onProductCardMouseenter: function(ev) {
            if ($(ev.currentTarget.querySelectorAll('.oe_product_image span')).length > 1) {
                setTimeout(function() {
                    $(ev.currentTarget.querySelectorAll('.oe_product_image span:first-child')).addClass('d-none').removeClass('d-flex');
                    $(ev.currentTarget.querySelectorAll('.oe_product_image span:last-child')).removeClass("d-none").addClass('d-flex');
                }, 200);
            }
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onProductCardMouseleave: function(ev) {
            if ($(ev.currentTarget.querySelectorAll('.oe_product_image span')).length > 1) {
                setTimeout(function() {
                   $(ev.currentTarget.querySelectorAll('.oe_product_image span:first-child')).removeClass("d-none").addClass('d-flex');
                   $(ev.currentTarget.querySelectorAll('.oe_product_image span:last-child')).addClass('d-none').removeClass('d-flex');
                }, 200);
            }
        },

        /**
         * @private
         * @param {Event} ev
         */
         _view_size_guide_category: function(SizeGuideCategory){
            this.$el.find('#product_size_guide').removeClass('d-none').modal('show');
            this.$el.find('#modal_size_guide_rec');
            if (SizeGuideCategory.length == 1) {
                var $createModal = $(QWeb.render(
                    'view_size_guide_modal',
                    { SizeGuideCategory: SizeGuideCategory }
                ));
            } else {
                var $createModal = $(QWeb.render(
                    'view_size_guide_modal_with_selected_col',
                    { SizeGuideCategory: SizeGuideCategory[0], SizeGuideColumns: SizeGuideCategory[1] }
                ));
            }
            this.$el.find('#modal_size_guide_rec').html('');
            $createModal.appendTo(this.$el.find('#modal_size_guide_rec'));
            this.$el.find('#pills-tab li:first').trigger('click');
            this.$el.find('#pills-tab li:first a').addClass('active');
         },

        /**
         * @private
         * @param {Event} ev
         */
        _onClick_size_guide_button: function(ev){
            var self = this;
            var $parent = this.$('input[name="color_id"]').closest('.js_product');
            var qty = $parent.find('input[name="add_qty"]').val();
            var productTemplateId = parseInt($parent.find('.product_template_id').val());
            if (productTemplateId) {
                ajax.jsonRpc('/website_sale/get_size_guide_info', 'call', { 'product_template_id': productTemplateId, })
                .then(function (SizeGuideCategory) {
                    self._view_size_guide_category(SizeGuideCategory);
                });
            }
        },

        /**
         * @see onChangeVariant
         *
         * @private
         * @override
         * @param {Event} ev
         * @returns {Deferred}
         */
        _getCombinationInfo: async function (ev) {
            var $parent = $(ev.target).closest('.js_product');
            if ($parent.find("input[name='identity_product']")) {
                let identity_product = $parent.find("input[name='identity_product']").val()
                if (identity_product) {
                    return await this._change_identity_product_filter();
                }
            }
            return this._super.apply(this, arguments);
        },
        _change_identity_product_filter: async function () {
            var self = this;
            var $size_id = this.$('input[name="size_id"]:checked');
            var sizeID = $size_id.val();
            var $color_id = this.$('input[name="color_id"]:checked');
            var colorID = $color_id.val();

            if (colorID > 0){
                var $parent = this.$('input[name="color_id"]').closest('.js_product');
                var qty = $parent.find('input[name="add_qty"]').val();
                var productTemplateId = parseInt($parent.find('.product_template_id').val());

                return await ajax.jsonRpc('/website_sale/get_product_identity_info', 'call', {
                    'product_template_id': productTemplateId,
                    'product_id': this._getProductId($parent),
                    'add_qty': parseInt(qty),
                    'pricelist_id': this.pricelistId || false,
                    'size_id': sizeID || 0,
                    'color_id': colorID || 0,
                }).then(function (combinationData) {
                    console.log("\n *****combinationData***combinationData****", combinationData);
                    self._onChangeCombination(false, $parent, combinationData);
                    self._disable_product_size($parent, combinationData.remaining_sizes);
                    self._show_product_qty($parent, combinationData.products_for_qty);
                });
            }
        },

        _disable_product_size: function($parent, remaining_sizes) {
            var self = this;
            $parent
            .find('input, label', '#size_li')
            .removeClass('css_not_available')
            .removeAttr('disabled');
            remaining_sizes.forEach(size => {
                var $input = $parent
                    .find('input.size_radio_input_' + size);
                /*
                * Set the On hand quantity=0 along with the Size name
                */
                var hasSpace = /\s/g.test($input.next('span').text());
                if (hasSpace) {
                    $input.next('span').replaceWith($('<span>', {
                        text: _.str.sprintf(_t('%s'), $input.next('span').text().split(' ')[0], 0),
                    }));
                } else {
                    $input.next('span').replaceWith($('<span>', {
                        text: _.str.sprintf(_t('%s'), $input.next('span').text(), 0),
                    }));
                }
                $input.addClass('css_not_available');
                $input.closest('label').addClass('css_not_available');
                $input.attr('disabled', 'disabled');
            });
        },

        /**
         * @private
         * @param {Event} ev
         * Set the On hand quantity along with the Size name
         */
        _show_product_qty: function($parent, products_for_qty) {
            var self = this;
            products_for_qty.forEach(size => {
                var $input = $parent.find('input.size_radio_input_' + size['product_tmpl_size_id']);
                
                $input.next('span').replaceWith($('<span>', {
                    text: _.str.sprintf(_t('%s'), size['product_tmpl_size_name'], size['product_tmpl_qty_available']),
                }));
                if(size['product_tmpl_qty_available'] <= 0){
                    $input.addClass('css_not_available');
                    $input.closest('label').addClass('css_not_available');
                    $input.attr('disabled', 'disabled');
                }
            });
        },

    })
});
