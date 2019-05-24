# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits=dp.get_precision('Product Price'),
        help="Fixed amount discount.")

    @api.onchange('discount')
    def _onchange_discount(self):
        if self.discount:
            self.discount_fixed = 0.0

    @api.onchange('discount_fixed')
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.multi
    @api.constrains('discount', 'discount_fixed')
    def _check_only_one_discount(self):
        for rec in self:
            if rec.discount and rec.discount_fixed:
                raise ValidationError(
                    _("You can only set one type of discount per line."))

    @api.model
    def _calc_line_base_price(self, line):
        res = super(SaleOrderLine, self)._calc_line_base_price(line)
        if line.discount_fixed:
            return line.price_unit - line.discount_fixed
        return res

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        res = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            line, account_id=account_id)
        res.update({
            'discount_fixed': self.discount_fixed,
        })
        return res
