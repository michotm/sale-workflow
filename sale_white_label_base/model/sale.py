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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    white_label_id = fields.Many2one('white.label', required=True)

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        res = super(SaleOrder, self)._prepare_order_line_procurement(
            group_id=group_id)
        res['white_label_id'] = self.white_label_id.id
        return res
