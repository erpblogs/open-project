from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.website.models import ir_http


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    # Countries now configurable
    # Country groups now get fallback pricelists when no pricelist exists for a given country
    country_ids = fields.Many2many('res.country', string='Countries', 
                                   relation='product_pricelist_country_rel', column1='product_pricelist_id', column2='country_id')
    state_ids = fields.Many2many('res.country.state', string='States')
    
    @api.onchange('country_ids')
    def _onchange_country_id(self):
        if self.country_ids:
            self.state_ids = [(5,)]

    @api.onchange('country_group_ids')
    def _onchange_country_group_ids(self):
        if self.country_group_ids:
            self.state_ids = [(5,)]
            self.country_ids = [(5,)]
            # Update the domain for available_state_ids based on country_ids
            if self.country_group_ids:
                return {
                    'domain': {
                        'country_ids': [('id', 'in', self.country_group_ids.mapped('country_ids')._origin.ids)]
                    }
                }

    @api.constrains('state_ids')
    def _check_states(self):
        for pricelist in self:
            for state in pricelist.state_ids:
                if pricelist.country_ids and state.country_id not in pricelist.country_ids:
                    raise ValidationError(_("State %s must belong to one of the countries in the pricelist.") % state.name)

    @api.constrains('country_group_ids.country_ids', 'country_ids')
    def _check_countries(self):
        for pricelist in self:
            if pricelist.country_group_ids and pricelist.country_ids and \
                any(country_id not in pricelist.country_group_ids.mapped('country_ids') for country_id in pricelist.country_ids):
                raise ValidationError(_("Country must belong to one of the country groups in the pricelist."))
            
    def _get_partner_pricelist_multi(self, partner_ids, company_id=None):
        """ Override 
            to enable filtering customers' price lists based on their country_id and state_id
            
            :param company_id: if passed, used for looking up properties,
                instead of current user's company
            :return: a dict {partner_id: pricelist}
        """
        # `partner_ids` might be ID from inactive uers. We should use active_test
        # as we will do a search() later (real case for website public user).
        Partner = self.env['res.partner'].with_context(active_test=False)
        website = ir_http.get_request_website()
        if not company_id and website:
            company_id = website.company_id.id
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
                country_group_domain = [('country_ids', '=', country_id)]
                for partner in Partner.search(group['__domain']):
                    # Always check customer State if customers does not setup there state. 
                    # Return the pricelist without config states
                    country_group_domain.append([('state_ids', '=', partner.state_id and partner.state_id.id)])
                        
                    pl = Pricelist.search(pl_domain + country_group_domain, limit=1)
                    
                    pl = pl or pl_fallback
                    result[partner['id']] = pl
           

        return result
    
