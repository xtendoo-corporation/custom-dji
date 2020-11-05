from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    picking_count = fields.Float(
        compute='_compute_picking_waiting_product_qty',
        string='Pickings'
    )

    def _compute_pickings_count(self):
        for picking in self:
            picking.picking_count = 0

    def _compute_picking_waiting_product_qty(self):
        for template in self:
            template.picking_count = float_round(
                sum([p.picking_count for p in template.product_variant_ids]),
                precision_rounding=template.uom_id.rounding)
