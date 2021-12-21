# Copyright (C) 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

import json

from odoo.exceptions import ValidationError, MissingError
from odoo.tests import common


class TestSaleAdvancePayment(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Partners
        cls.res_partner_1 = cls.env["res.partner"].create({"name": "Wood Corner"})

        # Products
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Desk Combination", "type": "product", "invoice_policy": "order"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Conference Chair", "type": "product", "invoice_policy": "order"}
        )
        cls.product_3 = cls.env["product.product"].create(
            {"name": "Repair Services", "type": "service", "invoice_policy": "order"}
        )

        cls.tax = cls.env["account.tax"].create(
            {"name": "Tax 15", "type_tax_use": "sale", "amount": 20}
        )
        cls.currency_euro = cls.env["res.currency"].search([("name", "=", "EUR")])
        cls.currency_usd = cls.env["res.currency"].search([("name", "=", "USD")])
        cls.currency_rate = cls.env["res.currency.rate"].create(
            {"rate": 1.20, "currency_id": cls.currency_usd.id}
        )

        # Sale Order
        cls.sale_order_1 = cls.env["sale.order"].create(
            {"partner_id": cls.res_partner_1.id}
        )
        cls.sale_order_1.write({"currency_id": cls.currency_usd.id})
        cls.order_line_1 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_1.id,
                "product_uom": cls.product_1.uom_id.id,
                "product_uom_qty": 10.0,
                "price_unit": 100.0,
                "tax_id": cls.tax,
            }
        )
        cls.order_line_2 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_2.id,
                "product_uom": cls.product_2.uom_id.id,
                "product_uom_qty": 25.0,
                "price_unit": 40.0,
                "tax_id": cls.tax,
            }
        )
        cls.order_line_3 = cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_1.id,
                "product_id": cls.product_3.id,
                "product_uom": cls.product_3.uom_id.id,
                "product_uom_qty": 20.0,
                "price_unit": 50.0,
                "tax_id": cls.tax,
            }
        )

        cls.journal_eur_bank = cls.env["account.journal"].create(
            {
                "name": "Journal Euro Bank",
                "type": "bank",
                "code": "111",
                "currency_id": cls.currency_euro.id,
            }
        )

        cls.journal_usd_bank = cls.env["account.journal"].create(
            {
                "name": "Journal USD Bank",
                "type": "bank",
                "code": "222",
                "currency_id": cls.currency_usd.id,
            }
        )
        cls.journal_eur_cash = cls.env["account.journal"].create(
            {
                "name": "Journal Euro Cash",
                "type": "cash",
                "code": "333",
                "currency_id": cls.currency_euro.id,
            }
        )

        cls.journal_usd_cash = cls.env["account.journal"].create(
            {
                "name": "Journal USD Cash",
                "type": "cash",
                "code": "444",
                "currency_id": cls.currency_usd.id,
            }
        )

    def test_unlink_payments_when_creating_invoice(self):
        order = self.sale_order_1
        context_payment = {"active_ids": [order.id], "active_id": order.id}
        advance_payment_1 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create({"journal_id": self.journal_usd_cash.id, "amount_advance": 100})
        )
        advance_payment_1.make_advance_payment()
        pay_1 = order.account_payment_ids

        order.action_confirm()
        order._create_invoices()

        with self.assertRaises(MissingError):
            pay_1.state

    def test_advance_payment_and_invoice_payment(self):
        order = self.sale_order_1
        # TODO: remove this dirty hack to pass test while main company's currency is EUR
        # (without it, the invoice's currency_id is EUR and it conflicts with order's
        # currency)
        order.write({"currency_id": self.currency_euro.id})

        order.action_confirm()
        context_payment = {"active_ids": [order.id], "active_id": order.id}
        advance_payment_1 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create({"journal_id": self.journal_eur_cash.id, "amount_advance": 100})
        )
        # Advance payment draft
        advance_payment_1.make_advance_payment()
        self.assertEqual(order.left_to_alloc, 3500)
        self.assertEqual(order.left_to_pay, 3600)
        # Advance payment posted
        pay_1 = order.account_payment_ids
        pay_1.action_post()
        self.assertEqual(order.left_to_alloc, 3500)
        self.assertEqual(order.left_to_pay, 3500)
        # Invoice draft
        order._create_invoices()
        invoice_id = order.invoice_ids[0]
        self.assertEqual(invoice_id.currency_id, self.currency_euro)
        self.assertEqual(order.left_to_alloc, 0)
        self.assertEqual(order.left_to_pay, 3500)
        # Register invoice's payment
        invoice_id.action_post()
        inv_context = {"active_ids": [invoice_id.id], "active_model": "account.move"}
        register_pay_wiz_id = (
            self.env["account.payment.register"]
            .with_context(inv_context)
            .create({"amount": 50})
        )
        register_pay_wiz_id.action_create_payments()
        self.assertEqual(order.left_to_alloc, 0)
        self.assertEqual(order.left_to_pay, 3450)

    def test_invoice_bank_payment_reconcile(self):
        order = self.sale_order_1
        order.write({"currency_id": self.currency_euro.id})
        order.action_confirm()
        # Invoice draft
        order._create_invoices()
        invoice_id = order.invoice_ids[0]
        self.assertEqual(invoice_id.currency_id, self.currency_euro)
        self.assertEqual(order.left_to_alloc, 0)
        self.assertEqual(order.left_to_pay, 3600)
        invoice_id.action_post()
        # TODO: Pay invoice through bank reconciliation
        # self.assertEqual(order.left_to_alloc, 0)
        # self.assertEqual(order.left_to_pay, 0)

    def test_sale_advance_payment(self):
        self.assertEqual(self.sale_order_1.currency_id, self.currency_usd)
        self.assertEqual(
            self.sale_order_1.left_to_alloc,
            3600,
        )
        self.assertEqual(
            self.sale_order_1.left_to_alloc,
            self.sale_order_1.amount_total,
            "Amounts should match",
        )

        context_payment = {
            "active_ids": [self.sale_order_1.id],
            "active_id": self.sale_order_1.id,
        }

        # Check residual > advance payment and the comparison takes
        # into account the currency. 3001*1.2 > 3600
        with self.assertRaises(ValidationError):
            advance_payment_0 = (
                self.env["account.voucher.wizard"]
                .with_context(context_payment)
                .create(
                    {
                        "journal_id": self.journal_eur_bank.id,
                        "amount_advance": 3001,
                        "order_id": self.sale_order_1.id,
                    }
                )
            )
            advance_payment_0.make_advance_payment()

        # Create Advance Payment 1 - EUR - bank
        advance_payment_1 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_eur_bank.id,
                    "amount_advance": 100,
                    "order_id": self.sale_order_1.id,
                }
            )
        )
        advance_payment_1.make_advance_payment()

        self.assertEqual(self.sale_order_1.left_to_alloc, 3480)

        # Create Advance Payment 2 - USD - cash
        advance_payment_2 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_cash.id,
                    "amount_advance": 200,
                    "order_id": self.sale_order_1.id,
                }
            )
        )
        advance_payment_2.make_advance_payment()

        self.assertEqual(self.sale_order_1.left_to_alloc, 3280)

        # Confirm Sale Order
        self.sale_order_1.action_confirm()

        # Create Advance Payment 3 - EUR - cash
        advance_payment_3 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_eur_cash.id,
                    "amount_advance": 250,
                    "order_id": self.sale_order_1.id,
                }
            )
        )
        advance_payment_3.make_advance_payment()
        self.assertEqual(self.sale_order_1.left_to_alloc, 2980)

        # Create Advance Payment 4 - USD - bank
        advance_payment_4 = (
            self.env["account.voucher.wizard"]
            .with_context(context_payment)
            .create(
                {
                    "journal_id": self.journal_usd_bank.id,
                    "amount_advance": 400,
                    "order_id": self.sale_order_1.id,
                }
            )
        )
        advance_payment_4.make_advance_payment()
        self.assertEqual(self.sale_order_1.left_to_alloc, 2580)

        self.sale_order_1.account_payment_ids.action_post()

        # Confirm Sale Order
        self.sale_order_1.action_confirm()

        # Create Invoice
        invoice = self.sale_order_1._create_invoices()
        invoice.action_post()

        # Compare payments
        rate = self.currency_rate.rate
        payment_list = [100 * rate, 200, 250 * rate, 400]
        payments = json.loads(invoice.invoice_outstanding_credits_debits_widget)
        result = [d["amount"] for d in payments["content"]]
        self.assertEqual(set(payment_list), set(result))
