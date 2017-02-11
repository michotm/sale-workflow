# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pricelist_readonly = fields.Boolean()
    partner_invoice_readonly = fields.Boolean()
    fiscal_position_readonly = fields.Boolean()

    @api.multi
    def _default_field_from_section(self):
        return ['pricelist', 'partner_invoice', 'fiscal_position']

    @api.multi
    @api.onchange('section_id', 'partner_id')
    def onchange_section_id(self):
        for record in self:
            if record.section_id:
                keys = self._default_field_from_section()
                for key in keys:
                    p_field = "%s_id" % key
                    st_field = "%s_id" % key
                    conf_field = "%s_confguration" % key
                    read_field = "%s_readonly" % key
                    if so_field == 'fiscal_position':
                        so_field = "%s" % key
                    if record.section_id[conf_field] == 'no':
                        record["readonly_field"] = False
                        continue
                    elif record.section_id[conf_field] == 'default':
                        record["readonly_field"] = False
                        if p_field == 'partner_invoice':
                            # TODO
                            record[so_field] = None
                        else:
                            record[so_field] = \
                                record[p_field] or record[st_field]
                    elif record.section_id[conf_field] == 'mandatory':
                        record[so_field] = record[st_field]
                        record["readonly_field"] = True

#    @api.multi
#    def onchange(self, values, field_name, field_onchange):
#        # TODO check this part !!! bizarre
#        # To avoid hard inheriting on partner_id we always play the section_id
#        if isinstance(field_name, list) and 'section_id' in field_name:
#            field_name.remove('section_id')
#            field_name.append('section_id')
#        # If we call an onchange on the partner_id we also call the onchange
#        # on the section_id for the compatibility
#        if field_name == 'partner_id':
#            field_name = ['partner_id', 'section_id']
#        return super(SaleOrder, self).onchange(
#            values, field_name, field_onchange)
