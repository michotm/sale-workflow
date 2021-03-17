# Copyright 2018 Akretion - Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestSalePartnerVersion(SavepointCase):
    def _get_created_partners(self):
        return (
            self.env["res.partner"]
            .with_context(active_test=False)
            .search([("id", ">", self.last_partner_id)], order="id desc")
        )

    def setUp(self):
        super(TestSalePartnerVersion, self).setUp()
        self.sale = self.env.ref("sale.sale_order_1")
        self.partner = self.env.ref("base.res_partner_2")  # used on sale_order_1
        self.partner_2 = self.env.ref("base.res_partner_12")  # unused yet
        self.user = self.env.ref("base.user_demo")
        self.user.partner_id = self.partner
        self.last_partner_id = (
            self.env["res.partner"]
            .with_context(active_test=False)
            .search([], order="id desc")[0]
            .id
            or 0
        )

    def test_edit_partner_all(self):
        """
        Edit a partner anywhere
        -> If that partner is used on partner_id,
           or shipping or invoicing address
           on any sale order, version it
        -> Only sale_order table should be affected
        """
        self.partner.street = "New street"
        versioned_partner = self._get_created_partners()
        self.assertEqual(self.sale.partner_id, versioned_partner)
        self.assertEqual(self.sale.partner_invoice_id, versioned_partner)
        self.assertEqual(self.sale.partner_shipping_id, versioned_partner)
        self.assertEqual(self.user.partner_id, self.partner)

    def test_edit_partner_partner_id(self):
        """
        Same as previous test, except only partner_id should be versioned
        """
        self.sale.partner_id = self.partner_2
        self.partner_2.street = "New street"
        versioned_partner = self._get_created_partners()
        self.assertEqual(self.sale.partner_id, versioned_partner)
        self.assertEqual(self.sale.partner_invoice_id, self.partner)
        self.assertEqual(self.sale.partner_shipping_id, self.partner)

    def test_edit_partner_partner_shipping_id(self):
        """
        Same as previous test, except only partner_shipping_id should be versioned
        """
        self.sale.partner_shipping_id = self.partner_2
        self.partner_2.street = "New street"
        versioned_partner = self._get_created_partners()
        self.assertEqual(self.sale.partner_shipping_id, versioned_partner)
        self.assertEqual(self.sale.partner_id, self.partner)
        self.assertEqual(self.sale.partner_invoice_id, self.partner)

    def test_edit_partner_partner_invoice_id(self):
        """
        Same as previous test, except only partner_invoice_id should be versioned
        """
        self.sale.partner_invoice_id = self.partner_2
        self.partner_2.street = "New street"
        versioned_partner = self._get_created_partners()
        self.assertEqual(self.sale.partner_invoice_id, versioned_partner)
        self.assertEqual(self.sale.partner_id, self.partner)
        self.assertEqual(self.sale.partner_shipping_id, self.partner)
