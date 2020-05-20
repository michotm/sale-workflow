# -*- coding: utf-8 -*-
# Copyright (C) 2016  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    production_ids = fields.One2many('mrp.production', 'sale_order_id')

    @api.multi
    def action_view_manufacturing_order(self):
        model_data_obj = self.env['ir.model.data']
        action_obj = self.pool['ir.actions.act_window']

        action_id = model_data_obj .xmlid_to_res_id(
            'mrp.mrp_production_action')
        result = action_obj.read(self._cr, self._uid, action_id,
                                 context=self._context)
        mos = self.production_ids
        result['domain'] = [('id', 'in', mos.ids)]
        return result
