# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm

class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def _get_sale_order_parent_ids(self, cr, uid, ids, context=None):
        parent_ids = []
        for sale in self.browse(cr, uid, ids, context=context):
            parent_ids.append(sale.parent_id.id)
        return parent_ids

    def _get_child_id(self, cr, uid, ids, field_name, args, context=None):
        result = {}
        for sale_id in ids:
            child_id = self.search(cr, uid, [
                ('parent_id', '=', sale_id),
                ], context=context)
            result[sale_id] = child_id[0] if child_id else False
        return result

    _columns = {
        'parent_id': fields.many2one(
            'sale.order',
            'Original Sale Order'),
        'child_id': fields.function(_get_child_id,
            string='Child',
            type='many2one',
            relation='sale.order',
            store = {
                'sale.order': (
                    _get_sale_order_parent_ids,
                    ['parent_id'],
                    10),
                }),
    }

    def _prepare_copy_quotation(self, cr, uid, order, context=None):
        return {'parent_id': order.id}

    def copy_quotation(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            res = super(SaleOrder, self).copy_quotation(
                cr, uid, [order.id], context=context)
            vals = self._prepare_copy_quotation(cr, uid, order, context=context)
            self.write(cr, uid, res['res_id'], vals, context=context)
            if self.pool.get('register.payment') and order.payment_ids:
                payment_ids = [p.id for p in order.payment_ids]
                self.pool['account.move.line'].write(cr, uid, payment_ids, {
                    'sale_ids': [(6, 0, [res['res_id']])],
                    }, context=context)
        return res
