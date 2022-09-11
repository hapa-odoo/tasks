# -*- coding: utf-8 -*-
{
    'name': "Website Product Filter",

    'summary': """
This module will filter the products in the ecommerce based on custom fields,
without using products Variants.
    """,

    'description': """
Task Id- 2740013 & 2882966
===========================

In Product Module:
==================

1) The following Fields will be added in product definition:
    a. Color (Many2one)
    b. Size (Many2one)
    c. eCommerce Name (Text)
    d. ecommerce identity Group (Many2one)


In eCommerce:
=============


1) The system will not display all products that are available for eCommerce, it should display one item for each identity group for example:
    a. Assume we have 3 products:
        i. Product A: identity group X
        ii. Product B: identity group X
        iii. Product C: identity group X

The system will display only one product with the eCommerce name that we defined in the product.

2) The ecommerce will show the following attributes beside the product:
    a. Size: (List of available Sizes will be the values from the products under the same identity group) and the on-hand Qty per size
    b. Color: (List of available color will be the values from the products under the same identity group) and the on-hand Qty per color

3) The images and price displayed will be the images for product of the selected size and color.

4) Once the user chooses to buy the product the id will be for the product with the same identity group, color and size.

5) This shows the details of the Product size guide.

6) When the user clicks on a product image, the pop-up window is displayed.
   This popup has product carrousel. 
   If the user clicks on the pop-up image, the image will be magnified.

7) When hovering over the Product image, the Tilde image is displayed. (User must add tilde image on Products > eCommerce > 'Product Tilde Image')

    """,

    'author': "Odoo India",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale','sale', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_country_views.xml',
        'views/product_views.xml',
        'views/product_feature_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
