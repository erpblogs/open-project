from odoo import models, fields, api

from .product_pricelist import PRICE_LIST_CODE

class ResCountryStateZip(models.Model):
    _name = 'res.country.zipcode'
    _description = 'State Zip Codes'
    _order = "state_id, name"

    @api.model
    def get_pricelist_zipcode(self):
        return [(item, item) for item in PRICE_LIST_CODE]
    
    name = fields.Char(string='Zip (Postcode)', required=True, translate=False)
    state_id = fields.Many2one('res.country.state', string='State', required=True)
    country_id = fields.Many2one(related='state_id.country_id', string='Country', store=True, readonly=True)
    pricelist_code = fields.Selection('get_pricelist_zipcode', string='Pricelist Code')
    
    