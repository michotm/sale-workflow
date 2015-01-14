# -*- coding: utf-8 -*-
##############################################################################
#
#  License AGPL version 3 or later
#  See license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp import models, fields, api, exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cancel_log = fields.HTML()

    @api.one
    def _cancel_linked_record(self):
        """
        Method that cancels the pickings related to the order. It writes
        messages on the cancellation logs attribute.
        """
        for picking in self.picking_ids:
            able_to_cancel, message, important = \
                picking.can_cancel_picking_out()
            if able_to_cancel:
                picking.action_cancel()
            self.add_cancel_log(message, important=important)

    @api.multi
    def add_cancel_log(self, message, important=False):
        """
        Writes message on cancellation logs attribute of the sale order.
        If important (boolean) is True, the method will write it in red.
        """
        if not message:
            return True
        for order in self.browse(self.env.ids):
            log = order.cancel_log or ""
            if important:
                log += '<p style="color: red">%s</p>'
            else:
                log += '<p>%s</p>'
            self.cancel_log = log.message
        return True

    @api.one
    def action_cancel(self):
        self._cancel_linked_record()
        return super(SaleOrder, self).action_cancel()

    @api.one
    def copy_data(self, default=None):
        if default is None:
            default = {}
        default['cancel_log'] = False
        return super(SaleOrder, self).copy_data(default=default)
