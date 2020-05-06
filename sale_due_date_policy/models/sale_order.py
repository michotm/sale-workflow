# Copyright 2020 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    due_date_term_id = fields.Many2one("account.payment.term", string="Due Date Terms")
    due_date = fields.Date()

    @api.multi
    def action_confirm(self):
        super().action_confirm()
        for order in self:
            if order.due_date_term_id:
                pterm = order.due_date_term_id
                pterm_list = pterm.with_context(
                    currency_id=order.company_id.currency_id.id
                ).compute(value=1, date_ref=order.confirmation_date)[0]
                order.due_date = max(line[0] for line in pterm_list)
        self.mapped("order_line").cron_due_date_reached()

    def action_cancel(self):
        super().action_cancel()
        self.mapped("order_line").filtered("due_date_reached").write(
            {"due_date_reached": False}
        )

