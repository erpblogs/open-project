from odoo import models, fields, api

class CustomResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            pricelist = self._get_pricelist_based_on_state(self.state_id)
            if pricelist:
                self.property_product_pricelist = pricelist

    # def _get_pricelist_based_on_state(self, state):
    #     return self.env['product.pricelist'].search([
    #         ('country_id', '=', state.country_id.id),
    #         ('state_id', '=', state.id)
    #     ], limit=1)
