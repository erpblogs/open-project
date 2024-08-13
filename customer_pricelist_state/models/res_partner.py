# -*- coding: utf-8 -*-

from odoo import api, fields, models


class APLSResPartner(models.Model):
    _inherit = 'res.partner'


    # Automating Price List Assignment Based on Customer State
    @api.onchange('state_id')
    def onchage_state_pricelist(self):
        res = self.env['product.pricelist']._get_partner_pricelist_multi(self._ids)
        for partner in self:
            partner.property_product_pricelist = res.get(partner.id)