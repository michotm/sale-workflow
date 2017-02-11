# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields


class CrmCaseSection(models.Model):
    _inherit = "crm.case.section"

    pricelist_configuration = fields.Selection([
	('no', 'No default Value'),
	('default', 'Default Value'),
	('mandatory', 'Mandatory')])
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string="Pricelist")
    fiscal_position_configuration = fields.Selection([
	('no', 'No default Value'),
	('default', 'Default Value'),
	('mandatory', 'Mandatory')])
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position',
        string='Fiscal Position')
    partner_invoice_id = fields.Many2one(
        'res.partner',
        string='Invoice Partner')
    partner_invoice_configuration = fields.Selection([
	('no', 'No default Value'),
	('default', 'Default Value'),
	('mandatory', 'Mandatory')])
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        company_dependent=True)
