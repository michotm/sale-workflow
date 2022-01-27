# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Payment Schedule",
    "description": """
        Create a payment schedule made with account.payment objects from payment_term_id in Sale Orders.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "http://akretion.com",
    "depends": [
        "account_payment_mode",
        "account_payment_sale",
        "account_payment_schedule",
        "sale_advance_payment",
        "sale_stock",
    ],
    "data": ["views/sale_order.xml", "wizard/sale_advance_payment_wizard_view.xml"],
    "demo": [],
}
