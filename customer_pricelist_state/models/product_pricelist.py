from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

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
                
            
    # res.partner.property_product_pricelist field computation
    @api.model
    def _get_partner_pricelist_multi(self, partner_ids):
        """ Override 
            to enable filtering customers' price lists based on their country_id and state_id
            
            :param company_id: if passed, used for looking up properties,
                instead of current user's company
            :return: a dict {partner_id: pricelist}
        """
        # `partner_ids` might be ID from inactive users. We should use active_test
        # as we will do a search() later (real case for website public user).
        Partner = self.env['res.partner'].with_context(active_test=False)
        company_id = self.env.company.id

        Property = self.env['ir.property'].with_company(company_id)
        Pricelist = self.env['product.pricelist']
        pl_domain = self._get_partner_pricelist_multi_search_domain_hook(company_id)

        # if no specific property, try to find a fitting pricelist
        specific_properties = Property._get_multi(
            'property_product_pricelist', Partner._name,
            list(models.origin_ids(partner_ids)),  # Some NewID can be in the partner_ids
        )
        result = {}
        remaining_partner_ids = []
        for pid in partner_ids:
            if (
                specific_properties.get(pid)
                and specific_properties[pid]._get_partner_pricelist_multi_filter_hook()
            ):
                result[pid] = specific_properties[pid]
            elif (
                isinstance(pid, models.NewId) and specific_properties.get(pid.origin)
                and specific_properties[pid.origin]._get_partner_pricelist_multi_filter_hook()
            ):
                result[pid] = specific_properties[pid.origin]
            else:
                remaining_partner_ids.append(pid)

        if remaining_partner_ids:
            # get fallback pricelist when no pricelist for a given country
            pl_fallback = (
                Pricelist.search(pl_domain + [('country_group_ids', '=', False)], limit=1) or
                Property._get('property_product_pricelist', 'res.partner') or
                Pricelist.search(pl_domain, limit=1)
            )
            # group partners by country, and find a pricelist for each country
            remaining_partners = self.env['res.partner'].browse(remaining_partner_ids)
            partners_by_country = remaining_partners.grouped('country_id')
            for country, partners in partners_by_country.items():
                country_id = country.id if country else False
                country_group_domain = expression.OR([
                                         expression.AND([[('country_group_ids.country_ids', '=', country_id)], [('country_ids', '=', False)]]),
                                         [('country_ids', '=', country_id)]
                                         ])
                partners_by_state = partners.grouped('state_id')
                for state, partners_state in partners_by_state.items():
                    state_group_domain = expression.OR([[('state_ids', '=', state.id if state else False)], [('state_ids', '=', False)]])
                    pl = Pricelist.search(expression.AND([pl_domain, country_group_domain,  state_group_domain]), limit=1)
                    pl = pl or pl_fallback
                    result.update(dict.fromkeys(partners_state._ids, pl))

        return result
