# -*- coding: utf-8 -*-
from odoo import models, api, _


class APLSResPartner(models.Model):
    _inherit = 'res.partner'

    # Automating Price List Assignment Based on Customer State
    @api.onchange('zip')
    def onchage_state_pricelist(self):
        # partner_id = self.id.origin if isinstance(self.id, models.NewId)  else self.id
        Pricelist = self.env['product.pricelist']
        
        if self.zip:
            zipcode_id =  self.env['res.country.zipcode'].search([('name', '=', self.zip)], limit=1)
            pls = Pricelist.search([('pricelist_code', '=', zipcode_id.pricelist_code)], limit=1)
            
            self.write({
                'country_id': zipcode_id.country_id,
                'state_id': zipcode_id.state_id,
                'property_product_pricelist': pls.id
            })
