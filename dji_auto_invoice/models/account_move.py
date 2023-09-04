from odoo import models, fields, api
import threading


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super().action_post()
        for invoice in self:
            if invoice.partner_id.email and invoice.move_type == 'out_invoice' and invoice.partner_id.auto_invoice:
                invoice.send_email()
        return res

    def send_email(self):
        print("*"*120)
        print("Entra a SEND MAIL")
        print("*"*120)
        self.ensure_one()
        template = self.env.ref('account.email_template_edi_invoice')
        email_message = template.with_context(mail_notify_force_send=True).send_mail(self.id)
        return email_message
