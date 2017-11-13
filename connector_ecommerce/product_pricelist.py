# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo Connector Ecommerce Modules
#   
#    Copyright © 2016 Basement720 Technology, Inc.
#    Copyright © 2016 Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#    This file is part of Odoo Connector Ecommerce Modules and is released under
#    the BSD 3-Clause License: https://opensource.org/licenses/BSD-3-Clause
##############################################################################

from openerp import models, fields, api
from openerp.addons.connector.session import ConnectorSession
from .event import on_product_price_changed

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends()
    def _get_checkpoint(self):
        checkpoint_model = self.env['connector.checkpoint']
        model_model = self.env['ir.model']
        model = model_model.search([('model', '=', 'product.product')])
        for product in self:
            points = checkpoint_model.search([('model_id', '=', model.id),
                                              ('record_id', '=', product.id),
                                              ('state', '=', 'need_review')],
                                             limit=1,
                                             )
            product.has_checkpoint = bool(points)

    has_checkpoint = fields.Boolean(compute='_get_checkpoint',
                                    string='Has Checkpoint')

class ProductPricelistItem(models.Model):
    
    _inherit = 'product.pricelist.item'
    
    @api.multi
    def write(self, vals):
        result = super(ProductPricelistItem, self).write(vals)
        self._price_changed(vals)
        return result
        
    @api.model
    def create(self, vals):
        pricelist_item = super(ProductPricelistItem, self).create(vals)
        pricelist_item._price_changed(vals)
        return pricelist_item
        
    @api.multi
    def _price_changed(self, vals):
	session = ConnectorSession(self.env.cr, self.env.uid,
                                   context=self.env.context)
                        
        for item_id in self.ids:
            
            pricelist_item = self.browse(item_id)
            
            if pricelist_item.applied_on in ['1_product', '0_product_variant']:
            
                if pricelist_item.applied_on == '0_product_variant':
                    product = pricelist_item.product_id
                    on_product_price_changed.fire(session, product._name, product.id)
            
                if pricelist_item.applied_on == '1_product':
                    domain = [('product_tmpl_id', '=', pricelist_item.product_tmpl_id.id)]
                    product = self.env['product.product'].search(domain,limit=1)
                    on_product_price_changed.fire(session, product._name, product.id)
            
                    
