# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.secondary.unit.mixin"]
    _name = "sale.order.line"

    _secondary_unit_fields = {
        "qty_field": "product_uom_qty",
        "uom_field": "product_uom",
    }

    product_uom_qty = fields.Float(
        store=True, readonly=False, compute="_compute_product_qty", copy=True
    )

    @api.depends("secondary_uom_qty", "secondary_uom_id")
    def _compute_product_qty(self):
        self._compute_helper_target_field_qty()

    def onchange_product_uom_for_secondary(self):
        self._onchange_helper_product_uom_for_secondary()

    @api.onchange("product_uom")
    def onchange_product_uom_for_secondary(self):
        if not self.secondary_uom_id:
            return
        factor = self.product_uom.factor * self.secondary_uom_id.factor
        qty = float_round(
            self.product_uom_qty / (factor or 1.0),
            precision_rounding=self.product_uom.rounding,
        )
        if (
            float_compare(
                self.secondary_uom_qty,
                qty,
                precision_rounding=self.product_uom.rounding,
            )
            != 0
        ):
            self.secondary_uom_qty = qty

    @api.onchange("product_id")
    def product_id_change(self):
        """If default purchases secondary unit set on product, put on secondary
        quantity 1 for being the default quantity. We override this method,
        that is the one that sets by default 1 on the other quantity with that
        purpose.
        """
        res = super().product_id_change()
        self.secondary_uom_id = self.product_id.sale_secondary_uom_id
        if self.secondary_uom_id:
            self.secondary_uom_qty = 1.0
        return res

    def _onchange_secondary_uom(self):
        """Only for test purpouse.
        This PR deletes this method so until the PR is merged
        https://github.com/OCA/purchase-workflow/pull/1070 we need this alias
        """
        self._onchange_helper_product_uom_for_secondary()
