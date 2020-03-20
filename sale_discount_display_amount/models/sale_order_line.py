# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    discount_total = fields.Float(
        compute='_compute_discount',
        string='Discount Subtotal',
        readonly=True,
        store=True)
    price_total_no_discount = fields.Float(
        compute='_compute_discount',
        string='Subtotal Without Discount',
        readonly=True,
        store=True)

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_discount(self):
        for line in self:
            if not line.discount:
                line.price_total_no_discount = line.price_subtotal
                continue
            price = line.price_unit
            taxes = line.tax_id.compute_all(
                price,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id)
            price_total_no_discount = taxes['total_included']
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(
                price,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id)
            discount_total = price_total_no_discount - taxes['total_included']

            line.update({
                'discount_total': discount_total,
                'price_total_no_discount': price_total_no_discount
            })
