# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    advance_paid = fields.Monetary(
        "Advance paid",
        compute="_compute_advance_paid",
        currency_field="currency_id",
    )

    @api.depends(
        "account_payment_ids",
        "account_payment_ids.state",
        "account_payment_ids.amount",
        "account_payment_ids.is_advance",
    )
    def _compute_advance_paid(self):
        for rec in self:
            adv_pay_ids = rec.account_payment_ids.filtered(
                lambda p: p.is_advance and p.state == "posted"
            )
            rec.advance_paid = sum(adv_pay_ids.mapped("amount"))

    def _prepare_payment_vals(self, date, amount, is_advance):
        self.ensure_one()
        pay_mode_id = self.payment_mode_id
        return {
            "date": date,
            "amount": amount,
            "payment_type": pay_mode_id.payment_method_id.payment_type,
            "partner_type": "customer",
            "ref": self.name,
            "journal_id": pay_mode_id.fixed_journal_id.id
            or pay_mode_id.variable_journal_ids[0].id,
            "currency_id": self.currency_id.id,
            "partner_id": self.partner_id.id,
            "payment_method_id": pay_mode_id.payment_method_id.id,
            "sale_id": self.id,
            "is_advance": is_advance,
        }

    def _get_order_schedule(self):
        """A list of tuplets <scheduled_date, price_total, price_paid> for each line.
        We assume scheduled_date is related to a future invoice's date."""
        self.ensure_one()
        line_by_date_ids = self.env["sale.order.line"].search(
            [("id", "in", self.order_line.ids)], order="scheduled_date"
        )
        return [
            (l.scheduled_date, l.price_total, l.price_paid_no_adv)
            for l in line_by_date_ids
        ]

    def schedule_payments(self):
        for rec in self:
            pay_term_id = rec.payment_term_id
            order_schedule = rec._get_order_schedule()
            msg = _("Impossible to schedule payments.\n")
            if not rec.payment_term_id:
                raise ValidationError(msg + _("Payment terms are required."))
            if not rec.payment_mode_id:
                raise ValidationError(msg + _("A payment mode is required."))

            # Use sale_advance_payment's '_cancel_unlink_unposted_payments'
            rec._cancel_unlink_unposted_payments()
            # Create payments
            to_compute = rec.payment_term_id.compute_schedule(
                rec.amount_total,
                rec.advance_paid,
                order_schedule,
                rec.currency_id,
                date_order=rec.date_order,
            )
            payment_vals = []
            for date, amount, is_advance in to_compute:
                vals = rec._prepare_payment_vals(date, amount, is_advance)
                payment_vals.append(vals)
            self.env["account.payment"].create(payment_vals)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_paid_no_adv = fields.Monetary(
        "Price paid not by Advance payment",
        compute="_compute_price_paid",
        currency_field="currency_id",
    )

    @api.depends(
        "invoice_lines.move_id.state",
        "invoice_lines.move_id.line_ids.matched_debit_ids",
    )
    def _compute_price_paid(self):
        for rec in self:
            line_ids = rec.invoice_lines.move_id.line_ids
            debit_ids = line_ids.matched_debit_ids.filtered(
                lambda md: not md.debit_move_id.move_id.payment_id.is_advance
            )
            total_paid_no_adv = sum(debit_ids.mapped("amount"))
            total_inv = rec.invoice_lines.move_id.amount_total

            rec.price_paid_no_adv = (
                total_paid_no_adv * (rec.price_total / total_inv) if total_inv else 0
            )
