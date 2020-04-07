# Copyright 2020 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def action_invoice_create(self):
        invoiced_lines = self.filtered(lambda x: len(x.invoice_lines) > 0)
        if len(invoiced_lines) > 0:
            raise UserError(
                _(
                    "Some lines already belong to an invoice. You can either "
                    "cancel or validate this invoice. ({})".format(
                        invoiced_lines.mapped("invoice_id").mapped(
                            "display_name"
                        )
                    )
                )
            )
        invoice_ids = []
        # We create one invoice per partner
        for partner in self.mapped("order_partner_id"):
            records = self.filtered(lambda x: x.order_partner_id == partner)
            invoice_id = records.mapped("order_id").action_invoice_create()[0]
            self.env["account.invoice.line"].search(
                [("invoice_id", "=", invoice_id)]
            ).unlink()
            for record in records:
                record.invoice_line_create(invoice_id, record.qty_to_invoice)
            invoice_ids.append(invoice_id)
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
