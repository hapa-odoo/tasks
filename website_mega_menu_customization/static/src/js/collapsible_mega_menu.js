odoo.define('website_mega_menu_customization.CollapseMegaMenu', function (require) {
    "use strict";
    console.log("\n**inside**LeaveStatsWidget*LeaveStatsWidget**");
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
            this.is_exapanded = false;
        },
        start() {
            var sel = this.$(".s_mega_menu_multi_menus");
            console.log("\n #######insiide start");
            if(config.device.isMobile){
                this.$('.nav').hide();

            }
        },
        _onClick(ev){
            console.log(">>>>>>>>>>>>>>config", config,"\nev++++++ev+++ev", ev);
            console.log("\n$$$$$", config.device.isMobileDevice);
            if(config.device.isMobile){
                // alert("hiiii");
                // ev.next().find('a').hide();
                ev.stopPropagation();
                this.$('.nav').hide();
                $(ev.currentTarget).next().slideUp();
                $(ev.currentTarget).next().slideDown();
            }
        }
    });

    return publicWidget.registry.CollapseMegaMenuWidget;

});