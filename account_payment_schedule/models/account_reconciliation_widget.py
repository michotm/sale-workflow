# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.osv import expression


class AccountReconciliationWidget(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def _domain_move_lines_for_reconciliation(
        self,
        st_line,
        aml_accounts,
        partner_id,
        excluded_ids=None,
        search_str=False,
        mode="rp",
    ):
        """Avoid to display invoice lines related to Orders with related payments in
        the reconciliation widget"""
        domain = super()._domain_move_lines_for_reconciliation(
            st_line,
            aml_accounts,
            partner_id,
            excluded_ids,
            search_str,
            mode,
        )

        domain = expression.AND([[("is_scheduled", "=", False)], domain])
        return domain
