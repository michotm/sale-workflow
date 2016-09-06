# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp import models, fields, api, exceptions, _


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _prepare_purchase_order(self, partner):
        res = super(ProcurementOrder, self)._prepare_purchase_order(partner)
        if self.group_id:
            sales = self.env['sale.order'].search(
                [('procurement_group_id', '=', self.group_id.id)])
            if len(sales) > 1:
                raise exceptions.ValidationError(
                    _("More than 1 sale order found for this group"))
            res['sale_order_id'] = sales.id
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sale_order_id = fields.Many2one('sale.order', 'Source Sale Order')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_view_purchase_order(self):
        model_data_obj = self.env['ir.model.data']
        action_obj = self.pool['ir.actions.act_window']
        po_line_obj = self.env['purchase.order.line']

        action_id = model_data_obj .xmlid_to_res_id(
            'purchase.purchase_form_action')
        result = action_obj.read(self._cr, self._uid, action_id,
                                 context=self._context)

        lines = po_line_obj.search([('sale_order_id', 'in', self.ids)])
        result['domain'] = [('id', 'in', lines.ids)]
        return result
