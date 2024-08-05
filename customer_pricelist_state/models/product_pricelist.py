from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    country_ids = fields.Many2many('res.country', string='Countries', compute='_compute_country_ids', store=True)
    state_ids = fields.Many2many('res.country.state', string='States')
    
    @api.depends('country_group_ids')
    def _compute_country_ids(self):
        for pricelist in self:
            countries = pricelist.mapped('country_group_ids.country_ids')
            pricelist.country_ids = [(6, 0, countries.ids)]

    @api.constrains('state_ids')
    def _check_states(self):
        for pricelist in self:
            for state in pricelist.state_ids:
                if pricelist.country_ids and state.country_id not in pricelist.country_ids:
                    raise ValidationError(_("State %s must belong to one of the countries in the pricelist.") % state.name)
