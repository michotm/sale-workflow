# -*- coding: utf-8 -*-
# Copyright 2020 Akretion (http://www.akretion.com)
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale due date policy",
    "summary": "Change qty delivered on a date",
    "version": "12.0.0.0.1",
    'category': 'Sales',
    "website": "https://github.com/oca/sale-workflow",
    "author": 'Akretion, Odoo Community Association (OCA)',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_management", "account"],
    "data": ["data/ir_cron.xml", "views/sale_order.xml"],
}
