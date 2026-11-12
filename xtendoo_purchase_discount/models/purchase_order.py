# Copyright 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2015-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # En Odoo 19 el core ya gestiona el descuento de la línea (importe,
    # factura, precio del movimiento, proveedor y tarifa de proveedor). Solo
    # falta propagar al movimiento de stock pendiente un cambio de descuento,
    # porque el core únicamente lo hace cuando cambia el precio unitario.
    _discount_limit = models.Constraint(
        "CHECK (discount <= 100.0)",
        "Discount must be lower than 100%.",
    )

    def write(self, vals):
        res = super().write(vals)
        if "discount" in vals:
            for line in self.filtered(lambda pol: pol.order_id.state == "purchase"):
                moves = line.move_ids.filtered(
                    lambda move: move.state not in ("cancel", "done")
                    and move.product_id == line.product_id
                )
                moves.write({"price_unit": line._get_stock_move_price_unit()})
        return res
