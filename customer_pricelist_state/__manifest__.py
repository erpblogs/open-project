{
    'name': 'Customer Price List by State',
    'version': '1.0',
    'summary': 'Automatically set price list based on customer state',
    'author': 'Quodoo',
    'category': 'Sales',
    'license': 'AGPL-3',
    'depends': ['base', 'product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        # 'datas/ir_action_server.xml',
        'views/product_pricelist_views.xml',
        'views/res_country_zipcode_views.xml',
    ],
    'installable': True,
    'application': False,
}
