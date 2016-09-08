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

from openerp import fields, models, api, _


class WhiteLabel(models.Model):
    _name = 'white.label'
    _description = 'White Label Brand'

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', required=True)
    logo = fields.Binary(related='partner_id.image')
    mrp_priority = fields.Selection(
        selection=[('0', 'Not urgent'),
                   ('1', 'Normal'),
                   ('2', 'Urgent'),
                   ('3', 'Very Urgent')],
        default='1'
    )
    is_white_label_shop = fields.Boolean('Is White Label')
    active = fields.Boolean()
