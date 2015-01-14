# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp import models, fields, api


class MrpProd(models.Model):
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one('sale.order', 'Source Sale Order')

    @api.model
    def create(self, vals):
        if self.env.context is None:
            context = {}
        if 'move_prod_id' in vals:
            move = self.env['stock.move'].browse(vals['move_prod_id'])
            if move.picking_id.sale_id:
                vals['sale_order_id'] = move.picking_id.sale_id.id
        return super(MrpProd, self).create(vals)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_view_manufacturing_order(self):
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        mrp_prod_obj = self.env['mrp.production']

        result = mod_obj.get_object_reference('mrp', 'mrp_production_action')
        id = result and result[1] or False
        result = act_obj.browse(id)[0]
        list_mo = mrp_prod_obj.search([('sale_order_id', 'in', self.ids)])
        mo_ids = []
        for mo in list_mo:
            mo_ids.append(mo.id)
        result['domain'] = "[('id', 'in', [" + \
            ','.join(map(str, mo_ids)) + "])]"
        return result
