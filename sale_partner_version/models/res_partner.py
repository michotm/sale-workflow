# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _version_impacted_columns(self):
        result = super()._version_impacted_columns()
        result += [
            ("sale_order", "partner_id"),
            ("sale_order", "partner_shipping_id"),
            ("sale_order", "partner_invoice_id"),
        ]
        return result

    def _version_need(self):
        result = super()._version_need()
        sale_orders = self.env["sale.order"].search(
            [
                "|",
                "|",
                ("partner_id", "=", self.id),
                ("partner_shipping_id", "=", self.id),
                ("partner_invoice_id", "=", self.id),
            ]
        )
        return result or bool(sale_orders)
