# Copyright 2021 Akretion 2021
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    advance_percent = fields.Float("Advance Percentage")
    advance_days = fields.Integer(
        "Advance days", help="Days number after Order date to pay the advance"
    )

    def compute_schedule(
        self, value, advance_paid, order_schedule, currency, date_order=False
    ):
        """Compute schedule payments based on self's advance parameters and
        order_schedule
        :param self:                    The current account.payment.term record.
        :param order_schedule:          A list <inv_date, inv_amount, inv_paid>, based
                                        on Order's lines datas. Amount in Order's
                                        currency and ordered by invoice_date.
                                        /!\ inv_paid does not include Advance payments.
        :param currency:                The Order's currency.
        :param date_order:              The Order's date used to compute advance date.
        :return:                        A list <due_date, to_pay, is_advance>.
        """
        self.ensure_one()
        today = fields.Date.context_today(self)
        date_order = date_order or today
        inv_res = []
        result = []
        # Compute advance payment
        perc_adv = self.advance_percent / 100
        advance_total = perc_adv * value
        to_advance = currency.round(advance_total - advance_paid)
        if to_advance > 0:
            date_adv = fields.Date.from_string(date_order)
            date_adv += relativedelta(days=self.advance_days)
            result.append((date_adv, to_advance, True))

        # Schedule including advance
        order_sched_no_overpaid = []
        new_adv_total = advance_total
        new_value = value
        for inv_date, inv_amt, inv_paid in order_schedule:
            # If we paid more than what we expected with the global advance percentage,
            # we don't need to create a payment for this line anymore.
            # But as this line won't consume all its theorical advance, we should
            # increase the part reserved for the advance in the other non-paid lines.
            # To compute the new reserved advance part on each other lines, we divide
            # *between them* the rest of the advance not used in the overpaid lines.
            if inv_paid > inv_amt * (1 - perc_adv):
                # (inv_amt - inv_paid) is the advance still used in the overpaid lines
                new_adv_total -= inv_amt - inv_paid
                # new_value is used to distribute the new advance on the remaining lines
                # proportionally to the amount of each remaining line *between* the
                # remaining lines
                new_value -= inv_amt
            else:
                order_sched_no_overpaid.append((inv_date, inv_amt, inv_paid))

        order_sched_real = []
        for inv_date, inv_amt, inv_paid in order_sched_no_overpaid:
            amt = inv_amt - (new_adv_total * inv_amt / new_value) - inv_paid
            if amt > 0:
                order_sched_real.append((inv_date, amt))
            else:
                # In this case the inv_paid is greater than the newly expected
                # amount to pay, so we don't need to create a  draft payment for it.
                # TODO: is it necessarry to re-recompute the remaining lines?
                continue

        # Group payments with the same date
        schedule = defaultdict(float)
        for inv_date, inv_amt in order_sched_real:
            schedule[inv_date] += inv_amt

        # Compute each invoice date and amount as classic invoice datas
        for inv_date, inv_amt in schedule.items():
            if inv_amt:
                inv_res.extend(
                    self.compute(inv_amt, date_ref=inv_date, currency=currency)
                )
        result.extend([(r[0], r[1], False) for r in inv_res])
        # Avoid cents differencies
        # (only if amount "scheduled + paid" is lower than expected)
        schedule_amount = sum(r[1] for r in result)
        total_paid = sum(o[2] for o in order_schedule)
        dist = currency.round(value - schedule_amount - advance_paid - total_paid)
        if dist > 0:
            max_date = max(o[0] for o in order_schedule)
            last_date = result and result[-1][0] or max_date or today
            result.append((last_date, dist, False))

        return result


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    @api.constrains("days")
    def _check_days(self):
        """Allows negative days after invoice date (but not negative days of the
        current or following month)"""
        try:
            super()._check_days()
        except ValidationError as e:
            if any(
                term_line.option in ("day_following_month", "day_current_month")
                and term_line.days <= 0
                for term_line in self
            ):
                raise e
