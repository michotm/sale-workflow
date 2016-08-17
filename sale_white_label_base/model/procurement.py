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

from openerp import fields, models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    white_label_id = fields.Many2one('white.label', string='White Label')

    @api.model
    def _prepare_mo_vals(self, procurement):
        res = super(ProcurementOrder, self)._prepare_mo_vals(procurement)
        res['white_label_id'] = procurement.white_label_id.id
        res['priority'] = procurement.white_label_id.mrp_priority
        return res

    @api.multi
    def _prepare_purchase_order(self, partner):
        res = super(ProcurementOrder, self)._prepare_purchase_order(partner)
        res['white_label_id'] = self.white_label_id.id
        return res
