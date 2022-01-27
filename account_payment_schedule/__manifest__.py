# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Payment Schedule",
    "description": """
        Common base for purchase_payment_schedule and sale_payment_schedule""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "http://akretion.com",
    "depends": [
        "account",
        "account_reconciliation_widget", # https://github.com/OCA/account-reconcile
        "purchase_advance_payment",
        "sale_advance_payment",
    ],
    "data": [
        # Views
        "views/account_payment_views.xml",
        "views/account_payment_term_views.xml",
    ],
    "demo": [],
}
