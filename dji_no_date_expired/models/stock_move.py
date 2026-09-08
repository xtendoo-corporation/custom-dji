from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _generate_serial_move_line_commands(self, field_data, location_dest_id=False, origin_move_line=None):
        move_lines_commands = super()._generate_serial_move_line_commands(
            field_data, location_dest_id, origin_move_line
        )
        for move_line_command in move_lines_commands:
            move_line_command[2]["expiration_date"] = False
        return move_lines_commands
