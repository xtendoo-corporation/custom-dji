from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _generate_serial_move_line_commands(self, lot_names, origin_move_line=None):
        """Override to add a default `expiration_date` into the move lines values."""
        move_lines_commands = super()._generate_serial_move_line_commands(lot_names, origin_move_line=origin_move_line)
        if self.product_id.use_expiration_date:
            date = False
            for move_line_command in move_lines_commands:
                move_line_vals = move_line_command[2]
                move_line_vals['expiration_date'] = date
        return move_lines_commands
