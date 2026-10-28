from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = ["res.users", "mail.thread"]

    digital_signature = fields.Binary(string="Digital Signature", attachment=True)

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        for user, vals in zip(users, vals_list):
            user._track_signature(vals, "digital_signature")
        return users

    def write(self, vals):
        for user in self:
            user._track_signature(vals, "digital_signature")
        return super().write(vals)
