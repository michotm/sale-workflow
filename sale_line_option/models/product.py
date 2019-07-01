# coding: utf-8
# © 2015 Akretion, Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    product_option_line_ids = fields.One2many('product.option.line',
            'parent_product_tmpl_id', 'Option Lines', copy=True)


class Product(models.Model):
    _inherit = 'product.product'
    
    product_option_line_ids = fields.One2many('product.option.line',
            'parent_product_id', 'Option Lines', copy=True)

class ProductOptionLine(models.Model):
    _name = 'product.option.line'
    _order = "sequence, name, id"
    _rec_name = "product_id"
    _description = 'Product Option Line'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    parent_product_id = fields.Many2one(
        'product.product', 'Parent Product',
        index=True, ondelete='cascade', required=True)
    parent_product_tmpl_id = fields.Many2one('product.template',
            'Parent Product Template Option',
            related='parent_product_id.product_tmpl_id', readonly=False)
    product_id = fields.Many2one(
        'product.product', 'Component Option', required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template Option',
            related='product_id.product_tmpl_id', readonly=False)
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        default=_get_default_product_uom_id, required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement"
        " for the inventory control")
    sequence = fields.Integer(
        'Sequence', default=1,
        help="Gives the sequence order when displaying.")
    name = fields.Char(compute='_compute_name', store=True, index=True)
    opt_min_qty = fields.Integer(
        string="Min Qty", default=0)
    opt_default_qty = fields.Integer(
        string="Default Qty", oldname='default_qty', default=0,
        help="This is the default quantity set to the sale line option ")
    opt_max_qty = fields.Integer(
        string="Max Qty", oldname='max_qty', default=1,
        help="High limit authorised in the sale line option")

    @api.multi
    @api.depends('product_id', 'product_tmpl_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.product_id.name

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        new_domain = self._prodopt_parent_lines_for_sale_line_option(args)
        res = super(ProductOptionLine, self).name_search(
            name=name, args=new_domain, operator=operator, limit=limit)
        return res

    def search(self, domain, offset=0, limit=None, order=None, count=False):
        new_domain = self._prodopt_parent_lines_for_sale_line_option(domain)
        return super(ProductOptionLine, self).search(
            new_domain, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def _prodopt_parent_lines_for_sale_line_option(self, domain):
        product = self.env.context.get('prodopt_parent_with_product')
        if isinstance(product, int):
            product = self.env['product.product'].browse(product)
        if product:
            new_domain = [
                '|',
                '&',
                ('parent_product_id.product_tmpl_id', '=', product.product_tmpl_id.id),
                ('parent_product_id.product_id', '=', False),
                ('parent_product_id.product_id', '=', product.id)]
            domain += new_domain
        return domain
