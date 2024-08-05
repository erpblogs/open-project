from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.website.models import ir_http


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    # Countries now configurable
    # Country groups now get fallback pricelists when no pricelist exists for a given country
    available_countries = fields.Many2many('res.country', string='Countries domain', compute="_compute_available_countries")
    country_ids = fields.Many2many('res.country', string='Countries', 
                                   relation='product_pricelist_country_rel', column1='product_pricelist_id', column2='country_id')
    state_ids = fields.Many2many('res.country.state', string='States')
    
    
    @api.constrains('country_group_ids.country_ids', 'country_ids')
    def _check_valid_countries(self):
        for pricelist in self:
            if pricelist.country_group_ids and pricelist.country_ids and \
                any(country_id not in pricelist.country_group_ids.mapped('country_ids') for country_id in pricelist.country_ids):
                raise ValidationError(_("Country must belong to one of the country groups in the pricelist."))
            
    @api.onchange('country_ids')
    def _onchange_country_ids(self):
        if self.country_ids:
            self.state_ids = [(5,)]

    @api.constrains('state_ids')
    def _check_valid_states(self):
        for pricelist in self:
            for state in pricelist.state_ids:
                if pricelist.country_ids and state.country_id not in pricelist.country_ids:
                    raise ValidationError(_("State %s must belong to one of the countries in the pricelist.") % state.name)
            
    @api.depends('country_group_ids')
    def _compute_available_countries(self):
        for r in self:
            r.available_countries = r.country_group_ids.mapped('country_ids.id') or False
                
            
    def _get_partner_pricelist_multi(self, partner_ids, company_id=None):
        """ Retrieve the applicable pricelist for given partners in a given company.

            It will return the first found pricelist in this order:
            First, the pricelist of the specific property (res_id set), this one
                   is created when saving a pricelist on the partner form view.
            Else, it will return the pricelist of the partner country group
            Else, it will return the generic property (res_id not set), this one
                  is created on the company creation.
            Else, it will return the first available pricelist

            :param company_id: if passed, used for looking up properties,
                instead of current user's company
            :return: a dict {partner_id: pricelist}
        """
        # `partner_ids` might be ID from inactive uers. We should use active_test
        # as we will do a search() later (real case for website public user).
        Partner = self.env['res.partner'].with_context(active_test=False)
        company_id = company_id or self.env.company.id

        Property = self.env['ir.property'].with_company(company_id)
        Pricelist = self.env['product.pricelist']
        pl_domain = self._get_partner_pricelist_multi_search_domain_hook(company_id)

        # if no specific property, try to find a fitting pricelist
        result = Property._get_multi('property_product_pricelist', Partner._name, partner_ids)

        remaining_partner_ids = [pid for pid, val in result.items() if not val or
                                 not val._get_partner_pricelist_multi_filter_hook()]
        if remaining_partner_ids:
            # get fallback pricelist when no pricelist for a given country
            pl_fallback = (
                Pricelist.search(pl_domain + [('country_group_ids', '=', False)], limit=1) or
                Property._get('property_product_pricelist', 'res.partner') or
                Pricelist.search(pl_domain, limit=1)
            )
            # group partners by country, and find a pricelist for each country
            domain = [('id', 'in', remaining_partner_ids)]
            groups = Partner.read_group(domain, ['country_id'], ['country_id'])
            for group in groups:
                country_id = group['country_id'] and group['country_id'][0]
                pl = Pricelist.search(pl_domain + [('country_group_ids.country_ids', '=', country_id)], limit=1)
                pl = pl or pl_fallback
                for pid in Partner.search(group['__domain']).ids:
                    result[pid] = pl

        return result
