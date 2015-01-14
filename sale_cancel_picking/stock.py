# -*- coding: utf-8 -*-
##############################################################################
#
#  License AGPL version 3 or later
#  See license in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2014 Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
#
##############################################################################

from openerp import models, api, exceptions, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def can_cancel_picking_out(self):
        """
        Method that returns if it's possible or not to cancel the picking_out
        By default we raise an error if the picking is done.
        You can override this behaviours if needed in your custom module

        :return: tuple that contain the following value
            (able_to_cancel, message, important)
        """
        able_to_cancel = False
        important = False
        message = ""

        if self.state == 'cancel':
            pass
        elif self.state == 'done':
            raise exceptions.Warning(
                _('User Error'),
                _('The Sale Order %s can not be cancelled as the picking'
                  ' %s is in the done state')
                % (self.sale_id.name, self.name))
        else:
            able_to_cancel = True
            message = _("Canceled picking out: %s") % self.name
        return able_to_cancel, message, important
