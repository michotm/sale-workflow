# Copyright 2020 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def action_invoice_create(self):
        invoice_ids = self.mapped("order_id").action_invoice_create(
            grouped=False, final=False
        )
        self.env["account.invoice.line"].search(
            [
                ("invoice_id", "in", invoice_ids),
                ("sale_line_ids", "not in", self.ids),
            ]
        ).unlink()
        return {
            "type": "ir.actions.act_window",
            "name": _("Invoices"),
            "views": [
                [False, "tree"],
                [self.env.ref("sale.account_invoice_form").id, "form"],
            ],
            "res_model": "account.invoice",
            "domain": [("id", "in", invoice_ids)],
        }
