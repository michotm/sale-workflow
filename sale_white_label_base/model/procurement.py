# -*- coding: utf-8 -*-
#########################################################################
#  Copyright (C) 2016  Akretion                                         #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU Affero General Public License as        #
# published by the Free Software Foundation, either version 3 of the    #
# License, or (at your option) any later version.                       #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
# GNU Affero General Public Licensefor more details.                    #
#                                                                       #
# You should have received a copy of the                                #
# GNU Affero General Public License                                     #
# along with this program.  If not, see <http://www.gnu.org/licenses/>. #
#                                                                       #
#########################################################################

from openerp import models, api, exceptions


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _get_white_label_from_group(self):
        self.ensure_one()
        white_label = self.env['white.label'].browse(False)
        if self.group_id:
            sales = self.env['sale.order'].search(
                [('procurement_group_id', '=', self.group_id.id)])
            if len(sales) > 1:
                raise exceptions.ValidationError(
                    _("More than 1 sale order found for this group"))
        return white_label

    @api.model
    def _prepare_mo_vals(self, procurement):
        res = super(ProcurementOrder, self)._prepare_mo_vals(procurement)
        white_label = procurement._get_white_label_from_group()
        res['white_label_id'] = white_label.id
        res['priority'] = white_label.mrp_priority
        return res

    @api.multi
    def _prepare_purchase_order(self, partner):
        res = super(ProcurementOrder, self)._prepare_purchase_order(partner)
        white_label = self._get_white_label_from_group()
        res['white_label_id'] = white_label.id
        return res
