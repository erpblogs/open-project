{
    'name': 'Customer Price List by State',
    'version': '1.0',
    'summary': 'Automatically set price list based on customer state',
    'description': """
This is the custom module for managing products and pricelists in Odoo.
That allow setup pricelist by multiple state and get customer product pricelist by state.
""",
    'author': 'Quodoo',
    'category': 'Sales',
    'license': 'AGPL-3',
    'depends': ['base', 'product', 'sale'],
    'data': [
        'views/product_pricelist_views.xml',
    ],
    'installable': True,
    'application': False,
}
