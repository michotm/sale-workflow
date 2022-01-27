# Copyright (C) 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import _, api, exceptions, fields, models
from odoo.tools import float_compare


class AccountVoucherWizard(models.TransientModel):
    _inherit = "account.voucher.wizard"

    is_advance = fields.Boolean("Is advance", default=True)

    def _prepare_payment_vals(self, order_id):
        res = super()._prepare_payment_vals(order_id)
        res["is_advance"] = self.is_advance
        return res

    @api.model
    def default_get(self, fields_list):
        """Default advance journal depends on Order's payment mode"""
        res = super().default_get(fields_list)
        order_id = self.env["sale.order"].browse([res.get("order_id")])
        payment_mode_id = order_id.payment_mode_id

        if "left_to_alloc" in fields_list:
            if payment_mode_id.bank_account_link == "fixed":
                res.update({"journal_id": payment_mode_id.fixed_journal_id.id})
            elif payment_mode_id.variable_journal_ids:
                res.update({"journal_id": payment_mode_id.variable_journal_ids[0].id})

        return res
