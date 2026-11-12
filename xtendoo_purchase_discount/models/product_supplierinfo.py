# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2014-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    discount = fields.Float(
        compute="_compute_discount",
        store=True,
        readonly=False,
        precompute=True,
    )

    _discount_limit = models.Constraint(
        "CHECK (discount <= 100.0)",
        "Supplier discount must be lower than 100%.",
    )

    @api.depends("partner_id")
    def _compute_discount(self):
        """Apply the default supplier discount of the selected supplier"""
        for record in self:
            record.discount = record.partner_id.default_supplierinfo_discount
