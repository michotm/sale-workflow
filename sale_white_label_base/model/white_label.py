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
from openerp import netsvc
from datetime import date
import base64


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

    @api.multi
    def create_white_label_attachment(self, service_name, invoices):
        self.ensure_one()
    

        attach_obj = self.env['ir.attachment']
        if service_name == 'account.report_invoice':
            name = _('invoices_details')
        elif service_name == 'account.summary.xlsx':
            name = _('invoices_summary')
        result, format = self.env['ir.actions.report.xml'].render_report(
            invoices.ids, service_name, data='')
        today = date.today().strftime('%Y-%m-%d')
        vals = {
            'type': 'binary',
            'datas': base64.encodestring(result),
            'res_model': 'white.label',
            'res_id': self.id,
            'name': name + '_' + today + '.' + format
        }
        attachment = attach_obj.create(vals)
        return attachment

    @api.model
    def send_invoice_email_to_white_label_shop(self):
        white_labels = self.search([('is_white_label_shop', '=', True)])
        invoice_obj = self.env['account.invoice']
        ir_data_obj = self.env['ir.model.data']
        template_obj = self.env['mail.template']
        mail_obj = self.env['mail.mail']
        for white_label in white_labels:
            invoices = invoice_obj.search(
                    [
                     ('white_label_id', '=', white_label.id),
                     ('white_label_mail_sent', '!=', True),
                     ('state', 'not in', ('draft', 'cancel')),
                    ])
            if not invoices:
                continue
            detail_attach = white_label.create_white_label_attachment(
                    'account.report_invoice', invoices)
            summary_attach = white_label.create_white_label_attachment(
                    'account.summary.xlsx', invoices)
            template_id = ir_data_obj.xmlid_to_res_id(
                'sale_white_label_base.sale_shop_white_label_email_template')
            values = template_obj.browse(template_id).generate_email(
                white_label.id)
            values['attachment_ids'] = [
                (6, 0, [detail_attach.id, summary_attach.id])
            ]
            mail = mail_obj.create(values)
            invoices.write({'white_label_mail_sent': True})
        return True
