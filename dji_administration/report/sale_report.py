# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):

        print("commercial group ::::", self.env["res.users"].has_group("dji_administration.commercial_group"))

        if self.env["res.users"].has_group("dji_administration.commercial_group"):
            fields['margin'] = ", 0 AS margin"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
