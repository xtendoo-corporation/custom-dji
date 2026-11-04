from odoo import _, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        """DJI asigna a mano la ruta de reparto de cada línea: no se puede
        confirmar un pedido si alguna línea de producto no tiene ruta."""
        for order in self:
            lines = order.order_line.filtered(
                lambda l: l.product_id and not l.display_type and not l.route_ids
            )
            if lines:
                raise ValidationError(
                    _(
                        "No puede confirmar el pedido %(order)s: faltan rutas en "
                        "estas líneas:\n%(lines)s",
                        order=order.name,
                        lines="\n".join("- %s" % l.product_id.display_name for l in lines),
                    )
                )
        return super()._action_confirm()
