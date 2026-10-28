from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Mismos nombres que en 13: los adjuntos ya guardados (res_field =
    # 'digital_signature') se leen sin tocarlos.
    digital_signature = fields.Binary(string="Digital Signature", attachment=True)
    vat_receiver = fields.Char("Vat receiver", help="This is the Vat receiver")
    name_receiver = fields.Char("Name receiver", help="This is the Name receiver")
