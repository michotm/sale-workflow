# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    is_advance = fields.Boolean("Is advance")

    is_action_post_visible = fields.Boolean(
        "Is action_post visible", compute="_compute_is_action_post_visible"
    )

    @api.depends("purchase_id", "sale_id", "is_advance")
    def _compute_is_action_post_visible(self):
        for rec in self:
            if rec.purchase_id or rec.sale_id:
                rec.is_action_post_visible = rec.is_advance
            else:
                rec.is_action_post_visible = True
