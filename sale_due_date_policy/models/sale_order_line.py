# Copyright 2020 Akretion France
# @author: Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    due_date_reached = fields.Boolean(default=False)

    qty_delivered_method = fields.Selection(
        selection_add=[("due_date_reached", "Due Date Reached")]
    )

    def _compute_qty_delivered_method(self):
        super(SaleOrderLine, self)._compute_qty_delivered_method()
        for line in self:
            if line.product_id.invoice_policy == "due_date_reached":
                line.qty_delivered_method = "due_date_reached"

    @api.depends("due_date_reached")
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()
        lines = self.filtered(lambda sol: sol.due_date_reached)
        for line in lines:
            line.qty_delivered = line.product_uom_qty

    def _prepare_due_date_reached_domain(self):
        domain = [
            ("state", "=", "sale"),
            ("qty_delivered_method", "=", "due_date_reached"),
            ("due_date_reached", "=", False),
        ]
        if len(self):
            domain.append(["id", "in", self.ids])
        return domain

    @api.model
    def cron_due_date_reached(self):
        """Set if due date is reached for sale order lines.

        If self is an empty recordset, it will be
        calc against all sale order lines.
        Lines are filtered by
        _prepare_due_date_reached_domain()
        """
        today = fields.Date.today()

        sol = self.search(self._prepare_due_date_reached_domain())
        orders = sol.mapped("order_id").filtered(
            lambda o: o.due_date and o.due_date <= today
        )
        sol.filtered(lambda ol: ol.order_id in orders).write({"due_date_reached": True})
