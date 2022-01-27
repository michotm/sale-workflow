# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_scheduled = fields.Boolean(
        string="Is scheduled",
        compute="_compute_is_scheduled",
        store=True,
        help="Technical field to filter invoiced related with Orders with "
        "scheduled payments",
    )

    @api.depends(
        "move_id.line_ids.purchase_order_id.account_payment_ids",
        "move_id.line_ids.sale_line_ids.order_id.account_payment_ids",
    )
    def _compute_is_scheduled(self):
        for rec in self:
            rec.is_scheduled = bool(
                rec.move_id.line_ids.purchase_order_id.account_payment_ids
                or rec.move_id.line_ids.sale_line_ids.order_id.account_payment_ids
            )
