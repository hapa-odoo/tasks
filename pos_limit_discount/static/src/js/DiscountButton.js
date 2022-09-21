odoo.define('pos_limit_discount.DiscountButton', function (require) {
    'use strict';

    const DiscountButton = require('pos_discount.DiscountButton');
    const Registries = require('point_of_sale.Registries');

    const PosLimitDiscountDiscountButton = (DiscountButton) =>
        class extends DiscountButton {
            constructor() {
                super(...arguments);
            }
            async apply_discount(pc) {
                super.apply_discount(pc);
                var order    = this.env.pos.get_order();
                var lines    = order.get_orderlines();
                var discount_product_id = this.env.pos.config.discount_product_id[0];
                var discount_line = lines.filter((line) =>{
                    return line.product.id == discount_product_id;
                });
                var global_discount_amount = Math.abs(discount_line[0].get_price_with_tax_before_discount());
                var product_to_skip_ids = this.env.pos.config.product_to_skip_ids;
                var lines_to_distribute = lines.filter((line) =>{
                    return line.get_product().id != discount_product_id && (!(product_to_skip_ids.includes(line.get_product().id)));
                });
                for (var line of lines_to_distribute){
                    var global_line_discount = global_discount_amount / lines_to_distribute.length;
                    line.set_global_discount_for_line(global_line_discount);
                    var global_discount_pc = ((global_discount_amount / line.get_price_with_tax_before_discount()*100));
                    line.set_global_discount_pc(global_discount_pc);
                }
            }
        };
        Registries.Component.extend(DiscountButton, PosLimitDiscountDiscountButton);
        
        return DiscountButton;
});
