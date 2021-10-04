# Copyright 2017 Denis Leemann, Camptocamp SA
# Copyright 2021 Iván Todorovich, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    manual_delivery = fields.Boolean(
        string="Manual Delivery",
        default=False,
        help="If enabled, the deliveries are not created at SO confirmation. "
        "You need to use the Create Delivery button in order to reserve "
        "and ship the goods.",
    )

    pending_to_deliver = fields.Boolean(compute="_compute_pending_to_deliver")

    def _compute_pending_to_deliver(self):
        for order in self:
            order.pending_to_deliver = True
            line_shippable = order.order_line.filtered(
                lambda l: l.product_id.type != "service"
            )
            if all(val is False for val in line_shippable.mapped("pending_to_deliver")):
                order.pending_to_deliver = False

    @api.onchange("team_id")
    def _onchange_team_id(self):
        self.manual_delivery = self.team_id.manual_delivery

    def action_manual_delivery_wizard(self):
        self.ensure_one()
        act_xmlid = "sale_manual_delivery.action_wizard_manual_delivery"
        action = self.env["ir.actions.actions"]._for_xml_id(act_xmlid)
        action["context"] = {
            "default_carrier_id": self.carrier_id.id,
            "default_warehouse_id": self.warehouse_id.id,
        }
        return action

    @api.constrains("manual_delivery")
    def _check_manual_delivery(self):
        if any(rec.state not in ["draft", "sent"] for rec in self):
            raise UserError(
                _(
                    "You can only change to/from manual delivery"
                    " in a quote, not a confirmed order"
                )
            )
