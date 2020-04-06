# Copyright 2020 Akretion France
# @author: Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    invoice_policy = fields.Selection(
        selection_add=[("due_date_reached", "Due Date Reached")]
    )
