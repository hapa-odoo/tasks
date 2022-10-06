odoo.define('website_mega_menu_customization.CollapseMegaMenu', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var config = require('web.config');
    
    publicWidget.registry.CollapseMegaMenuWidget = publicWidget.Widget.extend({
        selector: '.s_mega_menu_multi_menus',
        events: {
            'click h4.o_default_snippet_text': '_onClick',
            'touchstart h4.o_default_snippet_text': '_onClick',
        },
        init: function () {
            this._super.apply(this, arguments);
        },
        start() {
            if (config.device.isMobile) {
                this.$('.nav').hide();
            }
        },
        _onClick(ev) {
            if (config.device.isMobile) {
                ev.stopPropagation();
                this.$('.nav').hide();
                $(ev.currentTarget).next().slideUp();
                $(ev.currentTarget).next().slideDown();
            }
        }
    });

    return publicWidget.registry.CollapseMegaMenuWidget;

});