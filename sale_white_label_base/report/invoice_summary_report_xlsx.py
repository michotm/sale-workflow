# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 akretion Florian da Costa (www.akretion.com).
#    All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from openerp.tools.translate import _


class AccountSummaryXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, invoices):
        sheet = workbook.add_worksheet('Total')
        bold = workbook.add_format({'bold': True})
        sheet.set_column(0, 4, 20)   # Column  A,B,C,D,E width set to 20
        header = [
            _('Order Ref'),
            _('Customer Ref'),
            _('Invoice Ref'),
            _('Total Tax Excluded'),
            _('Total Tax included')]
        col = 0
        for item in header:
            sheet.write(0, col, item, bold)
            col += 1
        row = 1
        for invoice in invoices:
            if invoice.state in ('draft', 'cancel'):
                continue
            order_ref = invoice.origin
            customer_ref = invoice.name or ''
            sheet.write(row, 0, order_ref)
            sheet.write(row, 1, customer_ref)
            sheet.write(row, 2, invoice.number)
            sheet.write(row, 3, invoice.amount_untaxed)
            sheet.write(row, 4, invoice.amount_total)
            row +=1
        sheet.write(row, 0, 'Total', bold)
        sheet.write(row, 3, '=SUM(D2:D%s)' % row, bold)
        sheet.write(row, 4, '=SUM(E2:E%s)' % row, bold)


AccountSummaryXlsx('report.account.summary.xlsx',
             'account.invoice')



