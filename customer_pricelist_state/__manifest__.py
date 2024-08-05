{
    'name': 'Customer Price List by State',
    'version': '1.0',
    'summary': 'Automatically set price list based on customer state',
    'author': 'Quodoo',
    'category': 'Sales',
    'license': 'AGPL-3',
    'depends': ['base', 'product'],
    'data': [
        'views/product_pricelist_views.xml',
    ],
    'installable': True,
    'application': False,
}
