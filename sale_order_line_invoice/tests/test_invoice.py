# Copyright 2020 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestInvoiceSaleOrderLines(TransactionCase):
    def setUp(self):
        """Setup 3 Sale Orders and 4 so lines.
        """
        super(TestInvoiceSaleOrderLines, self).setUp()
        customer1 = self.env.ref("base.res_partner_12")
        customer2 = self.env.ref("base.res_partner_4")
        product_id = self.env.ref("product.product_product_1")  # service
        self.sale1 = self._create_sale_order(customer1)
        self.line1 = self._create_sale_order_line(self.sale1, product_id, 2, 2)
        self.lines = self.line1
        self.lines |= self._create_sale_order_line(
            self.sale1, product_id, 4, 1
        )
        self.sale2 = self._create_sale_order(customer2)
        self.lines |= self._create_sale_order_line(
            self.sale2, product_id, 2, 2
        )
        self.sale3 = self._create_sale_order(customer2)
        self.lines |= self._create_sale_order_line(
            self.sale3, product_id, 4, 1
        )

    def _create_sale_order(self, customer):
        sale = self.env["sale.order"].create({"partner_id": customer.id,})
        return sale

    def _create_sale_order_line(self, sale, product, qty, price):
        sale_line = self.env["sale.order.line"].create(
            {
                "product_id": product.id,
                "name": "cool product",
                "order_id": sale.id,
                "price_unit": price,
                "product_uom_qty": qty,
            }
        )
        return sale_line

    def test_invoice_lines(self):
        try:
            res = self.lines.action_invoice_create()
        except UserError:
            # There is no invoiceable lines
            pass
        self.sale1.action_confirm()
        self.sale2.action_confirm()
        self.sale3.action_confirm()
        for line in self.lines:
            line.qty_delivered_manual = line.product_uom_qty
        res = self.line1.action_invoice_create()
        self.assertEquals("account.invoice", res["res_model"])
        invoices = self.lines.mapped("invoice_lines").mapped("invoice_id")
        self.assertEquals(1, len(invoices))
        self.assertEquals(4, invoices.amount_total)
        res = self.lines.action_invoice_create()
        self.assertEquals("account.invoice", res["res_model"])
        invoices = self.lines.mapped("invoice_lines").mapped("invoice_id")
        self.assertEquals(3, len(invoices))
        self.assertEquals(16, sum(invoices.mapped("amount_total")))
