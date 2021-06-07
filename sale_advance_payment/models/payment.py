# Copyright 2017 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPayment(models.Model):

    _inherit = "account.payment"

    sale_id = fields.Many2one(
        "sale.order", "Sale", readonly=True, states={"draft": [("readonly", False)]}
    )

    def action_open(self):
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.payment",
            "res_id": self.id,
            "type": "ir.actions.act_window",
            "target": "current",
        }
