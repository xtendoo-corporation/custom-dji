from odoo import _, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        for order in self:
            if not order.route_ids:
                raise ValidationError(_("Debe seleccionar una ruta"))
        return super()._action_confirm()
