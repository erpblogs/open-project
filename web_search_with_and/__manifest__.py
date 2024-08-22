{
    "name": "Use AND conditions on omnibar search",
    'version': '1.0',
    'summary': 'Automatically set price list based on customer state',
    'author': 'Quodoo',
    'category': 'web',
    'license': 'AGPL-3',
    'depends': ['web'],
    "assets": {
        "web.assets_backend": [
            "/web_search_with_and/static/src/js/search_model.esm.js",
            "/web_search_with_and/static/src/js/search_bar.esm.js",
        ],
    },
    'installable': True,
    'application': False,
}
