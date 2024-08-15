from odoo import models, fields, api, _
from odoo.addons.website.models import ir_http

PRICE_LIST_CODE = [
    'NT',
    'NSW',
    'ACT',
    'VIC',
    'QLD',
    'SA',
    'WA',
    'TAS',
    'Remote',
    'Very Remote'
]



class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    @api.model
    def get_pricelist_zipcode(self):
        return [(item, item) for item in PRICE_LIST_CODE]

    pricelist_code = fields.Selection('get_pricelist_zipcode', string='Pricelist Code')