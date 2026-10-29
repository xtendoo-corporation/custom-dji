import datetime

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def action_generate_lot_line_vals(self, context_data, mode, first_lot, count, lot_text):
        vals_list = super().action_generate_lot_line_vals(
            context_data, mode, first_lot, count, lot_text
        )
        # Quita la caducidad por defecto "hoy + vida util" que pone el core;
        # una fecha distinta (escrita por el usuario) se respeta.
        product = self.env["product.product"].browse(context_data.get("default_product_id"))
        picking = self.env["stock.picking"].browse(context_data.get("default_picking_id"))
        if product.use_expiration_date:
            from_date = picking.scheduled_date or fields.Datetime.today()
            default_date = from_date + datetime.timedelta(days=product.expiration_time)
            for vals in vals_list:
                if vals.get("expiration_date") == default_date:
                    vals["expiration_date"] = False
        return vals_list

    def _generate_serial_move_line_commands(self, field_data, location_dest_id=False, origin_move_line=None):
        move_lines_commands = super()._generate_serial_move_line_commands(
            field_data, location_dest_id, origin_move_line
        )
        for move_line_command in move_lines_commands:
            move_line_command[2]["expiration_date"] = False
        return move_lines_commands
