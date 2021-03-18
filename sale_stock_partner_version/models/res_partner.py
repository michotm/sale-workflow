# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _version_impacted_columns(self):
        res = super(ResPartner, self)._version_impacted_tables()
        columns = [
            ('procurement_group', "partner_id"),
            ('procurement_group', "partner_address_id"),
            ('stock_picking', "owner_id"),
            ('stock_move, "')
            # quant, picking, move, rule, warehouse,
        ]
        res.extend(columns)
        return res
